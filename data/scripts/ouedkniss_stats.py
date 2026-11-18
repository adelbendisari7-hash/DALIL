"""Statistiques agrégées par modèle à partir de la collecte Ouedkniss anonymisée (aucune annonce individuelle).

    python data/scripts/ouedkniss_stats.py ANNONCES_ANONYMISEES.jsonl [--sortie data/market/ouedkniss_modeles.json]

Pour chaque marque et modèle (noms harmonisés : « Clio5 », « clio 5 » -> « Clio 5 ») : nombre d'annonces, en Algérie et
dans la wilaya d'Oran, années (3e et 97e centiles, pour écarter les erreurs de saisie), et motorisations citées dans le
titre ou la description (« 1.5 dCi », « 1.6 HDi », « 2.0 TDI »…) avec leur carburant. Les champs « motorisation » et
« cylindrée » d'Ouedkniss sont presque toujours vides ou en texte libre (« moteur 10/10 ») : on lit le texte à la place.

Sert à prioriser et à compléter le référentiel véhicules (`data/scripts/build_vehicles.py`). Source et autorisation :
data/SOURCES.md. Rejouable.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIN_ANNONCES = 3  # un modèle cité moins de 3 fois n'est pas publié (agrégat trop fin, souvent une saisie libre)

BRAND_NAMES = {  # orthographe du référentiel DALIL
    "citroen": "Citroën", "mercedes-benz": "Mercedes", "mercedes benz": "Mercedes", "mercedes": "Mercedes", "mg": "MG",
    "bmw": "BMW", "dfsk": "DFSK", "baic": "BAIC", "gac": "GAC", "jac": "JAC", "byd": "BYD", "ds": "DS", "seat": "Seat",
    "skoda": "Skoda", "volkswagen": "Volkswagen", "land rover": "Land Rover", "alfa romeo": "Alfa Romeo",
    "great wall": "Great Wall", "ssangyong": "SsangYong", "kgm": "KGM",
}
SUFFIXES_TO_DROP = {"facelift", "restyle", "restylee", "restylée", "phase", "ph1", "ph2", "nouvelle", "new"}
BODY_WORDS = {"sedan", "hatchback", "break", "multispace", "long", "court", "berline", "sw", "estate"}

# Motorisation : cylindrée + code moteur. Le code donne aussi le carburant.
CODES = {
    "dci": ("dCi", "diesel"), "hdi": ("HDi", "diesel"), "bluehdi": ("BlueHDi", "diesel"), "ehdi": ("e-HDi", "diesel"),
    "tdi": ("TDI", "diesel"), "crdi": ("CRDi", "diesel"), "cdti": ("CDTi", "diesel"), "d4d": ("D-4D", "diesel"),
    "multijet": ("Multijet", "diesel"), "jtd": ("JTD", "diesel"), "tdci": ("TDCi", "diesel"), "cdi": ("CDI", "diesel"),
    "tsi": ("TSI", "essence"), "tfsi": ("TFSI", "essence"), "vvti": ("VVT-i", "essence"), "vti": ("VTi", "essence"),
    "thp": ("THP", "essence"), "puretech": ("PureTech", "essence"), "tce": ("TCe", "essence"), "sce": ("SCe", "essence"),
    "mpi": ("MPI", "essence"), "gdi": ("GDi", "essence"), "tgdi": ("T-GDi", "essence"), "ecoboost": ("EcoBoost", "essence"),
    "16v": ("16V", "essence"), "8v": ("8V", "essence"),
    # « Turbo » ou « T » seuls ne disent pas le carburant (une 1.9 Turbo est presque toujours diesel) : lu dans le texte
    "turbo": ("Turbo", "inconnu"), "t": ("T", "inconnu"),
}
ENGINE_RE = re.compile(r"(?<![\d.,])([0-6])[.,]([0-9])\s*l?\s*(blue\s*hdi|e[\s-]?hdi|t[\s-]?gdi|d[\s-]?4[\s-]?d|vvt[\s-]?i|"
                       r"dci|hdi|tdi|crdi|cdti|multijet|jtd|tdci|cdi|tsi|tfsi|vti|thp|pure\s*tech|tce|sce|mpi|gdi|"
                       r"ecoboost|16\s*v|8\s*v|turbo|t)(?![a-z0-9])", re.IGNORECASE)
FUEL_WORDS = [("diesel", "diesel"), ("gasoil", "diesel"), ("gazoil", "diesel"), ("essence", "essence"),
              ("gpl", "gpl"), ("sirghaz", "gpl"), ("hybride", "hybride"), ("hybrid", "hybride"), ("electrique", "electrique")]


def _plain(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def brand_name(raw: str) -> str:
    k = re.sub(r"\s+", " ", _plain(raw or "").strip())
    return BRAND_NAMES.get(k, (raw or "?").strip().title())


def model_key(raw: str) -> str:
    k = _plain(raw or "").strip()
    k = re.sub(r"([a-z])(\d)$", r"\1 \2", k)          # « clio5 » -> « clio 5 »
    k = re.sub(r"[\s_]+", " ", k).strip()
    # Carrosserie : même voiture pour le diagnostic (« Aveo 4 portes » = « Aveo 5 portes » = « Aveo »)
    k = re.sub(r"(?<![a-z0-9])[2-5] ?portes(?![a-z])", " ", k)
    words = [w for w in k.split() if w not in SUFFIXES_TO_DROP and w not in BODY_WORDS]
    return " ".join(words) or k


def engine_of(text: str) -> tuple[str, str] | None:
    m = ENGINE_RE.search(text or "")
    if not m:
        return None
    code = re.sub(r"[\s-]", "", m.group(3).lower())
    label, fuel = CODES.get(code, (m.group(3), "inconnu"))
    return f"{m.group(1)}.{m.group(2)} {label}", fuel


def fuel_of(row: dict, text: str) -> str | None:
    c = _plain(row.get("carburant") or "")
    for w, f in FUEL_WORDS:
        if w in c:
            return f
    t = _plain(text)
    for w, f in FUEL_WORDS:
        if re.search(rf"(?<![a-z]){w}(?![a-z])", t):
            return f
    return None


def pct(values: list[int], p: float) -> int | None:
    if not values:
        return None
    v = sorted(values)
    return v[min(len(v) - 1, max(0, round(p * (len(v) - 1))))]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("annonces", type=Path)
    ap.add_argument("--sortie", type=Path, default=ROOT / "data" / "market" / "ouedkniss_modeles.json")
    args = ap.parse_args(argv)

    spellings: dict[tuple[str, str], Counter] = defaultdict(Counter)
    years: dict[tuple[str, str], list[int]] = defaultdict(list)
    oran: Counter = Counter()
    engines: dict[tuple[str, str], Counter] = defaultdict(Counter)
    engine_years: dict[tuple[str, str, str, str], list[int]] = defaultdict(list)
    fuels: dict[tuple[str, str], Counter] = defaultdict(Counter)
    total = 0
    with args.annonces.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if not r.get("brand") or not r.get("model"):
                continue
            total += 1
            key = (brand_name(r["brand"]), model_key(r["model"]))
            spellings[key][re.sub(r"\s+", " ", r["model"].strip())] += 1
            y = r.get("year")
            year = int(y) if str(y or "").isdigit() and 1950 <= int(y) <= 2027 else None
            if year:
                years[key].append(year)
            if "oran" in _plain(f"{r.get('region') or ''} {r.get('city') or ''}"):
                oran[key] += 1
            text = f"{r.get('title') or ''} {r.get('version_trim') or ''} {r.get('description') or ''}"
            eng = engine_of(text)
            fuel = fuel_of(r, text)
            if eng:
                label, efuel = eng
                efuel = efuel if efuel != "inconnu" else (fuel or "inconnu")
                engines[key][(label, efuel)] += 1
                if year:
                    engine_years[(*key, label, efuel)].append(year)
            if fuel:
                fuels[key][fuel] += 1

    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    from anonymiser_ouedkniss import scrub  # défense en profondeur : aucun numéro dans un nom de modèle

    models = []
    dropped = Counter()
    for key, sp in spellings.items():
        n = sum(sp.values())
        if n < MIN_ANNONCES:
            dropped["moins de 3 annonces"] += 1
            continue
        if scrub(key[1], Counter()) != key[1] or scrub(sp.most_common(1)[0][0], Counter()) != sp.most_common(1)[0][0]:
            dropped["numéro ou adresse dans le nom"] += 1
            continue
        ys = years[key]
        eng = []
        for (label, fuel), c in engines[key].most_common(12):
            ey = engine_years[(*key, label, fuel)]
            eng.append({"engine": label, "fuel": fuel, "n": c, "year_p10": pct(ey, 0.10), "year_p90": pct(ey, 0.90)})
        models.append({
            "brand": key[0], "model_key": key[1], "model": sp.most_common(1)[0][0], "n": n, "n_oran": oran[key],
            "year_p03": pct(ys, 0.03), "year_p50": pct(ys, 0.50), "year_p97": pct(ys, 0.97),
            "fuels": dict(fuels[key].most_common()), "engines": eng,
        })
    models.sort(key=lambda m: -m["n"])
    out = {
        "_source": "Collecte Ouedkniss de l'utilisateur, anonymisée (data/scripts/anonymiser_ouedkniss.py) ; agrégats seulement",
        "_licence": "Autorisation déclarée par l'utilisateur, confirmation écrite à obtenir (data/SOURCES.md)",
        "_annonces": total, "_min_annonces": MIN_ANNONCES, "_ecartes": dict(dropped), "modeles": models,
    }
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{total} annonces -> {len(models)} modèles ; {sum(1 for m in models if m['n'] >= 100)} avec au moins 100 annonces")
    print(f"écrit : {args.sortie}")


if __name__ == "__main__":
    main()
