"""Chaîne de diagnostic complète (section 6.1, variante D).

Fusion = mélange pondéré de trois distributions sur les pannes types :
  classifieur (0,6) + recherche dans la base (0,2) + codes OBD (0,5, si présents)
puis contraintes véhicule (carburant), réponses aux questions de précision et,
si un modèle de langage est configuré, reclassement limité aux candidats.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...config import get_settings
from ...models import DtcCode, DtcPart, Fault, PartCategory, PartReference, Product, ProductFitment, VehicleVariant
from .classifier import get_classifier
from .llm import get_llm, rerank_with_llm
from .normalize import detect_lang, extract_dtc, normalize, strip_accents
from .retrieval import DOMAIN_SOURCES, MODELS_LOCK, dense_index, domain_index, get_index
from .safety import DISCLAIMER, DO_NOT_DRIVE, TOO_SHORT, UNKNOWN, text_is_dangerous

MIX = {"clf": 0.6, "ret": 0.2, "dtc": 0.5}
MIN_SHOWN = 0.05
MIN_RETRIEVAL_SIM = 0.15  # réglé sur data/test/dev_fr_synthetique.jsonl, index des fiches de référence seulement
# Seuil du garde-fou par vecteurs (recherche hybride). Réglé sur data/test/dev_fr_synthetique.jsonl + 20 cas de démo :
# pannes >= 0,492, hors-sujet <= 0,482 ; le seuil est au milieu, marge de 0,005 de chaque côté. À revoir avec des
# textes réels, sans toucher au jeu de test d'Oran. Un refus à tort donne « je ne sais pas » : l'erreur sûre.
MIN_DOMAIN_DENSE = 0.487
MAX_QUESTIONS = 3
# Description trop courte pour trancher (« frein ») : sans code OBD et sous ce nombre de mots utiles, on pose
# d'office les questions de précision au lieu d'afficher un résultat sûr (78 % pour « frein » le 17/11/2026).
MIN_INFORMATIVE_WORDS = 2  # « frein » (1 mot) : questions ; « moteur chauffe », « ça grince quand je freine » (2) : non
# Mots qui ne disent rien de la panne : mots grammaticaux et termes trop généraux.
UNINFORMATIVE = set("""
le la les l un une des de du d a au aux et ou en sur sous dans par pour avec sans je j me m ma mon mes ta ton tes
tu il elle on nous vous ils elles ca c ce cet cette ces est sont ai as avait fait font quand qui que qu y ne n pas
plus tres trop bien mal tout toute tous encore aussi deja voiture auto automobile vehicule bagnole probleme
problemes panne pannes souci soucis truc chose marche ya il_y_a bonjour salut svp merci aide
""".split())


def informative_words(text: str) -> int:
    """Mots utiles du texte d'origine (sans accents), avant l'ajout de synonymes par la normalisation."""
    import re

    return sum(1 for w in re.findall(r"[a-z0-9]+", strip_accents(text.lower())) if len(w) > 1 and w not in UNINFORMATIVE)
# Poids de la recherche : plein poids quand le meilleur passage étiqueté atteint ce score. Les scores des deux
# modes n'ont pas la même échelle (cosinus de fragments de caractères / probabilité du reclassement) :
# un seuil par mode.
RET_FULL_SIM = {"keyword": 0.35, "hybrid": 0.35}
RET_FULL_COVERAGE = 0.5  # part des passages retrouvés qui doit appuyer une panne pour un plein poids


@dataclass
class DiagnosisInput:
    text: str
    variant_id: int | None = None
    dtc_codes: list[str] = field(default_factory=list)
    answers: dict[str, int] = field(default_factory=dict)  # id question -> indice de l'option


@lru_cache
def question_bank() -> dict[str, dict]:
    data = json.loads((Path(get_settings().data_dir) / "seed" / "faults.json").read_text(encoding="utf-8"))
    return {q["id"]: q for q in data["questions"]}


def _normalized(d: dict[str, float]) -> dict[str, float]:
    s = sum(v for v in d.values() if v > 0)
    return {k: v / s for k, v in d.items() if v > 0} if s > 0 else {}


def parts_to_faults(probs: dict[str, float], faults: dict[str, Fault], cats: dict[int, PartCategory]) -> dict[str, float]:
    """Convertit une distribution sur les familles de pièces en distribution sur les pannes types.

    score(panne) = somme sur ses pièces de poids(panne, pièce) x P(pièce)
                 + 0,5 x poids maximal de ses pièces de la famille F x P(F), pour une étiquette de niveau 1.
    Une panne dont la pièce principale est prédite reçoit donc l'essentiel de la masse.
    """
    slug_of = {c.id: c.slug for c in cats.values()}
    parent_of = {c.slug: slug_of.get(c.parent_id) for c in cats.values()}
    out: dict[str, float] = {}
    for slug, f in faults.items():
        score = 0.0
        fam_best: dict[str, float] = {}
        for fp in f.parts:
            part = slug_of.get(fp.category_id)
            score += fp.weight * probs.get(part, 0.0)
            fam = parent_of.get(part)
            if fam:
                fam_best[fam] = max(fam_best.get(fam, 0.0), fp.weight)
        score += sum(0.5 * w * probs.get(fam, 0.0) for fam, w in fam_best.items())
        if score > 0:
            out[slug] = score
    return out


def _part_view(cat: PartCategory) -> dict:
    return {"category_id": cat.id, "slug": cat.slug, "name": cat.name_fr}


def _references(db: Session, category_id: int, variant_id: int | None) -> tuple[int, list[dict]]:
    """Niveau 1 famille / 2 référence trouvée / 3 référence confirmée (section 6.7). Jamais générée."""
    if not variant_id:
        return 1, []
    confirmed = db.execute(
        select(Product.oem_ref, Product.part_brand, Product.shop_id).join(ProductFitment)
        .where(ProductFitment.variant_id == variant_id, Product.category_id == category_id,
               Product.oem_ref.is_not(None), Product.in_stock.is_(True))
    ).all()
    found = db.scalars(select(PartReference).where(
        PartReference.variant_id == variant_id, PartReference.category_id == category_id)).all()
    refs = {}
    for r in found:
        refs[r.oem_ref] = {"oem_ref": r.oem_ref, "part_brand": r.part_brand, "level": 2, "source": r.source}
    for oem, brand, shop_id in confirmed:
        refs[oem] = {"oem_ref": oem, "part_brand": brand, "level": 3, "source": "catalogue magasin", "shop_id": shop_id}
    level = max((r["level"] for r in refs.values()), default=1)
    return level, sorted(refs.values(), key=lambda r: -r["level"])


def _pick_questions(top: list[tuple[str, float]], answered: dict[str, int]) -> list[dict]:
    if len(answered) >= MAX_QUESTIONS:
        return []
    contenders = {slug for slug, _ in top[:3]}
    a, b = top[0][0], top[1][0]
    scored = []
    for q in question_bank().values():
        if q["id"] in answered:
            continue
        # pouvoir discriminant : écart des effets d'une option sur les deux premières pannes
        spread = max(abs(o["boosts"].get(a, 0) - o["boosts"].get(b, 0)) for o in q["options"])
        touch = sum(1 for o in q["options"] for s in o["boosts"] if s in contenders)
        if spread > 0:
            scored.append((spread, touch, q))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    n = min(MAX_QUESTIONS - len(answered), 2)
    return [{"id": q["id"], "text": q["text"], "options": [o["label"] for o in q["options"]]} for _, _, q in scored[:n]]


def run_diagnosis(db: Session, inp: DiagnosisInput, mode: str = "full", use_llm: bool = True) -> tuple[dict, list[int]]:
    """`use_llm=False` rend tout de suite le classement du classifieur et marque `llm: "pending"` quand un
    modèle de langage est configuré : le serveur affinera ensuite en arrière-plan (voir routers/public.py)."""
    s = get_settings()
    text = (inp.text or "").strip()
    lang = detect_lang(text)
    codes = sorted(set(c.upper() for c in inp.dtc_codes) | set(extract_dtc(text)))
    variant = db.get(VehicleVariant, inp.variant_id) if inp.variant_id else None
    vehicle_label = (
        f"{variant.model.brand.name} {variant.model.name} {variant.engine} ({variant.year_from}-{variant.year_to or ''})"
        if variant else "véhicule non précisé"
    )

    faults = {f.slug: f for f in db.scalars(select(Fault))}
    cats = {c.id: c for c in db.scalars(select(PartCategory))}

    result: dict = {
        "status": "ok", "lang": lang, "vehicle": vehicle_label, "causes": [], "questions": [], "dtc": [],
        "dtc_parts": [], "safety": {"do_not_drive": False, "message": None}, "disclaimer": DISCLAIMER,
        "message": None, "model_version": s.model_version, "mode": mode,
        "llm": "off",  # off | pending | used | cached | fallback (modèle absent, trop lent, ou réponse rejetée)
    }

    # --- Codes OBD : explication en français et pièces candidates (F3)
    dtc_cat_weight: dict[int, float] = {}
    for code in codes:
        row = db.get(DtcCode, code)
        if row is None:
            result["dtc"].append({"code": code, "known": False, "title_fr": "Code non reconnu (code constructeur ou faute de frappe ?)"})
            continue
        result["dtc"].append({"code": code, "known": True, "title_fr": row.title_fr, "causes": row.causes, "symptoms": row.symptoms})
        for dp in db.scalars(select(DtcPart).where(DtcPart.code == code)):
            dtc_cat_weight[dp.category_id] = max(dtc_cat_weight.get(dp.category_id, 0), dp.weight)
    result["dtc_parts"] = [
        {**_part_view(cats[cid]), "weight": w} for cid, w in sorted(dtc_cat_weight.items(), key=lambda x: -x[1])
    ]

    if lang != "fr":
        result.update(status="unknown", message="La première version ne comprend que le français. L'arabe et la darija arrivent ensuite.")
        return result, []

    # Index et modèles partagés entre les requêtes (reconstruits ou chargés à la demande) : un diagnostic à la
    # fois dans cette partie. Une fois les modèles chargés elle prend ~0,03 s ; le modèle de langage, lent, reste hors du verrou.
    with MODELS_LOCK:
        # --- Recherche
        search_index = get_index()
        # En mode classifieur seul, la recherche hybride (vecteurs et reclassement) serait du temps perdu.
        hits = search_index.search(db, text, k=8) if text and not (mode == "classifier" and search_index.name == "hybrid") else []
        retrieved_ids = [h.chunk_id for h in hits]
        # Appui de la recherche pour chaque panne : somme des similarités des passages étiquetés avec elle.
        # La part de cet appui dans tout ce qui a été retrouvé (couverture) dit si les passages trouvés
        # parlent vraiment de la même panne ou si un seul passage étiqueté se perd parmi d'autres.
        ret: dict[str, float] = {}
        ret_best = 0.0
        for h in hits:
            f = h.meta.get("fault")
            if f in faults:
                ret[f] = ret.get(f, 0.0) + h.score
                ret_best = max(ret_best, h.score)
        ret_coverage = sum(ret.values()) / max(sum(h.score for h in hits), 1e-9)
        # Le domaine (« est-ce une panne automobile ? ») se juge sur les fiches de référence seulement :
        # les sources externes (rappels…) contiennent trop de vocabulaire général pour servir de garde-fou.
        domain_hits = domain_index.search(db, text, k=1) if text else []
        max_sim = max((h.score for h in domain_hits), default=0.0)
        # Avec la recherche hybride, un second garde-fou : ressemblance des vecteurs avec les fiches de référence.
        dense_domain = dense_index.domain_similarity(db, text, DOMAIN_SOURCES) if search_index.name == "hybrid" else None

        # --- Classifieur
        clf: dict[str, float] = {}
        if len(normalize(text).split()) >= 2 and mode in ("full", "classifier"):
            model = get_classifier()
            probs = model.predict_proba(text)
            if getattr(model, "target", "fault") == "part":
                clf = parts_to_faults(probs, faults, cats)
            else:
                clf = {k: v for k, v in probs.items() if k in faults}

    # --- Codes OBD -> pannes
    dtc_scores: dict[str, float] = {}
    if dtc_cat_weight:
        for slug, f in faults.items():
            sc = max((fp.weight * dtc_cat_weight.get(fp.category_id, 0) for fp in f.parts), default=0)
            if sc > 0:
                dtc_scores[slug] = sc

    components = {"clf": _normalized(clf), "ret": _normalized(ret) if mode != "classifier" else {}, "dtc": _normalized(dtc_scores)}
    # Une recherche qui ne trouve qu'un passage lointain, ou un seul passage étiqueté parmi beaucoup
    # d'autres, ne doit pas peser comme une correspondance nette : le poids de la recherche suit la
    # similarité du meilleur passage étiqueté (plein poids à RET_FULL_SIM) et la couverture (à RET_FULL_COVERAGE).
    weights = dict(MIX)
    if ret:
        weights["ret"] *= min(1.0, ret_best / RET_FULL_SIM[search_index.name]) * min(1.0, ret_coverage / RET_FULL_COVERAGE)
    total_w = sum(weights[k] for k, d in components.items() if d)
    mix: dict[str, float] = {}
    for k, d in components.items():
        if d and total_w:
            for slug, p in d.items():
                mix[slug] = mix.get(slug, 0) + weights[k] / total_w * p

    # Hors sujet : pas de code OBD et texte sans rapport avec la base
    off_topic = not dtc_scores and (max_sim < MIN_RETRIEVAL_SIM or (dense_domain is not None and dense_domain < MIN_DOMAIN_DENSE))

    # --- Contraintes véhicule et réponses
    if variant:
        for slug in mix:
            fuel = faults[slug].fuel
            if fuel and fuel != variant.fuel and not (fuel == "essence" and variant.fuel in ("gpl", "hybride")):
                mix[slug] *= 0.05
    bank = question_bank()
    for qid, idx in (inp.answers or {}).items():
        q = bank.get(qid)
        if q and 0 <= idx < len(q["options"]):
            for slug, boost in q["options"][idx]["boosts"].items():
                if slug in mix:
                    mix[slug] *= math.exp(3 * boost)
                elif boost > 0:
                    mix[slug] = 0.02 * math.exp(3 * boost)
    mix = _normalized(mix)
    ranked = sorted(mix.items(), key=lambda x: -x[1])

    if off_topic or not ranked or ranked[0][1] < s.confidence_threshold:
        result.update(status="unknown", message=UNKNOWN)
        if text_is_dangerous(text):
            result["safety"] = {"do_not_drive": True, "message": DO_NOT_DRIVE}
        return result, retrieved_ids

    # --- Reclassement par modèle de langage (si configuré)
    explanations: dict[str, str] = {}
    if mode in ("full", "retrieval"):  # variantes D et C (section 6.2)
        candidates = {slug: faults[slug].name_fr for slug, _ in ranked[:6]}
        if use_llm:
            llm_rank, result["llm"] = rerank_with_llm(text, vehicle_label, [h.text for h in hits], candidates)
        else:
            llm_rank = None
            result["llm"] = "pending" if get_llm().name != "none" else "off"
        if llm_rank:
            order = [r["fault"] for r in llm_rank]
            explanations = {r["fault"]: r["explanation"] for r in llm_rank}
            ranked = sorted(ranked, key=lambda x: (order.index(x[0]) if x[0] in order else 99, -x[1]))

    for slug, conf in ranked[:3]:
        if conf < MIN_SHOWN:
            continue
        f = faults[slug]
        parts = sorted(f.parts, key=lambda fp: -fp.weight)
        main = cats[parts[0].category_id]
        level, refs = _references(db, main.id, inp.variant_id)
        result["causes"].append({
            "fault": slug, "name": f.name_fr, "system": f.system, "severity": f.severity,
            "description": f.description, "confidence": round(conf, 3),
            "part": _part_view(main), "other_parts": [_part_view(cats[fp.category_id]) for fp in parts[1:]],
            "reference_level": level, "references": refs, "explanation": explanations.get(slug),
            "do_not_drive": f.do_not_drive,
        })

    top_conf = result["causes"][0]["confidence"]
    too_short = not codes and not inp.answers and informative_words(text) < MIN_INFORMATIVE_WORDS
    if len(ranked) > 1 and (too_short or top_conf - ranked[1][1] < s.clarify_margin):
        qs = _pick_questions(ranked, inp.answers or {})
        if qs:
            result.update(status="clarify", questions=qs)
    if too_short and result["status"] != "clarify":
        # Une seule panne ressort (confiance de 100 % par construction) ou aucune question ne départage : un mot seul
        # (« bruit ») ne suffit pas, on demande une description plus précise plutôt que d'afficher un résultat sûr.
        result.update(status="unknown", message=TOO_SHORT, causes=[])
        if text_is_dangerous(text):
            result["safety"] = {"do_not_drive": True, "message": DO_NOT_DRIVE}
        return result, retrieved_ids

    danger = text_is_dangerous(text) or any(c["do_not_drive"] and c["confidence"] >= 0.2 for c in result["causes"])
    if danger:
        result["safety"] = {"do_not_drive": True, "message": DO_NOT_DRIVE}
    result["urgency"] = result["causes"][0]["severity"]
    return result, retrieved_ids
