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
  `solution` (résumé de solution du forum, ou message de l'auteur qui donne la cause : « c'était bien… », « résolu »,
  « j'ai changé… »), `auteur` (dernier message de l'auteur, sans tournure de solution), `reponses` (pièce la plus
  citée dans les réponses), `question` (pièce citée dans la question). Accord avec la catégorie du forum -> suffixe
  « +component ». Une panne type n'est attribuée que pour `solution+component`.

Constat du 24/11/2026 sur la base complète (99 779 discussions) : 0,2 % seulement sont marquées « résolues », mais
l'auteur revient dans 44 % des discussions et donne souvent la cause : son dernier message est lu pour toutes.
Seules 51 catégories sont propres (74 % des discussions) ; ailleurs, le champ catégorie contient le titre recopié
depuis l'adresse : il n'est alors pas pris pour une catégorie. Les sujets qui ne décrivent pas une panne (avis,
entretien, autoradio, GPS, actualité…) sont marqués `diagnostic = False` et restent hors de l'entraînement.
"""
from __future__ import annotations

import os
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Iterator

from ..common import Record
from ..taxonomy_map import categories_fr, family_of, fault_for
from . import SOURCES, Context

# Catégories du forum -> famille de pièces DALIL. Seulement les correspondances sans ambiguïté : « Démarrage »,
# « Moteur », « Voyants », « Puissance », « Bruit », « Ralenti » ou « Fumée » recouvrent plusieurs familles et ne
# sont pas forcés. Les 51 catégories propres de la collecte (au moins 100 discussions chacune) sont ici, dans
# CLEAN_CATEGORIES ou dans NOT_A_FAULT ; tout autre texte du champ catégorie est un titre recopié depuis l'adresse.
CATEGORY_FAMILY = {
    "freinage": "freinage", "frein": "freinage", "abs": "freinage", "embrayage": "transmission",
    "boite de vitesse": "transmission", "boite de vitesses": "transmission", "transmission": "transmission",
    "climatisation": "climatisation", "chauffage": "refroidissement", "refroidissement": "refroidissement",
    "circuit de refroidissement": "refroidissement", "liquide de refroidissement": "refroidissement",
    "moteur surchauffe": "refroidissement", "surchauffe": "refroidissement", "radiateur": "refroidissement",
    "ventilateur": "refroidissement", "suspension": "suspension", "amortisseurs": "suspension",
    "amortisseur": "suspension", "direction": "direction", "echappement": "echappement",
    "distribution": "distribution", "courroie": "distribution", "allumage": "allumage", "bougies": "allumage",
    "prechauffage": "allumage", "batterie": "electricite", "eclairage": "electricite", "alternateur": "electricite",
    "fusibles": "electricite", "injection": "alimentation", "carburant": "alimentation", "turbo": "alimentation",
    "filtre": "filtration", "huile": "moteur", "train avant": "train-roulant", "roulement": "train-roulant",
}
# Catégories propres sans famille unique (gardées pour l'entraînement, sans suffixe « +component »)
CLEAN_CATEGORIES = {
    "demarrage", "moteur", "electronique", "voyants", "bruit", "puissance", "cle et verrouillage", "compteur",
    "moteur cale", "moteur broute", "tableau de bord", "antidemarrage", "ralenti", "fumee", "leve vitre",
    "essuie glace", "ventilation", "roues et pneus", "vibration",
}
# Catégories qui ne décrivent pas une panne : hors de l'entraînement (diagnostic = False), gardées en connaissance
NOT_A_FAULT = {"avis et fiabilite", "entretien", "autoradio", "gps", "alarme", "carrosserie", "actualite et nouveautes"}
# Le message de l'auteur donne la cause trouvée
SOLUTION_CUE = re.compile(
    r"c'?[eé]tait|c'est bien|r[eé]solu|r[eé]gl[eé]|j'ai (fait )?chang[eé]|"
    r"(a|ont) [eé]t[eé] chang[eé]|remplac[eé]|le probl[eè]me venait|venait d[eu' ]|tout est rentr[eé]|"
    r"(ça|ca) (re)?marche|plus de probl[eè]me|trouv[eé] la (panne|cause)", re.IGNORECASE)

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


def clean_category(cat: str | None) -> str | None:
    """Catégorie du forum si elle est l'une des catégories propres, sinon None (titre recopié depuis l'adresse)."""
    c = _plain(cat or "")
    return c if c in CATEGORY_FAMILY or c in CLEAN_CATEGORIES or c in NOT_A_FAULT else None


def category_family(cat: str | None) -> str | None:
    c = clean_category(cat)
    return CATEGORY_FAMILY.get(c) if c else None


def post_number(p: dict) -> int:
    """« #3 » ou 3 -> 3 (la collecte écrit « #n »)."""
    digits = re.sub(r"\D", "", str(p.get("post_number") or ""))
    return int(digits) if digits else 0


def _vehicle(topic: dict) -> dict:
    declared = topic.get("model_declared") or ""
    y = YEAR_RE.search(declared)
    low = _plain(declared)
    fuel = "diesel" if re.search(r"diesel|dci|hdi|tdi|crdi|jtd|d-?4d|gasoil", low) else (
        "essence" if re.search(r"essence|vti|tsi|tce|16v|puretech", low) else None)
    return {"make": topic.get("brand"), "model": topic.get("model"), "year": int(y.group(1)) if y else None,
            "fuel": fuel, "declared": scrub(declared)[:120], "dalil_brand": None, "dalil_model": None}


def author_solution(own_posts: list[str]) -> tuple[str | None, bool]:
    """Le dernier message de l'auteur qui donne la cause (True), sinon son dernier message (False)."""
    for text in reversed(own_posts):
        if SOLUTION_CUE.search(text or ""):
            return text, True
    return (own_posts[-1], False) if own_posts else (None, False)


def label(topic: dict, replies: list[str], author_last: str | None,
          author_is_solution: bool = True) -> tuple[list[str], str | None, str | None]:
    """(catégories, famille, qualité) d'après la solution, le dernier message de l'auteur, les réponses, la question."""
    fam_cat = category_family(topic.get("symptom_category"))
    summary = topic.get("resolution_summary") or ""
    if author_is_solution:
        tiers = [("solution", " ".join(x for x in [summary, author_last] if x))]
    else:
        tiers = [("solution", summary), ("auteur", author_last or "")]
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
    n_topics = con.execute("SELECT count(*) FROM topics").fetchone()[0]
    n_msgs = con.execute("SELECT count(*) FROM messages").fetchone()[0]
    ctx.log(f"  {n_topics} discussions, {n_msgs} messages (autorisation : {autorisation})")

    # Discussion par discussion (index sur messages.topic_id) : la base complète ne tient pas confortablement en
    # mémoire. Messages dans l'ordre d'enregistrement : « #10 » trié comme texte passerait avant « #2 ».
    n = 0
    for row in con.execute("SELECT * FROM topics ORDER BY topic_id"):
        t = dict(row)
        question = scrub(f"{t.get('title') or ''}. {t.get('problem_description') or ''}").strip(" .")
        if len(question) < 15:
            continue
        posts = [dict(r) for r in con.execute(
            "SELECT post_number, author, content FROM messages WHERE topic_id = ? ORDER BY id", (t["topic_id"],))]
        replies = [scrub(p["content"] or "") for p in posts if post_number(p) > 1 and p.get("author") != t.get("author")]
        own = [scrub(p["content"] or "") for p in posts if post_number(p) > 1 and p.get("author") == t.get("author")]
        resolved = str(t.get("is_resolved")) in ("1", "True", "true")
        author_text, cue = author_solution(own)
        cats, fam, quality = label(t, replies, author_text, author_is_solution=cue or resolved)
        strong = quality == "solution+component"
        category = clean_category(t.get("symptom_category"))
        yield Record(
            id=f"largus_forum:{t['topic_id']}", source=spec.id, kind="qa", lang="fr", text=question,
            license=spec.license, attribution=spec.attribution, url=t.get("url"),
            vehicle=_vehicle(t), categories=cats, family=fam,
            fault=fault_for(cats, "keyword+component") if strong else None, label_quality=quality,
            meta={"diagnostic": category not in NOT_A_FAULT, "resolved": resolved, "symptom_category": category,
                  "replies": len(replies), "views": t.get("views_count"),
                  "solution": (scrub(t.get("resolution_summary") or "") or (author_text if cue else ""))[:1000] or None},
        )
        n += 1
        if ctx.limit and n >= ctx.limit:
            break
    con.close()
