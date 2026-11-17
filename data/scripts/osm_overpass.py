"""Liste de départ des magasins d'Oran depuis OpenStreetMap (API Overpass), étape 4.

    python data/scripts/osm_overpass.py                 # écrit data/raw/osm_oran.csv
    python data/scripts/osm_overpass.py --out x.csv

Le CSV produit s'importe tel quel dans le back-office (Admin > Import CSV, source = osm).
Les fiches arrivent en brouillon : elles servent de liste de visite, pas de base validée.
Licence : ODbL (attribution « © les contributeurs d'OpenStreetMap »). Voir data/SOURCES.md.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import httpx

OVERPASS = "https://overpass-api.de/api/interpreter"
# Wilaya d'Oran : relation administrative de niveau 4 ; repli sur une emprise si l'aire n'est pas trouvée.
QUERY = """
[out:json][timeout:90];
area["name:fr"="Oran"]["admin_level"="4"]->.w;
(
  nwr["shop"~"^(car_parts|car_repair|tyres)$"](area.w);
);
out center tags;
"""
BBOX_QUERY = """
[out:json][timeout:90];
(
  nwr["shop"~"^(car_parts|car_repair|tyres)$"](35.45,-1.05,35.95,-0.10);
);
out center tags;
"""
TYPE_MAP = {"car_parts": "pieces", "car_repair": "garage", "tyres": "pneus"}


# Serveurs publics de l'API Overpass (mêmes données OpenStreetMap) : le principal est souvent surchargé (502, 504).
MIRRORS = [OVERPASS, "https://overpass.kumi.systems/api/interpreter", "https://overpass.private.coffee/api/interpreter"]


def fetch(query: str) -> list[dict]:
    last: Exception | None = None
    for url in MIRRORS:
        try:
            r = httpx.post(url, data={"data": query}, timeout=120, headers={"User-Agent": "dalil-prototype/0.1"})
            r.raise_for_status()
            return r.json().get("elements", [])
        except (httpx.HTTPError, ValueError) as e:  # serveur surchargé ou réponse illisible : miroir suivant
            print(f"{url} indisponible ({e.__class__.__name__}), essai du serveur suivant")
            last = e
    raise SystemExit(f"Aucun serveur Overpass n'a répondu ({last}) ; réessayer plus tard.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "raw" / "osm_oran.csv"))
    args = ap.parse_args()
    elements = fetch(QUERY) or fetch(BBOX_QUERY)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["name", "phone", "lat", "lng", "address", "hours", "shop_type", "source", "osm_id"])
        for e in elements:
            tags = e.get("tags", {})
            lat = e.get("lat") or e.get("center", {}).get("lat")
            lng = e.get("lon") or e.get("center", {}).get("lon")
            kind = TYPE_MAP.get(tags.get("shop"), "pieces")
            counts[kind] = counts.get(kind, 0) + 1
            name = tags.get("name:fr") or tags.get("name") or f"Sans nom (OSM {e['type']}/{e['id']})"
            phone = (tags.get("phone") or tags.get("contact:phone") or "").split(";")[0]
            addr = " ".join(x for x in (tags.get("addr:housenumber"), tags.get("addr:street"), tags.get("addr:city")) if x)
            w.writerow([name, phone, lat, lng, addr, tags.get("opening_hours", ""), kind, "osm", f"{e['type']}/{e['id']}"])
    print(f"{len(elements)} éléments écrits dans {out} : {counts}")
    print("Mesure de couverture à reporter dans le mémoire (section 4) : comparer ce nombre au comptage terrain.")


if __name__ == "__main__":
    main()
