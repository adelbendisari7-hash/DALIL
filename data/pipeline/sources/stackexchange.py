"""Stack Exchange Mechanics : questions de panne avec réponse acceptée (export du 31/12/2024).

Pourquoi cet export : les exports publiés depuis juin 2025 contiennent des données volontairement
altérées (section 5 du cahier des charges).

Étiquetage : la question décrit les symptômes, la réponse acceptée nomme la cause. La pièce est donc
cherchée d'abord dans la réponse, puis dans les étiquettes (tags), puis dans la question.
Attribution CC BY-SA 4.0 : lien vers la question et nom de l'auteur gardés pour chaque enregistrement.
"""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator

from ..common import RAW, Record, download
from ..taxonomy_map import categories_en, fault_for, reconcile
from . import SOURCES, Context

DUMP = "https://archive.org/download/stackexchange_20241231/stackexchange_20241231/mechanics.stackexchange.com.7z"
SITE = "https://mechanics.stackexchange.com"
MAKES = {
    "toyota", "honda", "ford", "chevrolet", "nissan", "hyundai", "kia", "renault", "peugeot", "citroen", "dacia",
    "volkswagen", "vw", "fiat", "skoda", "opel", "vauxhall", "mazda", "subaru", "bmw", "mercedes-benz", "audi",
    "mitsubishi", "suzuki", "seat", "volvo", "jeep", "dodge", "chrysler", "gmc", "buick", "lexus", "mini",
}
TAG_RE = re.compile(r"<([^>]+)>|\|([^|]+)(?=\|)")
# Une question « diagnostique » décrit un symptôme ; les autres (procédures, culture générale)
# restent dans la base de connaissances mais ne servent pas d'exemples d'entraînement.
SYMPTOM_RE = re.compile(
    r"\b(noise|noisy|sound|squeal|squeak|grind|grinding|rattl|clunk|knock|ticking|whin|humming|vibrat|shak|shudder|"
    r"leak|drip|smell|smoke|overheat|stall|won'?t start|wont start|no start|doesn'?t start|hard (to )?start|cranks? but|"
    r"misfir|rough idle|idle|hesitat|lose power|loss of power|losing power|warning light|check engine|cel\b|"
    r"light (is |comes |came )?on|dash light|pull(s|ing)? to|wobbl|slipping|dead battery|battery (dies|drain)|won'?t|symptom)",
    re.IGNORECASE,
)
PROCEDURE_RE = re.compile(
    r"^\s*(how (to|do|can|tight|much|often|long|should)|what is the best way|what('s| is) the (best|right|correct)|"
    r"what size|which|can i|should i|is it (ok|okay|safe|normal|possible|worth)|where (is|can|do)|do i need)",
    re.IGNORECASE,
)


def strip_html(s: str) -> str:
    s = re.sub(r"(?is)<(pre|code)[^>]*>.*?</\1>", " ", s or "")
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def _extract(ctx: Context) -> tuple:
    import py7zr

    archive = download(DUMP, RAW / "stackexchange" / "mechanics.stackexchange.com.7z", refresh=ctx.refresh, log=ctx.log)
    out = RAW / "stackexchange" / "mechanics"
    if ctx.refresh or not (out / "Posts.xml").exists():
        with py7zr.SevenZipFile(archive) as z:
            z.extract(path=out, targets=["Posts.xml", "Users.xml"])
    return out / "Posts.xml", out / "Users.xml"


def _rows(path) -> Iterator[dict]:
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag == "row":
            yield dict(el.attrib)
            el.clear()


def collect(ctx: Context) -> Iterator[Record]:
    spec = SOURCES["stackexchange_mechanics"]
    posts_path, users_path = _extract(ctx)
    users = {u["Id"]: u.get("DisplayName", "") for u in _rows(users_path)}
    questions, answers = {}, {}
    for p in _rows(posts_path):
        if p.get("PostTypeId") == "1" and p.get("AcceptedAnswerId") and int(p.get("Score", 0)) >= 1:
            questions[p["Id"]] = p
        elif p.get("PostTypeId") == "2":
            answers[p["Id"]] = p
    ctx.log(f"  {len(questions)} questions avec réponse acceptée")
    n = 0
    for qid, q in questions.items():
        a = answers.get(q["AcceptedAnswerId"])
        if a is None:
            continue
        title, body, answer = q.get("Title", ""), strip_html(q.get("Body", "")), strip_html(a.get("Body", ""))
        tags = [t1 or t2 for t1, t2 in TAG_RE.findall(q.get("Tags", ""))]
        cats = categories_en(answer) or categories_en(" ".join(t.replace("-", " ") for t in tags)) or categories_en(title + " " + body)
        cats, fam, quality = reconcile(cats, None)
        diagnostic = bool(SYMPTOM_RE.search(title + " " + body[:600])) and not PROCEDURE_RE.search(title)
        make = next((t for t in tags if t in MAKES), None)
        author = users.get(q.get("OwnerUserId", ""), "") or q.get("OwnerDisplayName", "")
        yield Record(
            id=f"stackexchange_mechanics:{qid}", source=spec.id, kind="qa", lang="en",
            text=f"{title}. {body}"[:3000], license=spec.license,
            attribution=f"{author or 'auteur inconnu'}, {SITE}/q/{qid} (CC BY-SA 4.0, traduit et abrégé)",
            url=f"{SITE}/q/{qid}", vehicle={"make": make.title(), "model": None, "year": None, "dalil_brand": None,
                                            "dalil_model": None} if make else None,
            categories=cats, family=fam, fault=fault_for(cats, quality) if diagnostic else None, label_quality=quality,
            meta={"diagnostic": diagnostic, "tags": tags, "score": int(q.get("Score", 0)), "answer": answer[:3000],
                  "answer_url": f"{SITE}/a/{a['Id']}", "answer_author": users.get(a.get("OwnerUserId", ""), "")},
        )
        n += 1
        if ctx.limit and n >= ctx.limit:
            return
