"""NHTSA : plaintes (récits de pannes) et rappels, par véhicule, via l'API publique api.nhtsa.gov.

Les réponses brutes sont gardées dans data/raw/nhtsa/ : rejouer ne réinterroge pas l'API.
"""
from __future__ import annotations

import json
import time
from collections.abc import Iterator
from pathlib import Path

from ..common import RAW, Record, client, get_json
from ..taxonomy_map import categories_en, fault_for, nhtsa_family, reconcile
from . import SOURCES, Context

API = "https://api.nhtsa.gov"
VEHICLES = json.loads((Path(__file__).parent / "nhtsa_vehicles.json").read_text(encoding="utf-8"))["vehicles"]


def _fetch(kind: str, v: dict, year: int, ctx: Context) -> list[dict]:
    path = RAW / "nhtsa" / kind / f"{v['make']}_{v['model']}_{year}.json".replace(" ", "_")
    if path.exists() and not ctx.refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    endpoint = "/complaints/complaintsByVehicle" if kind == "complaints" else "/recalls/recallsByVehicle"
    with client() as c:
        data = get_json(c, API + endpoint, {"make": v["make"], "model": v["model"], "modelYear": year})
    rows = data.get("results", [])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    time.sleep(0.3)  # politesse envers l'API publique
    return rows


def _vehicle(v: dict, year: int) -> dict:
    return {"make": v["make"].title(), "model": v["model"].title(), "year": year,
            "dalil_brand": v["dalil_brand"], "dalil_model": v["dalil_model"]}


def collect_complaints(ctx: Context) -> Iterator[Record]:
    spec = SOURCES["nhtsa_complaints"]
    seen: set[int] = set()
    n = 0
    for v in VEHICLES:
        for year in range(v["years"][0], v["years"][1] + 1):
            rows = _fetch("complaints", v, year, ctx)
            ctx.log(f"  {v['make']} {v['model']} {year} : {len(rows)} plaintes")
            for row in rows:
                odi = row.get("odiNumber")
                text = (row.get("summary") or "").strip()
                if not odi or odi in seen or len(text) < 40:
                    continue
                seen.add(odi)
                cats, fam, quality = reconcile(categories_en(text), nhtsa_family(row.get("components", "")))
                yield Record(
                    id=f"nhtsa_complaints:{odi}", source=spec.id, kind="complaint", lang="en", text=text,
                    license=spec.license, attribution=spec.attribution,
                    url=f"https://www.nhtsa.gov/vehicle/{year}/{v['make']}/{v['model']}".replace(" ", "%20"),
                    vehicle=_vehicle(v, year), categories=cats, family=fam,
                    fault=fault_for(cats, quality) if quality == "keyword+component" else None, label_quality=quality,
                    meta={"odi": odi, "components": row.get("components"), "crash": row.get("crash"),
                          "fire": row.get("fire"), "date": row.get("dateComplaintFiled")},
                )
                n += 1
                if ctx.limit and n >= ctx.limit:
                    return


def collect_recalls(ctx: Context) -> Iterator[Record]:
    spec = SOURCES["nhtsa_recalls"]
    by_campaign: dict[str, Record] = {}
    for v in VEHICLES:
        for year in range(v["years"][0], v["years"][1] + 1):
            for row in _fetch("recalls", v, year, ctx):
                camp = row.get("NHTSACampaignNumber")
                if not camp:
                    continue
                if camp in by_campaign:  # une campagne couvre plusieurs années : on garde les années
                    by_campaign[camp].meta["years"].append(year)
                    continue
                text = " ".join(x for x in (row.get("Summary"), row.get("Consequence"), row.get("Remedy")) if x).strip()
                cats, fam, quality = reconcile(categories_en(row.get("Component", "") + " " + text), nhtsa_family(row.get("Component", "")))
                by_campaign[camp] = Record(
                    id=f"nhtsa_recalls:{camp}", source=spec.id, kind="recall", lang="en", text=text,
                    license=spec.license, attribution=spec.attribution,
                    url=f"https://www.nhtsa.gov/recalls?nhtsaId={camp}", vehicle=_vehicle(v, year),
                    categories=cats, family=fam, fault=None, label_quality=quality,
                    meta={"campaign": camp, "component": row.get("Component"), "years": [year]},
                )
    records = list(by_campaign.values())
    yield from records[: ctx.limit] if ctx.limit else records
