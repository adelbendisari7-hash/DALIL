"""CVFFAD (Mendeley Data, CC BY 4.0) : types de pannes et graphe de connaissances, en chinois.

Ce que la source apporte vraiment : 35 types de pannes, chacun relié à ses symptômes, causes et
réparations (graphe de 565 triplets). Ce qu'elle n'apporte pas : les textes d'événements sont générés
par gabarit (champ source = generated) et décrivent des camions et cars de marques anonymisées.
On n'en garde donc qu'une fiche par type de panne, marquée synthetic, jamais utilisée pour l'évaluation.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

from ..common import RAW, Record, download
from ..taxonomy_map import family_of
from . import SOURCES, Context

BASE = "https://data.mendeley.com/public-files/datasets/r98g7g6k5t/files/"
FILES = {
    "fault_events.csv": "c06212b7-2cee-4a36-b3af-720ad29380f5",
    "knowledge_graph_triples.csv": "d87cacb6-24b2-44c6-a0c6-9666422a8996",
}
MAPPING = json.loads((Path(__file__).parent / "cvffad_fr.json").read_text(encoding="utf-8"))["faults"]
PREDICATES = {"表现为": "symptoms", "由...引起": "causes", "维修措施": "repairs"}


def collect(ctx: Context) -> Iterator[Record]:
    spec = SOURCES["cvffad"]
    paths = {name: download(BASE + fid + "/file_downloaded", RAW / "cvffad" / name, refresh=ctx.refresh, log=ctx.log)
             for name, fid in FILES.items()}

    counts: dict[str, int] = defaultdict(int)
    name_to_code: dict[str, str] = {}
    with paths["fault_events.csv"].open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            counts[row["fault_code"]] += 1
            name_to_code[row["fault_name"]] = row["fault_code"]

    kg: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    with paths["knowledge_graph_triples.csv"].open(encoding="utf-8-sig") as f:
        for t in csv.DictReader(f):
            key = PREDICATES.get(t["predicate"])
            if key and t["source"] == "fault_pattern":
                kg[t["subject"]][key].append(t["object"])

    n = 0
    for code, m in sorted(MAPPING.items()):
        if m.get("out_of_scope") or m["zh"] not in name_to_code:
            continue
        parts = kg.get(m["zh"], {})
        text = (f"{m['zh']}。表现为：{'；'.join(parts.get('symptoms', []))}。"
                f"原因：{'；'.join(parts.get('causes', []))}。维修措施：{'；'.join(parts.get('repairs', []))}。")
        cats = m.get("categories", [])
        yield Record(
            id=f"cvffad:{code}", source=spec.id, kind="fault_type", lang="zh", text=text,
            license=spec.license, attribution=spec.attribution, url="https://doi.org/10.17632/r98g7g6k5t.1",
            categories=cats, family=m.get("family") or family_of(cats[0] if cats else None), fault=m.get("fault"),
            label_quality="manual", synthetic=True,
            meta={"fault_code": code, "name_fr": m["fr"], "events": counts.get(code, 0),
                  "symptoms_zh": parts.get("symptoms", []), "causes_zh": parts.get("causes", []),
                  "repairs_zh": parts.get("repairs", [])},
        )
        n += 1
        if ctx.limit and n >= ctx.limit:
            return
