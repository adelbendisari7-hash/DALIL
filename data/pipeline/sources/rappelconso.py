"""RappelConso : rappels de véhicules publiés par la DGCCRF, déjà en français.

Export complet de la rubrique « automobiles, motos, scooters » via l'API Opendatasoft.
"""
from __future__ import annotations

import json
from collections.abc import Iterator

from ..common import RAW, Record, download
from ..taxonomy_map import categories_fr, family_fr, reconcile
from . import SOURCES, Context

EXPORT = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/rappelconso-v2-gtin-espaces/exports/json"
    "?where=sous_categorie_produit%3D%22automobiles%2C%20motos%2C%20scooters%22"
)


def collect(ctx: Context) -> Iterator[Record]:
    spec = SOURCES["rappelconso"]
    path = download(EXPORT, RAW / "rappelconso" / "rappels_auto.json", refresh=ctx.refresh, log=ctx.log)
    rows = json.loads(path.read_text(encoding="utf-8"))
    ctx.log(f"  {len(rows)} fiches de rappel")
    seen: set[str] = set()
    n = 0
    for row in rows:
        guid = row.get("rappel_guid") or str(row.get("id"))
        motif = (row.get("motif_rappel") or "").strip()
        if not motif or guid in seen:
            continue
        seen.add(guid)
        marque = (row.get("marque_produit") or "").strip()
        modeles = (row.get("modeles_ou_references") or row.get("libelle") or "").strip()
        risques = (row.get("risques_encourus") or "").strip()
        text = f"Rappel {marque} {modeles} : {motif}" + (f" Risque : {risques}." if risques else "")
        cats, fam, quality = reconcile(categories_fr(motif), family_fr(motif))
        yield Record(
            id=f"rappelconso:{guid}", source=spec.id, kind="recall", lang="fr", text=text,
            license=spec.license, attribution=spec.attribution, url=row.get("lien_vers_la_fiche_rappel"),
            vehicle={"make": marque.title(), "model": modeles[:120], "year": None, "dalil_brand": None, "dalil_model": None},
            categories=cats, family=fam, fault=None, label_quality=quality,
            meta={"date": row.get("date_publication"), "risques": risques, "fiche": row.get("numero_fiche")},
        )
        n += 1
        if ctx.limit and n >= ctx.limit:
            return
