"""Forum L'Argus « Panne auto, mécanique et entretien » : questions de conducteurs, réponses et solutions (français).

Lit la base SQLite produite par la collecte de l'utilisateur (tables `topics` et `messages`), en lecture seule.

    DALIL_LARGUS_AUTORISATION="écrite, 2026-11-20" python data/pipeline/run.py collect --sources largus_forum \\
        --largus-db C:/Users/.../largus_pannes.db

**Verrou** : rien n'est lu tant que DALIL_LARGUS_AUTORISATION n'est pas renseignée (accord de L'Argus, à archiver ;
voir data/sources/largus_forum.md). Un forum appartient à ses auteurs : sans accord, on n'utilise pas ses messages.

- **Anonymisation** : noms d'auteurs jamais repris ; adresses e-mail, liens, numéros et mentions « @ » effacés des textes.
- **Texte** = la question (titre + description du problème) : c'est ce qu'écrira un utilisateur de DALIL. La solution
  n'y est pas recopiée, sinon l'entraînement apprendrait à lire le nom de la pièce au lieu des symptômes.
- **Étiquette** (famille de pièce), par ordre de confiance (`label_quality`) :
  `solution` (solution confirmée ou message final de l'auteur), `reponses` (pièce la plus citée dans les réponses),
  `question` (pièce citée dans la question). Accord avec la catégorie du forum -> suffixe « +component ».
  Une panne type n'est attribuée que pour `solution` en accord avec la catégorie.
"""
from __future__ import annotations

import os
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Iterator

from ..common import Record
from ..taxonomy_map import categories_fr, family_fr, family_of, fault_for
from . import SOURCES, Context

# Catégories du forum -> famille de pièces DALIL. Seulement les correspondances sans ambiguïté : « Démarrage »,
# « Moteur », « Voyants » ou « Puissance » recouvrent plusieurs familles et ne sont pas forcés.
CATEGORY_FAMILY = {
    "freinage": "freinage", "frein": "freinage", "embrayage": "transmission", "boite de vitesse": "transmission",
    "boite de vitesses": "transmission", "transmission": "transmission", "climatisation": "climatisation",
    "chauffage": "refroidissement", "refroidissement": "refroidissement", "surchauffe": "refroidissement",
    "suspension": "suspension", "amortisseurs": "suspension", "direction": "direction", "echappement": "echappement",
    "distribution": "distribution", "courroie": "distribution", "allumage": "allumage", "batterie": "electricite",
    "eclairage": "electricite", "alternateur": "electricite", "injection": "alimentation", "carburant": "alimentation",
    "turbo": "alimentation", "train avant": "train-roulant", "roulement": "train-roulant",
}

_SCRUB = [
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[e-mail]"),
    (re.compile(r"(?:https?://|www\.)\S*", re.IGNORECASE), "[lien]"),
    # numéros : 0X XX XX XX XX, +33 ou +213 (pas « 120000 km 2003 », qui ne commence pas par 0)
    (re.compile(r"(?<!\d)(?:(?:\+|00)(?:33|213)[\s.-]?0?|0)[1-9](?:[\s.-]?\d{2}){4}(?!\d)"), "[téléphone]"),
    (re.compile(r"(?<![\w@])@[^\s@]{2,}"), "[compte]"),
]
YEAR_RE = re.compile(r"(?<!\d)(19[5-9]\d|20[0-3]\d)(?!\d)")


def scrub(text: str) -> str:
    t = text or ""
    for pat, label in _SCRUB:
        t = pat.sub(label, t)
    return re.sub(r"[ \t]+", " ", t).strip()


def _plain(s: str) -> str:
    import unicodedata

    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn").strip()


def category_family(cat: str | None) -> str | None:
    c = _plain(cat or "")
    if c in CATEGORY_FAMILY:
        return CATEGORY_FAMILY[c]
    return family_fr(c) if c else None


def _vehicle(topic: dict) -> dict:
    declared = topic.get("model_declared") or ""
    y = YEAR_RE.search(declared)
    low = _plain(declared)
    fuel = "diesel" if re.search(r"diesel|dci|hdi|tdi|crdi|jtd|d-?4d|gasoil", low) else (
        "essence" if re.search(r"essence|vti|tsi|tce|16v|puretech", low) else None)
    return {"make": topic.get("brand"), "model": topic.get("model"), "year": int(y.group(1)) if y else None,
            "fuel": fuel, "declared": scrub(declared)[:120], "dalil_brand": None, "dalil_model": None}


def label(topic: dict, replies: list[str], author_last: str | None) -> tuple[list[str], str | None, str | None]:
    """(catégories, famille, qualité) d'après la solution, les réponses, puis la question."""
    fam_cat = category_family(topic.get("symptom_category"))
    tiers = [("solution", " ".join(x for x in [topic.get("resolution_summary"), author_last] if x))]
    votes: Counter = Counter()
    for r in replies:
        for c in categories_fr(r)[:2]:
            votes[c] += 1
    question = f"{topic.get('title') or ''} {topic.get('problem_description') or ''}"
    for quality, text in tiers:
        cats = categories_fr(text) if text.strip() else []
        if cats:
            return _with_family(cats, fam_cat, quality)
    if votes:
        return _with_family([c for c, _ in votes.most_common()], fam_cat, "reponses")
    cats = categories_fr(question)
    if cats:
        return _with_family(cats, fam_cat, "question")
    return [], fam_cat, "component" if fam_cat else None


def _with_family(cats: list[str], fam_cat: str | None, quality: str) -> tuple[list[str], str | None, str]:
    if fam_cat:
        same = [c for c in cats if family_of(c) == fam_cat]
        if same:
            return same[:3], fam_cat, f"{quality}+component"
    return cats[:3], family_of(cats[0]), quality


def _connect(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)  # lecture seule
    con.row_factory = sqlite3.Row
    return con


def collect(ctx: Context) -> Iterator[Record]:
    spec = SOURCES["largus_forum"]
    autorisation = os.environ.get("DALIL_LARGUS_AUTORISATION", "").strip()
    if not autorisation:
        raise SystemExit("L'Argus : DALIL_LARGUS_AUTORISATION non renseignée. Un forum appartient à ses auteurs : "
                         "renseigner l'accord de L'Argus (ex. « écrite, 2026-11-20 ») avant toute lecture.")
    db = ctx.options.get("largus_db") or os.environ.get("DALIL_LARGUS_DB")
    if not db or not Path(db).exists():
        raise SystemExit(f"L'Argus : base introuvable ({db}). Option --largus-db ou variable DALIL_LARGUS_DB.")
    con = _connect(db)
    topics = [dict(r) for r in con.execute("SELECT * FROM topics ORDER BY topic_id")]
    msgs: dict[str, list[dict]] = {}
    for r in con.execute("SELECT topic_id, post_number, author, content FROM messages ORDER BY topic_id, post_number"):
        msgs.setdefault(str(r["topic_id"]), []).append(dict(r))
    con.close()
    ctx.log(f"  {len(topics)} discussions, {sum(len(v) for v in msgs.values())} messages (autorisation : {autorisation})")

    n = 0
    for t in topics:
        question = scrub(f"{t.get('title') or ''}. {t.get('problem_description') or ''}").strip(" .")
        if len(question) < 15:
            continue
        posts = msgs.get(str(t["topic_id"]), [])
        replies = [scrub(p["content"] or "") for p in posts if p["post_number"] and int(p["post_number"]) > 1
                   and p.get("author") != t.get("author")]
        own_last = next((scrub(p["content"] or "") for p in reversed(posts)
                         if p.get("author") == t.get("author") and p["post_number"] and int(p["post_number"]) > 1), None)
        resolved = str(t.get("is_resolved")) in ("1", "True", "true")
        cats, fam, quality = label(t, replies, own_last if resolved else None)
        strong = quality == "solution+component"
        yield Record(
            id=f"largus_forum:{t['topic_id']}", source=spec.id, kind="qa", lang="fr", text=question,
            license=spec.license, attribution=spec.attribution, url=t.get("url"),
            vehicle=_vehicle(t), categories=cats, family=fam,
            fault=fault_for(cats, "keyword+component") if strong else None, label_quality=quality,
            meta={"diagnostic": True, "resolved": resolved, "symptom_category": t.get("symptom_category"),
                  "replies": len(replies), "views": t.get("views_count"),
                  "solution": scrub(t.get("resolution_summary") or "")[:1000] or None},
        )
        n += 1
        if ctx.limit and n >= ctx.limit:
            return
