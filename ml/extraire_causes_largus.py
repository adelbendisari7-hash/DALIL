"""Causes confirmées de L'Argus, extraites avec précision, pour servir d'exemples réels (texte du conducteur -> pièce).

    python ml/extraire_causes_largus.py            # -> data/processed/largus_causes.jsonl (hors git)
    python ml/extraire_causes_largus.py --echantillon 60 > echantillon.txt   # pour mesurer la justesse
    python ml/extraire_causes_largus.py --source techniconnexion   # même règle, forum Techniconnexion

Pourquoi : les étiquettes de pièce déduites de tout le message de l'auteur ne sont justes que dans 28 % des cas
(relecture du 24/11/2026) : l'auteur cite aussi les pièces changées pour rien. Ici, on ne garde que la pièce nommée
juste après une tournure qui affirme la cause (« c'était bien la bobine », « panne résolue en changeant le démarreur »,
« le problème venait du capteur PMH »), dans une fenêtre de quelques mots. Les cas des jeux de test privés sont exclus.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))

from pipeline.taxonomy_map import categories_fr  # noqa: E402

# source -> (enregistrements du pipeline, causes extraites, identifiants vérifiés sans texte, exemples vérifiés)
SOURCES = {
    "largus_forum": ("largus_forum.jsonl", "largus_causes.jsonl", "largus", "largus_causes_verifiees.jsonl"),
    "techniconnexion": ("techniconnexion.jsonl", "techniconnexion_causes.jsonl", "techniconnexion",
                        "techniconnexion_causes_verifiees.jsonl"),
}
PROCESSED = ROOT / "data" / "processed"
SRC = PROCESSED / "largus_forum.jsonl"
OUT = PROCESSED / "largus_causes.jsonl"
TESTS = sorted((ROOT / "data" / "test_prive").glob("*.jsonl"))

# Tournures qui affirment la cause ; la pièce doit suivre dans les WINDOW mots
CUE = re.compile(
    r"(c'?\s?[ée]tai[ts]? (bien |juste |simplement |tout simplement |finalement |en fait |effectivement )*"
    r"|(panne|probl[eè]me) (est |a [ée]t[ée] )?r[ée]solue? (en|apr[eè]s) (avoir )?(chang\w+|rempla\w+|chang[ée] de)"
    r"|(le |la |mon |ma )?(probl[eè]me|panne|souci|bruit|fuite) (venait|provenait|vient|provient) (bien |en fait )?(d[eu]'?|de la|des)"
    r"|il s'agissait (bien |en fait )?d[eu'e]"
    r"|verdict ?:? ?)", re.IGNORECASE)
WINDOW = 7
# Seconde forme (26/11/2026) : « j'ai changé la pompe et tout marche » ; la réussite doit être dite dans la même phrase
CHANGE = re.compile(r"(j'?\s?ai|on a|le garage a|il a|le m[ée]cano a|nous avons)\s+(donc |finalement |enfin |juste |simplement )*"
                    r"(chang\w*|remplac\w*|mis (un|une|des) (neuve?s?|nouveaux?|nouvelles?))\s+", re.IGNORECASE)
REUSSITE = re.compile(r"(tout )?(marche|fonctionne|refonctionne|remarche|roule)\b|plus (de |aucun )(probl|souci|bruit|panne)|"
                      r"r[ée]solu|nickel|impec|d[ée]marre (au quart|nickel|bien|maintenant|du premier)|rentr[ée] dans l'ordre",
                      re.IGNORECASE)
# Formulations absentes de la taxonomie (vérifiées le 26/11/2026)
EXTRA = [
    (r"sonde (de )?(temp\w*|d'?eau|liquide)|thermo ?contact|sonde moteur", "sonde-temperature"),
    (r"pompe (a |à )?(injection|gasoil|gazole|gas-oil|essence|de gavage|haute pression|hp)|pompe injection", "pompe-carburant"),
    (r"but[ée]e( d'?embrayage)?|disque d'?embrayage|m[ée]canisme d'?embrayage", "kit-embrayage"),
    (r"c[aâ]ble d'?embrayage", "cable-embrayage"),
    (r"capteur (de )?(pression|surpression|suralimentation)", "capteur-pression-admission"),
    (r"bo[iî]tier papillon|corps papillon|moteur pas (a|à) pas|vanne de ralenti|r[ée]gulateur de ralenti", "papillon-motorise"),
    (r"\bfap\b|filtre (a|à) particules", "catalyseur"),
    (r"wastegate|waste gate|g[ée]om[ée]trie variable|membrane (du |de )?turbo", "turbocompresseur"),
    (r"porte[- ]filtre (a|à) gas\w*|filtre (a|à) (gasoil|gazole|gas-oil|essence|carburant)", "filtre-carburant"),
    (r"joints? d'?injecteurs?", "injecteurs"),
    (r"capteur (pmh|de vilebrequin|volant moteur|sur le volant)", "capteur-vilebrequin"),
    (r"silent ?blocs?", "silentblocs"),
    (r"bougies? (de )?(pr[ée]?chauff\w*|p[ée]chauff\w*|chauffe)", "bougies-prechauffage"),
    (r"tendeur", "galet-tendeur"),
]
EXTRA = [(re.compile(r"courroie (de l'?|d'?)?(alternateur|accessoires?|servitude)", re.IGNORECASE), "courroie-accessoires")] + \
        [(re.compile(p, re.IGNORECASE), slug) for p, slug in EXTRA]
# Mesure du 26/11/2026 (60 extraits relus) : 58 % de justes. Erreurs : hypothèses prises pour des confirmations, et
# pièces homonymes. D'où ces garde-fous.
HYPOTHESE = re.compile(r"\b(si|s'|persuad\w+|croyai\w*|pensai\w*|peut[- ]?[eê]tre|pas|comme si|soit|sans doute|"
                       r"au d[ée]but|d'abord|on m'a dit|on m'avait dit|me disait|m'ont dit|dit que|suppos\w+)\b[^.!?]{0,25}$", re.IGNORECASE)
INCERTAIN = re.compile(r"\?|\bou (le|la|les|un|une|bien|alors)\b|\bpeut[- ]?[eê]tre\b", re.IGNORECASE)
# « c'était bon / pareil / avant que… » : la tournure ne désigne rien
VIDE = re.compile(r"\s*(bon|pareil|avant|apr[eè]s|compris|exactement|tout simple|pour|moins|comme|pr[ée]vu|normal|grave|"
                  r"possible|clair|nickel|ok|vrai)\b", re.IGNORECASE)
# pièce nommée mais autre chose en cause (fil, faisceau…) ou homonyme d'un autre circuit
FAUX_AMIS = re.compile(r"^\s*(le |la |les |un |une |du |des )?(fil|fils|faisceau|connecteur|masse|cosse de masse|prise|"
                       r"c[aâ]ble de masse|relais|fusible|contacteur|tresse|capteur (de |du |d')?(la |l')?p[ée]dale)\b|"
                       r"durite\w*.{0,30}(turbo|[ée]changeur|intercooler)|"
                       r"durite (du |de |d')?(turbo|gas|gaz|essence|carbu|retour|"
                       r"hydraul|frein|direction|d'air|admission)|sonde\w* (de )?temp\w* (d'?)?(air|admission)|"
                       r"bobine d'appel|admission d'air", re.IGNORECASE)


def plain(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn")


def cause(solution: str) -> tuple[str | None, str]:
    """(pièce, extrait) : première pièce nommée juste après une tournure de cause."""
    for m in CUE.finditer(solution or ""):
        before = solution[max(0, m.start() - 40):m.start()]
        after = solution[m.end():]
        window = " ".join(after.split()[:WINDOW])
        sentence = re.split(r"[.!?]", after, maxsplit=1)[0]
        if VIDE.match(after):
            continue
        if HYPOTHESE.search(before) or INCERTAIN.search(" ".join(sentence.split()[:WINDOW + 3])) or FAUX_AMIS.search(window):
            continue
        for pat, slug in EXTRA:
            if pat.search(window):
                return slug, (m.group(0) + window)
        cats = categories_fr(window)
        if cats:
            return cats[0], (m.group(0) + window)
    return None, ""


# Troisième forme (27/11/2026) : « la pompe à eau était HS », « c'est bien le démarreur qui était mort » : la pièce est
# AVANT l'état. Le message doit aussi dire que c'est réglé (REUSSITE), sinon c'est un constat en cours de recherche.
ETAT = re.compile(r"\b([ée]tai(?:t|ent)|est|sont|[ée]tait bien)\s+(compl[eè]tement |bien |totalement |carr[ée]ment |d[ée]j[aà] )?"
                  r"(hs|h\.s|morte?s?|d[ée]fectueu(?:x|se|ses)|grip+[ée]e?s?|bouch[ée]e?s?|cass[ée]e?s?|fichue?s?|naze|"
                  r"foutue?s?|grill[ée]e?s?|cram[ée]e?s?|us[ée]e?s?|en cause|en court[- ]circuit|cuite?s?)\b", re.IGNORECASE)


def cause_etat(solution: str) -> tuple[str | None, str]:
    """« la X était HS … tout marche » : pièce dans les 6 mots avant l'état, réussite dite dans le message."""
    if not REUSSITE.search(solution or ""):
        return None, ""
    for sent in re.split(r"[.!?\n]", solution or ""):
        m = ETAT.search(sent)
        if not m:
            continue
        before = sent[:m.start()]
        if HYPOTHESE.search(before[-60:]) or INCERTAIN.search(sent) or re.search(r"\bpas\b|\bni\b|\bsi\b", before[-40:]):
            continue
        window = " ".join(before.split()[-6:])
        if FAUX_AMIS.search(window) or re.search(r"\b(et|ainsi que)\b", window):
            continue
        for pat, slug in EXTRA:
            if pat.search(window):
                return slug, (window + " " + m.group(0))
        cats = categories_fr(window)
        if len(cats) == 1:   # deux pièces nommées : on ne sait pas laquelle était hors service
            return cats[0], (window + " " + m.group(0))
    return None, ""


def cause_changement(solution: str) -> tuple[str | None, str]:
    """« j'ai changé la X … et tout marche » : pièce juste après le verbe, réussite dans la même phrase."""
    for sent in re.split(r"[.!?\n]", solution or ""):
        m = CHANGE.search(sent)
        if not m or not REUSSITE.search(sent[m.end():]) or HYPOTHESE.search(sent[:m.start()][-40:]):
            continue
        window = " ".join(sent[m.end():].split()[:5])
        if FAUX_AMIS.search(window) or re.search(r"\b(et|puis|ainsi que|,)\b.*\b(et|puis)\b", window):
            continue  # plusieurs pièces changées d'un coup : on ne sait pas laquelle était en cause
        for pat, slug in EXTRA:
            if pat.search(window):
                return slug, (m.group(0) + window)
        cats = categories_fr(window)
        if cats:
            return cats[0], (m.group(0) + window)
    return None, ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--echantillon", type=int, default=0, help="afficher N cas tirés au hasard pour mesurer la justesse")
    ap.add_argument("--graine", type=int, default=11)
    ap.add_argument("--source", choices=list(SOURCES), default="largus_forum")
    ap.add_argument("--changement", action="store_true",
                    help="ajouter la seconde forme : « j'ai changé X … et tout marche » (cause_changement)")
    ap.add_argument("--etat", action="store_true",
                    help="ajouter la troisième forme : « la X était HS … tout marche » (cause_etat)")
    ap.add_argument("--nouveaux", action="store_true",
                    help="n'écrire que les candidats absents de causes_verifiees.json (vérification suivante)")
    ap.add_argument("--verifiees", action="store_true",
                    help="reconstruire data/processed/largus_causes_verifiees.jsonl (exemples d'entraînement) à partir "
                         "de data/largus/causes_verifiees.json (identifiants vérifiés, sans texte)")
    args = ap.parse_args()
    src_name, out_name, ver_dir, ver_name = SOURCES[args.source]
    src, out_path = PROCESSED / src_name, PROCESSED / out_name
    if args.verifiees:
        ver = json.loads((ROOT / "data" / ver_dir / "causes_verifiees.json").read_text(encoding="utf-8"))["causes"]
        want = {c["id"]: c for c in ver}
        out = PROCESSED / ver_name
        # cas marqués « controle » : jeu de contrôle privé (data/test_prive/), jamais dans les exemples d'entraînement
        ctl_path = ROOT / "data" / "test_prive" / f"{ver_dir}_controle.jsonl"
        n = 0
        ctl_rows = []
        with out.open("w", encoding="utf-8") as f:
            for line in src.read_text(encoding="utf-8").split(chr(10)):
                if line.strip():
                    r = json.loads(line)
                    c = want.get(r["id"])
                    if not c:
                        continue
                    if c.get("controle"):
                        ctl_rows.append({"id": f"{ver_dir[:3]}c{len(ctl_rows) + 1:03d}", "source_id": r["id"],
                                         "text": r["text"], "expect": [c["part"]]})
                        continue
                    f.write(json.dumps({"id": r["id"], "text": r["text"], "part": c["part"], "fault": c["fault"]},
                                       ensure_ascii=False) + "\n")
                    n += 1
        if ctl_rows:
            ctl_path.parent.mkdir(parents=True, exist_ok=True)
            ctl_path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in ctl_rows), encoding="utf-8")
            print(f"{len(ctl_rows)} cas de contrôle -> {ctl_path}")
        print(f"{n} exemples vérifiés -> {out}")
        return
    banned = {json.loads(l)["source_id"] for p in TESTS for l in p.read_text(encoding="utf-8").split(chr(10)) if l.strip()}
    rows = []
    for line in src.read_text(encoding="utf-8").split(chr(10)):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["id"] in banned or not (r.get("meta") or {}).get("diagnostic", True):
            continue
        sol = ((r.get("meta") or {}).get("solution") or "").replace("’", "'")
        part, extrait = cause(sol)
        forme = "cause"
        if not part and args.changement:
            (part, extrait), forme = cause_changement(sol), "changement"
        if not part and args.etat:
            (part, extrait), forme = cause_etat(sol), "etat"
        if part:
            rows.append({"id": r["id"], "text": r["text"], "part": part, "extrait": extrait[:160], "forme": forme})
    if args.nouveaux:
        ver_file = ROOT / "data" / ver_dir / "causes_verifiees.json"
        seen = set(json.loads(ver_file.read_text(encoding="utf-8")).get("examines", [])) if ver_file.exists() else set()
        seen |= {c["id"] for c in json.loads(ver_file.read_text(encoding="utf-8"))["causes"]} if ver_file.exists() else set()
        rows = [r for r in rows if r["id"] not in seen]
    if args.echantillon:
        random.Random(args.graine).shuffle(rows)
        for i, r in enumerate(rows[:args.echantillon], 1):
            print(f"#{i} {r['part']} | {r['extrait']} || Q: {' '.join(r['text'].split())[:110]}")
        return
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    print(f"{len(rows)} causes extraites -> {out_path}")
    print(Counter(r["part"] for r in rows).most_common(40))


if __name__ == "__main__":
    main()
