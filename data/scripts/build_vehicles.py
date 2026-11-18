"""Complète le référentiel véhicules (data/seed/vehicles.json) à partir des statistiques de marché.

    python data/scripts/build_vehicles.py [--stats data/market/ouedkniss_modeles.json] [--seuil 100]

- Les marques, modèles et motorisations déjà présents ne sont jamais modifiés ni retirés : leurs identifiants en base
  servent aux produits des magasins, aux compatibilités et aux tests (mise à jour en place par `python -m app.seed`).
- Ajoute chaque modèle d'au moins `--seuil` annonces Ouedkniss, et les modèles de COMPLEMENTS (utilitaires et modèles
  anciens comptés par l'ONS mais absents de la collecte, qui ne couvre que la catégorie « Voitures »).
- Motorisations d'un nouveau modèle : celles citées dans au moins 5 annonces (et 5 % des motorisations citées), avec les
  années observées (10e et 90e centiles), plus « Autre motorisation » sur toute la période du modèle.
- Chaque ajout porte `source` et `a_verifier: true` (à confirmer par les magasins enquêtés, docs/essais-oran.md).

Rejouable : relancé, il ajoute seulement ce qui manque.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "data" / "seed" / "vehicles.json"
LAST_YEAR = 2026  # au-delà, le modèle est considéré comme encore produit (year_to = null)

COUNTRY = {
    "Renault": "France", "Peugeot": "France", "Citroën": "France", "DS": "France", "Dacia": "Roumanie",
    "Volkswagen": "Allemagne", "Audi": "Allemagne", "BMW": "Allemagne", "Mercedes": "Allemagne", "Opel": "Allemagne",
    "Porsche": "Allemagne", "Seat": "Espagne", "Cupra": "Espagne", "Skoda": "République tchèque", "Fiat": "Italie",
    "Alfa Romeo": "Italie", "Toyota": "Japon", "Nissan": "Japon", "Mazda": "Japon", "Mitsubishi": "Japon",
    "Suzuki": "Japon", "Honda": "Japon", "Isuzu": "Japon", "Daihatsu": "Japon", "Hyundai": "Corée du Sud",
    "Kia": "Corée du Sud", "Daewoo": "Corée du Sud", "SsangYong": "Corée du Sud", "Chevrolet": "États-Unis",
    "Ford": "États-Unis", "Land Rover": "Royaume-Uni", "Lada": "Russie", "Geely": "Chine", "Chery": "Chine",
    "Livan": "Chine", "MG": "Chine", "Jetour": "Chine", "GAC": "Chine", "Great Wall": "Chine", "Kaiyi": "Chine",
    "Changan": "Chine", "Jetta": "Chine", "Lifan": "Chine", "Roewe": "Chine", "Zotye": "Chine", "DFSK": "Chine",
    "JAC": "Chine", "BAIC": "Chine", "BYD": "Chine", "Haval": "Chine",
}

# Utilitaires et modèles anciens courants en Algérie (ONS 2020 : 18 % de camionnettes ; Mazda et Isuzu surtout en
# utilitaires) que la collecte « Voitures » ne contient pas ou peu. Années et carburant approximatifs : à vérifier.
COMPLEMENTS = [
    ("Peugeot", "Partner", 1996, None, "diesel"), ("Peugeot", "Expert", 1995, None, "diesel"),
    ("Peugeot", "Boxer", 1994, None, "diesel"), ("Peugeot", "J5", 1981, 1994, "diesel"),
    ("Peugeot", "504", 1968, 1990, None), ("Peugeot", "404", 1960, 1975, None),
    ("Renault", "Express", 1985, 2000, None), ("Renault", "Trafic", 1980, None, "diesel"),
    ("Renault", "Master", 1980, None, "diesel"), ("Renault", "R4", 1961, 1992, "essence"),
    ("Toyota", "Hiace", 1989, None, "diesel"), ("Hyundai", "H-100", 1993, None, "diesel"),
    ("Hyundai", "H-1", 1997, None, "diesel"), ("Kia", "K2700", 1997, None, "diesel"),
    ("Mazda", "B2500", 1985, 2006, "diesel"), ("Mazda", "BT-50", 2006, None, "diesel"), ("Mazda", "323", 1985, 2003, "essence"),
    ("Isuzu", "D-Max", 2002, None, "diesel"), ("Mitsubishi", "Pajero", 1982, None, None),
    ("Fiat", "Ducato", 1981, None, "diesel"), ("Fiat", "Doblo Cargo", 2001, None, "diesel"),
    ("Citroën", "Jumper", 1994, None, "diesel"), ("Mercedes", "Sprinter", 1995, None, "diesel"),
    ("Lada", "Niva", 1977, None, "essence"), ("Toyota", "Land Cruiser", 1980, None, "diesel"),
    ("Honda", "Civic", 1980, None, "essence"), ("Honda", "Accord", 1985, None, "essence"),
]


TYPOS = {"tahru": "Tharu", "santafe": "Santa Fe", "c elysee": "C-Élysée", "x trail": "X-Trail"}


def clean_name(name: str, brand: str = "") -> str:
    """Nom affiché : sans la carrosserie (« Aveo 4 portes » -> « Aveo »), majuscules harmonisées (« ATECA » -> « Ateca »,
    « GX3 PRO » -> « GX3 Pro »), Renault numérotées en « R4 », « R19 », fautes de frappe courantes corrigées."""
    n = re.sub(r"(?<![\w])[2-5] ?portes(?!\w)", " ", name, flags=re.IGNORECASE)
    n = re.sub(r"(?<![\w])(sedan|hatchback|break|multispace|long|court|berline|facelift)(?!\w)", " ", n, flags=re.IGNORECASE)
    n = re.sub(r"\s+", " ", n).strip()
    if n.lower() in TYPOS:
        return TYPOS[n.lower()]
    n = " ".join(w.capitalize() if w.isalpha() and w.isupper() and (len(w) >= 4 or w == "PRO") else w for w in n.split())
    if brand == "Renault" and re.fullmatch(r"\d{1,2}", n):
        n = f"R{n}"
    return n


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def variants_for(m: dict) -> list[dict]:
    y0 = m.get("year_p03") or m.get("year_p50") or 2000
    y1 = m.get("year_p97")
    y1 = None if y1 is None or y1 >= LAST_YEAR - 1 else y1
    src = f"ouedkniss:{m['n']} annonces"
    cited = sum(e["n"] for e in m.get("engines", []))
    out, seen = [], set()
    for e in m.get("engines", []):
        if e["n"] < 5 or (cited and e["n"] < 0.05 * cited) or e["fuel"] == "inconnu" or e["engine"] in seen:
            continue
        seen.add(e["engine"])
        ef, et = e.get("year_p10") or y0, e.get("year_p90")
        et = None if et is None or et >= LAST_YEAR - 1 else et
        out.append({"year_from": max(ef, y0), "year_to": et, "engine": e["engine"], "fuel": e["fuel"],
                    "source": src, "a_verifier": True})
    fuels = m.get("fuels") or {}
    tot = sum(fuels.values())
    main_fuel = max(fuels, key=fuels.get) if tot and max(fuels.values()) >= 0.7 * tot else "inconnu"
    out.append({"year_from": y0, "year_to": y1, "engine": "Autre motorisation", "fuel": main_fuel if not out else "inconnu",
                "source": src, "a_verifier": True})
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stats", type=Path, default=ROOT / "data" / "market" / "ouedkniss_modeles.json")
    ap.add_argument("--seuil", type=int, default=100)
    args = ap.parse_args(argv)

    data = json.loads(SEED.read_text(encoding="utf-8"))
    brands = {b["name"]: b for b in data["brands"]}
    existing = {(b["name"], norm(m["name"])) for b in data["brands"] for m in b["models"]}
    stats = json.loads(args.stats.read_text(encoding="utf-8"))["modeles"]
    by_key: dict[tuple[str, str], dict] = {}
    for m in stats:  # plusieurs graphies peuvent donner le même nom : on garde la plus fréquente
        k = (m["brand"], norm(clean_name(m["model"], m["brand"])))
        if k not in by_key or m["n"] > by_key[k]["n"]:
            by_key[k] = m
    brand_volume: dict[str, int] = {}
    for m in stats:
        brand_volume[m["brand"]] = brand_volume.get(m["brand"], 0) + m["n"]

    def brand(name: str) -> dict:
        if name not in brands:
            b = {"name": name, "country": COUNTRY.get(name), "priority": 0, "models": [], "source": "ouedkniss+ons"}
            brands[name] = b
            data["brands"].append(b)
        return brands[name]

    added = 0
    for m in stats:
        if m["n"] < args.seuil:
            continue
        name = clean_name(m["model"], m["brand"])
        if (m["brand"], norm(name)) in existing or not name:
            continue
        brand(m["brand"])["models"].append({"name": name, "source": f"ouedkniss:{m['n']} annonces ({m['n_oran']} à Oran)",
                                            "variants": variants_for(m)})
        existing.add((m["brand"], norm(name)))
        added += 1
    for bname, mname, y0, y1, fuel in COMPLEMENTS:
        if (bname, norm(mname)) in existing:
            continue
        st = by_key.get((bname, norm(mname)))
        variants = variants_for(st) if st else [{"year_from": y0, "year_to": y1, "engine": "Autre motorisation",
                                                 "fuel": fuel or "inconnu", "source": "equipe (ONS 2020 : marque)",
                                                 "a_verifier": True}]
        brand(bname)["models"].append({"name": mname, "source": "equipe (utilitaire ou modèle ancien, ONS 2020)",
                                       "variants": variants})
        existing.add((bname, norm(mname)))
        added += 1

    # Ordre d'affichage : priorité = volume d'annonces (les marques déjà présentes gardent au moins leur priorité)
    for b in data["brands"]:
        b["priority"] = max(b.get("priority", 0), round(brand_volume.get(b["name"], 0) / 1000))
        for mm in b["models"]:  # priorité d'affichage du modèle (colonne models.priority) = nombre d'annonces
            mm["priority"] = by_key.get((b["name"], norm(mm["name"])), {}).get("n", 0)
        b["models"].sort(key=lambda mm: (-mm["priority"], mm["name"]))
    data["brands"].sort(key=lambda bb: (-bb["priority"], bb["name"]))
    data["_note"] = ("Référentiel : modèles initiaux de l'équipe, complétés le 18/11/2026 par les modèles d'au moins "
                     f"{args.seuil} annonces Ouedkniss (data/market/ouedkniss_modeles.json) et des utilitaires et modèles "
                     "anciens de l'ONS. Les entrées « a_verifier » sont à confirmer par les magasins enquêtés.")
    SEED.write_text(_dump(data), encoding="utf-8")
    nb_models = sum(len(b["models"]) for b in data["brands"])
    nb_vars = sum(len(m["variants"]) for b in data["brands"] for m in b["models"])
    print(f"{added} modèles ajoutés ; référentiel : {len(data['brands'])} marques, {nb_models} modèles, {nb_vars} motorisations")


def _dump(data: dict) -> str:
    """Une motorisation par ligne : le fichier reste lisible et les différences git restent courtes."""
    lines = ["{", f'  "_note": {json.dumps(data["_note"], ensure_ascii=False)},', '  "brands": [']
    for i, b in enumerate(data["brands"]):
        head = {k: v for k, v in b.items() if k != "models"}
        lines.append("    " + json.dumps(head, ensure_ascii=False)[:-1] + ', "models": [')
        for j, m in enumerate(b["models"]):
            mh = {k: v for k, v in m.items() if k != "variants"}
            lines.append("      " + json.dumps(mh, ensure_ascii=False)[:-1] + ', "variants": [')
            for k, v in enumerate(m["variants"]):
                lines.append("        " + json.dumps(v, ensure_ascii=False) + ("," if k < len(m["variants"]) - 1 else ""))
            lines.append("      ]}" + ("," if j < len(b["models"]) - 1 else ""))
        lines.append("    ]}" + ("," if i < len(data["brands"]) - 1 else ""))
    lines += ["  ]", "}", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
