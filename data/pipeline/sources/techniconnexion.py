"""Forum Techniconnexion (techniconnexion.com) : pannes décrites par des conducteurs, réponses de mécaniciens (français).

Lit la collecte de l'utilisateur (dossier `ml_ready/` : `dataset_full.jsonl`, une ligne par discussion, et
`posts_with_metadata.jsonl`, une ligne par message), en lecture seule.

    DALIL_TECHNICONNEXION_AUTORISATION="orale, 2026-11-27" python data/pipeline/run.py collect \\
        --sources techniconnexion --techniconnexion-dir C:/Users/.../WebScraping/data/ml_ready

**Verrou** : rien n'est lu tant que DALIL_TECHNICONNEXION_AUTORISATION n'est pas renseignée. Le site n'a ni licence
ni conditions d'utilisation, et son robots.txt refuse l'entraînement d'IA (`Content-Signal: ai-train=no`) : seul
l'accord des administrateurs permet l'usage (voir data/sources/techniconnexion.md).

Réduction du bruit (relevée sur la collecte complète, 27/11/2026) :
- **Citations retirées** : le texte de chaque message est relu dans son HTML, sans les blocs `<blockquote>`
  (22 000 messages citent un autre message ; sans cela, l'hypothèse d'un autre passerait pour la cause trouvée).
- **Mentions du forum retirées** : fichiers joints, « Vous n'avez pas la permission… », « Téléchargé n fois »,
  « Dernière édition par… », « Sujet répertorié ici ».
- **Sujets qui ne sont pas des pannes** (`diagnostic = False`, hors entraînement) : index des sections « résolus »,
  tutos et fiches pratiques, listes, périodicités, revues techniques, achats, et questions de procédure
  (« comment démonter… », « dépose… ») qui ne décrivent aucun symptôme.
- **Formules de clôture** des modérateurs (« merci pour le retour d'infos ») : jamais prises pour une solution ;
  elles servent seulement à savoir que la discussion est résolue (`meta.repertorie`).
- **Anonymisation** : pseudonymes de tous les participants, e-mails, liens, numéros, plaques et mentions « @ » masqués.

Étiquette (famille de pièce), par ordre de confiance, comme pour L'Argus : `solution` (message de l'auteur qui
donne la cause), `auteur`, `reponses` (pièce la plus citée, les techniciens confirmés du forum comptant double),
`question`. Accord avec la section du forum (Moteur, Électricité, Trains roulants…) -> suffixe « +domaine ».
Une panne type n'est attribuée que pour `solution+domaine` d'une discussion résolue.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterator

from ..common import Record
from ..taxonomy_map import categories_fr, family_of, fault_for
from . import SOURCES, Context
from .largus import SOLUTION_CUE, _plain

# Section du forum -> familles de pièces compatibles. Les sections sont larges : elles confirment une famille,
# elles n'en imposent aucune.
DOMAIN_FAMILIES = {
    "moteur": {"moteur", "alimentation", "allumage", "distribution", "refroidissement", "gestion-moteur", "filtration",
               "echappement", "transmission"},
    "electricite": {"electricite", "allumage", "gestion-moteur", "climatisation", "refroidissement"},
    "trains roulants": {"freinage", "suspension", "direction", "train-roulant", "transmission"},
    "interieur": {"climatisation", "electricite", "refroidissement"},
    "carrosserie": {"electricite"},
}
# Rangs du forum attribués aux membres qui réparent (les autres : « Nouveau », « Petit mécano »…)
EXPERT_RANKS = {"tech-admin", "tech-modo", "tech-d'honneur", "ingenieur", "technicien superieur", "technicien",
                "mecano qualifie", "mecano"}

NOT_A_FAULT_TITLE = re.compile(
    r"\btuto\b|tutoriel|fiches? pratiques?|probl[eè]mes?s? .{0,40}r[eé]solus|r[eé]pertoire|\bliste (des|de)\b|"
    r"p[eé]riodicit[eé]|revue technique|\brta\b|documentation|notice|sch[eé]ma|pr[eé]sentation|bienvenue|"
    r"\b(achat|acheter|vente|vendre|vends|recherche (une|un) (voiture|v[eé]hicule))\b|conseil d'achat|"
    r"\bavis\b|comparatif|quelle? (huile|marque|voiture|mod[eè]le)", re.IGNORECASE)
PROCEDURE_TITLE = re.compile(
    r"^\s*(comment\s+)?(d[eé]monter|d[eé]montage|d[eé]pose[rz]?|repose|remplacer|remplacement|changer|changement|"
    r"enlever|retirer|sortir|monter|montage|installer|installation|brancher|branchement|r[eé]gler|r[eé]glage|"
    r"purger|purge|vidange|vidanger|calage|caler la|acc[eé]der|ouvrir|o[uù] (se )?trouve|o[uù] est|r[eé]f[eé]rence|"
    r"num[eé]ro|code peinture|couple de serrage|programm\w+|codage|coder|r[eé]initialis\w+|raz)\b", re.IGNORECASE)
SYMPTOM = re.compile(
    r"panne|probl[eéè]me|pb\b|souci|bruit|fait du (froid|bruit)|(marche|tourne) (pas|plus|mal)|claque|cliquet|siffl|grinc|cogn|vibr|tremble|fui(t|te|tes|r|e)\b|fume|fum[eé]e|odeur|"
    r"cass[eé]|\bcasse\b|us[eé]e?s?\b|l[aâ]ch[eé]|anormal|bizarre|\bne \w+ plus\b|allum[eé]|"
    r"cale\b|calage moteur|d[eé]marre (pas|plus|mal)|d[eé]marrage|voyant|t[eé]moin|code (d[eé]faut|erreur)|\bp[0-3]\d{3}\b|"
    r"perte de puissance|manque de puissance|mode d[eé]grad|[aà][- ]coups?|broute|rat[eé]s|chauffe|surchauffe|"
    r"consomm|ne (marche|fonctionne|s'allume|charge|tient|monte|passe|freine|refroidit|chauffe)|"
    r"plus de (frein|chauffage|clim|courant)|hs\b|grill[eé]|bloqu|dur\b|patine|craque|ralenti|s'[eé]teint|"
    r"d[eé]fectu|d[eé]faut", re.IGNORECASE)
CLOSURE = re.compile(r"r[eé]pertori|retour d'?\s?infos?|merci (pour|de) (le|ton|ce|votre) retour", re.IGNORECASE)
TOPIC_LINK = re.compile(r"/t(\d+)-")

_SCRUB = [
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[e-mail]"),
    (re.compile(r"(?:https?://|www\.)\S*", re.IGNORECASE), "[lien]"),
    (re.compile(r"(?<!\d)(?:(?:\+|00)(?:33|32|41|213)[\s.-]?0?|0)[1-9](?:[\s.-]?\d{2}){4}(?!\d)"), "[téléphone]"),
    (re.compile(r"\b[A-Z]{2}[- ]?\d{3}[- ]?[A-Z]{2}\b"), "[plaque]"),
    (re.compile(r"(?<![\w@])@[^\s@+]{2,}"), "[compte]"),
]
_BOILERPLATE = [
    re.compile(r"Vous n'avez pas la permission de t[eé]l[eé]charger les fichiers joints\.?", re.IGNORECASE),
    re.compile(r"Fichiers? joints?", re.IGNORECASE),
    re.compile(r"[^\n]*\.(pdf|jpe?g|png|gif|bmp|zip|rar|doc|xls)\b[^\n]*", re.IGNORECASE),
    re.compile(r"\(\d+ ?[KkMm]o\) T[eé]l[eé]charg[eé] \d+ fois"),
    re.compile(r"Derni[eè]re [eé]dition par[^\n]*", re.IGNORECASE),
    re.compile(r"Sujet r[eé]pertori[eé] (ici|dans)[^\n]*", re.IGNORECASE),
    re.compile(r"[^\n]*\ba [eé]crit ?:", re.IGNORECASE),   # citation que le HTML n'aurait pas balisée
]


class _Text(HTMLParser):
    """Texte d'un message sans les citations (<blockquote>), les balises de code ni les images."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("blockquote", "script", "style"):
            self.skip += 1
        elif tag in ("br", "p", "div", "li", "tr") and not self.skip:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("blockquote", "script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def own_text(html: str | None, fallback: str = "") -> str:
    """Texte propre au message (citations retirées). Sans HTML, le texte de la collecte."""
    if not html:
        return fallback or ""
    p = _Text()
    try:
        p.feed(html)
        p.close()
    except Exception:  # HTML cassé : on garde le texte de la collecte
        return fallback or ""
    return re.sub(r"\n\s*\n+", "\n", "".join(p.out)).strip()


def mask_names(text: str, names: set[str]) -> str:
    for name in sorted((n for n in names if n and len(n) >= 3), key=len, reverse=True):
        text = re.sub(rf"(?<![\w@]){re.escape(name)}(?!\w)", "[membre]", text, flags=re.IGNORECASE)
    return text


def scrub(text: str, names: set[str] | None = None) -> str:
    t = text or ""
    for pat in _BOILERPLATE:
        t = pat.sub(" ", t)
    if names:
        t = mask_names(t, names)
    for pat, label in _SCRUB:
        t = pat.sub(label, t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def is_diagnostic(title: str, first_post: str, index_section: bool) -> bool:
    """Le sujet décrit-il une panne ? (sinon : hors entraînement)"""
    if index_section or NOT_A_FAULT_TITLE.search(title or ""):
        return False
    if PROCEDURE_TITLE.search(title or "") and not SYMPTOM.search(title or ""):
        return False  # « Démontage du tableau de bord » : une procédure, même si le message parle d'un souci
    return bool(SYMPTOM.search(f"{title} {first_post}"))


def domain(subsystem: str | None) -> str | None:
    d = _plain(subsystem or "")
    return d if d in DOMAIN_FAMILIES else None


def author_solution(own_posts: list[str]) -> tuple[str | None, bool]:
    """Le dernier message de l'auteur qui donne la cause (True), sinon son dernier message (False)."""
    for text in reversed(own_posts):
        if SOLUTION_CUE.search(text or ""):
            return text, True
    return (own_posts[-1], False) if own_posts else (None, False)


def label(question: str, replies: list[tuple[str, bool]], author_last: str | None, author_is_solution: bool,
          dom: str | None) -> tuple[list[str], str | None, str | None]:
    """(catégories, famille, qualité). `replies` = [(texte, écrit par un technicien confirmé)]."""
    allowed = DOMAIN_FAMILIES.get(dom or "", set())
    tiers = [("solution" if author_is_solution else "auteur", author_last or "")]
    for quality, text in tiers:
        cats = categories_fr(text) if text.strip() else []
        if cats:
            return _with_domain(cats, allowed, quality)
    votes: Counter = Counter()
    for text, expert in replies:
        for c in categories_fr(text)[:2]:
            votes[c] += 2 if expert else 1
    if votes:
        return _with_domain([c for c, _ in votes.most_common()], allowed, "reponses")
    cats = categories_fr(question)
    if cats:
        return _with_domain(cats, allowed, "question")
    return [], None, None


def _with_domain(cats: list[str], allowed: set[str], quality: str) -> tuple[list[str], str | None, str]:
    same = [c for c in cats if family_of(c) in allowed]
    if same:
        return same[:3], family_of(same[0]), f"{quality}+domaine"
    return cats[:3], family_of(cats[0]), quality


def _vehicle(t: dict) -> dict:
    fuel = _plain(t.get("fuel_type") or "") or None
    year = t.get("year")
    try:
        year = int(year) if year and 1950 <= int(year) <= 2035 else None
    except (TypeError, ValueError):
        year = None
    return {"make": t.get("brand") or None, "model": t.get("model") or None, "year": year, "fuel": fuel,
            "engine": t.get("engine_code") or t.get("displacement") or None, "dalil_brand": None, "dalil_model": None}


def _read_posts(path: Path) -> dict[int, list[dict]]:
    posts: dict[int, list[dict]] = defaultdict(list)
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            p = json.loads(line)
            posts[p["topic_id"]].append({
                "i": p.get("post_index") or 0, "author": p.get("author") or "",
                "rank": _plain(p.get("author_rank") or ""),
                "text": own_text(p.get("content_html"), p.get("content_text") or ""),
                "links": {int(x) for x in TOPIC_LINK.findall(p.get("content_html") or "")},
            })
    for ps in posts.values():
        ps.sort(key=lambda p: p["i"])
    return posts


def collect(ctx: Context) -> Iterator[Record]:
    spec = SOURCES["techniconnexion"]
    autorisation = os.environ.get("DALIL_TECHNICONNEXION_AUTORISATION", "").strip()
    if not autorisation:
        raise SystemExit("Techniconnexion : DALIL_TECHNICONNEXION_AUTORISATION non renseignée. Le site refuse "
                         "l'entraînement d'IA (robots.txt) : renseigner l'accord des administrateurs avant toute lecture.")
    folder = ctx.options.get("techniconnexion_dir") or os.environ.get("DALIL_TECHNICONNEXION_DIR")
    if not folder or not (Path(folder) / "dataset_full.jsonl").exists():
        raise SystemExit(f"Techniconnexion : collecte introuvable ({folder}). Option --techniconnexion-dir.")
    folder = Path(folder)
    posts = _read_posts(folder / "posts_with_metadata.jsonl")
    topics = [json.loads(line) for line in (folder / "dataset_full.jsonl").open(encoding="utf-8") if line.strip()]
    # discussions rangées par un modérateur dans une section « résolus » (liens des index)
    filed = {tid for t in topics if t.get("is_resolved_section") for p in posts.get(t["topic_id"], []) for tid in p["links"]}
    ctx.log(f"  {len(topics)} discussions, {sum(len(v) for v in posts.values())} messages, {len(filed)} rangées "
            f"comme résolues (autorisation : {autorisation})")

    n = 0
    for t in topics:
        ps = posts.get(t["topic_id"], [])
        if not ps:
            continue
        author = ps[0]["author"]
        names = {p["author"] for p in ps}
        title = scrub(t.get("symptom_title") or "", names)
        first = scrub(ps[0]["text"], names)
        question = f"{title}. {first}".strip(" .")
        if len(question) < 20:
            continue
        later = ps[1:]
        closure = any(CLOSURE.search(p["text"]) for p in later if p["author"] != author)
        resolved = bool(t.get("is_resolved")) or closure or t["topic_id"] in filed
        own = [scrub(p["text"], names) for p in later if p["author"] == author]
        replies = [(scrub(p["text"], names), p["rank"] in EXPERT_RANKS) for p in later
                   if p["author"] != author and not CLOSURE.search(p["text"])]
        author_text, cue = author_solution(own)
        dom = domain(t.get("subsystem"))
        cats, fam, quality = label(question, replies, author_text, cue, dom)
        # Relecture du 27/11/2026 (120 étiquettes, sans voir le niveau) : quand la famille trouvée est aussi celle
        # d'une pièce nommée dans la question, elle est juste dans 73 à 82 % des cas, sinon dans 31 à 44 %.
        if quality and not quality.startswith("question") and fam in {family_of(c) for c in categories_fr(question)[:2]}:
            quality += "+accord"
        diagnostic = is_diagnostic(t.get("symptom_title") or "", first, bool(t.get("is_resolved_section")))
        strong = (quality or "").startswith("solution+domaine") and resolved
        yield Record(
            id=f"techniconnexion:{t['topic_id']}", source=spec.id, kind="qa", lang="fr", text=question,
            license=spec.license, attribution=spec.attribution, url=f"https://www.techniconnexion.com{t.get('topic_url') or ''}",
            vehicle=_vehicle(t), categories=cats, family=fam,
            fault=fault_for(cats, "keyword+component") if strong else None, label_quality=quality,
            meta={"diagnostic": diagnostic, "resolved": resolved, "repertorie": closure or t["topic_id"] in filed,
                  "domain": dom, "brand_group": t.get("brand_group"), "replies": len(replies),
                  "expert_replies": sum(e for _, e in replies), "fault_codes": t.get("fault_codes") or [],
                  "solution": (author_text if cue else "")[:1500] or None},
        )
        n += 1
        if ctx.limit and n >= ctx.limit:
            break
