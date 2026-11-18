"""Import des lieux OpenStreetMap d'Oran en brouillons, et liste de visite pour le terrain (étape 4).

    cd backend
    python -m app.import_osm                       # data/raw/osm_oran.csv -> brouillons + data/terrain/liste_visite_osm.xlsx
    python -m app.import_osm --dry-run             # liste de visite seulement, base inchangée
    python -m app.import_osm --csv autre.csv --liste sortie.xlsx

- **Brouillons** : statut `draft`, source `osm`. Un brouillon n'est jamais recommandé aux automobilistes
  (RECOMMENDABLE_STATUSES) ; il le devient quand l'équipe le vérifie sur place (Admin > Magasins > Vérifier).
- **Rejouable** : fusion par identifiant OSM (puis par téléphone) ; une valeur saisie n'est jamais effacée.
- **Commune** : la commune dont le centre est le plus proche (au plus MAX_KM), à confirmer sur place.
- **Liste de visite** : une ligne par lieu, triée par commune, avec un lien vers la carte et des colonnes à remplir.
  Les en-têtes sont ceux que l'import du back-office comprend : une fois remplie, la liste se réimporte telle quelle
  (Admin > Import CSV) et complète les fiches (téléphone, marques, familles, origine des pièces…).

Licence : ODbL. Attribution « © les contributeurs d'OpenStreetMap » (data/SOURCES.md), rappelée dans la liste.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Commune, Shop
from .services.imports import import_shops

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = ROOT / "data" / "raw" / "osm_oran.csv"
DEFAULT_LIST = ROOT / "data" / "terrain" / "liste_visite_osm.xlsx"
MAX_KM = 15.0
TYPE_FR = {"pieces": "Pièces", "garage": "Garage", "pneus": "Pneus", "casse": "Casse"}
TYPE_ORDER = {"pieces": 0, "pneus": 1, "casse": 2, "garage": 3}
ATTRIBUTION = "© les contributeurs d'OpenStreetMap (ODbL), extraction du 17/11/2026"

# Colonnes de la liste : (en-tête, largeur). Les en-têtes en gras sont relus par l'import du back-office.
COLUMNS = [
    ("Commune", 16), ("Type", 9), ("Nom", 30), ("Adresse", 24), ("Téléphone", 14), ("Carte", 11), ("ID OSM", 18),
    ("Visité le", 11), ("Existe", 10), ("Marques", 22), ("Familles", 22), ("Origine des pièces", 18),
    ("Mode de vente", 13), ("Accepte DALIL", 13), ("Enquêteur", 12), ("Remarques", 30),
]
TO_FILL = {"Visité le", "Existe", "Marques", "Familles", "Origine des pièces", "Mode de vente", "Accepte DALIL",
           "Enquêteur", "Remarques"}


def km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def nearest_commune(lat: float | None, lng: float | None, communes: list[Commune]) -> tuple[Commune | None, float | None]:
    if lat is None or lng is None:
        return None, None
    best = min(((km(lat, lng, c.lat, c.lng), c) for c in communes if c.lat is not None and c.lng is not None),
               default=None, key=lambda x: x[0])
    if best is None or best[0] > MAX_KM:
        return None, None
    return best[1], round(best[0], 1)


def read_osm(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def prepare(db: Session, rows: list[dict]) -> list[dict]:
    """Lignes prêtes pour import_shops, avec la commune la plus proche."""
    communes = list(db.scalars(select(Commune).where(Commune.wilaya_code == "31")))
    out = []
    for r in rows:
        lat = float(r["lat"]) if r.get("lat") else None
        lng = float(r["lng"]) if r.get("lng") else None
        commune, dist = nearest_commune(lat, lng, communes)
        r = dict(r)
        if not r.get("phone") and re.fullmatch(r"[\s.+\d-]{9,}", r.get("address") or ""):
            r["phone"], r["address"] = r["address"].strip(), ""   # numéro saisi dans l'adresse sur OSM
        out.append({**r, "source": "osm", "commune": commune.nom_fr if commune else "", "_km": dist})
    return out


def write_visit_list(db: Session, rows: list[dict], path: Path, notes: list[dict] | None = None) -> int:
    remarks = {}
    for n in notes or []:
        for r in rows:
            if r["osm_id"] and r["osm_id"] + " fusionné" in n["note"]:
                remarks[r["osm_id"]] = "À vérifier : " + n["note"].split(" : ")[0]
    rows = sorted(rows, key=lambda r: (r["commune"] or "~", TYPE_ORDER.get(r["shop_type"], 9), r["name"]))
    wb = Workbook()
    ws = wb.active
    ws.title = "À visiter"
    ws.append([c for c, _ in COLUMNS])
    fill = PatternFill("solid", start_color="FFF2CC")
    for i, (name, width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=i)
        cell.font = Font(bold=True)
        if name in TO_FILL:
            cell.fill = fill
        ws.column_dimensions[cell.column_letter].width = width
    for r in rows:
        ws.append([r["commune"] or "", TYPE_FR.get(r["shop_type"], r["shop_type"]), r["name"],
                   r.get("address") or "", r.get("phone") or "", "Ouvrir", r["osm_id"]] + [""] * (len(TO_FILL) - 1)
                  + [remarks.get(r["osm_id"], "")])
        link = ws.cell(row=ws.max_row, column=6)
        link.hyperlink = f"https://www.openstreetmap.org/{r['osm_id']}"
        link.font = Font(color="0563C1", underline="single")
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions
    last = ws.max_row
    for col, values in (("I", "oui,non,déménagé,fermé"), ("L", "origine,adaptable,occasion,origine;adaptable"),
                        ("M", "detail,gros,les_deux"), ("N", "oui,non,à rappeler")):
        dv = DataValidation(type="list", formula1=f'"{values}"', allow_blank=True)
        dv.add(f"{col}2:{col}{last}")
        ws.add_data_validation(dv)

    info = wb.create_sheet("Lisez-moi")
    for line in [
        "Liste de visite des lieux OpenStreetMap d'Oran (magasins de pièces, pneus, garages).",
        ATTRIBUTION,
        "",
        "Sur place : remplir les colonnes jaunes. Le lien « Ouvrir » montre le lieu sur la carte.",
        "Existe : « non », « déménagé » ou « fermé » -> la fiche sera rejetée dans le back-office.",
        "Marques : marques de voitures servies, séparées par « ; » (ex. Renault; Peugeot; Dacia).",
        "Familles : familles de pièces vendues, séparées par « ; » (ex. freinage; filtration; batterie).",
        "Téléphone : le numéro du magasin (jamais un numéro personnel sans l'accord du gérant).",
        "",
        "Au retour : Admin > Import CSV (enregistrer en .xlsx ou .csv). Les fiches sont complétées (fusion par ID OSM) "
        "et restent en brouillon ; les vérifier une à une (Admin > Magasins) pour qu'elles soient recommandées.",
        "La commune proposée est la plus proche du point OpenStreetMap : la corriger si besoin ; vide = à préciser "
        "(écrire le nom exact d'une commune d'Oran, sinon la ligne est refusée à l'import).",
        "Commencer par les lignes « Pièces » : ce sont celles que DALIL recommande. Les garages servent aux essais "
        "(mécaniciens pour le jeu de test d'Oran, docs/essais-oran.md).",
    ]:
        info.append([line])
    info.column_dimensions["A"].width = 120
    for row in info.iter_rows():
        row[0].alignment = Alignment(wrap_text=True)
    info["A1"].font = Font(bold=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return len(rows)


def run(db: Session, csv_path: Path = DEFAULT_CSV, list_path: Path = DEFAULT_LIST, dry_run: bool = False) -> dict:
    rows = prepare(db, read_osm(csv_path))
    report = None
    if not dry_run:
        report = import_shops(db, [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows], default_source="osm")
        db.commit()
    n = write_visit_list(db, rows, list_path, report.notes if report else None)
    by_commune: dict[str, int] = {}
    for r in rows:
        by_commune[r["commune"] or "(à préciser)"] = by_commune.get(r["commune"] or "(à préciser)", 0) + 1
    return {"lieux": n, "crees": report.created if report else 0, "mis_a_jour": report.updated if report else 0,
            "erreurs": report.errors if report else [], "a_verifier": report.notes if report else [], "sans_commune": sum(1 for r in rows if not r["commune"]),
            "par_commune": dict(sorted(by_commune.items(), key=lambda x: -x[1])), "liste": str(list_path)}


def main() -> None:
    from .db import SessionLocal

    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--liste", default=str(DEFAULT_LIST))
    ap.add_argument("--dry-run", action="store_true", help="liste de visite seulement, base inchangée")
    args = ap.parse_args()
    with SessionLocal() as db:
        res = run(db, Path(args.csv), Path(args.liste), args.dry_run)
    for k, v in res.items():
        print(f"{k} : {v}")


if __name__ == "__main__":
    main()
