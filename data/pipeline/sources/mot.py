"""DVSA MOT (contrôle technique britannique, OGL v3) : quelle pièce lâche, sur quel modèle, à quel kilométrage.

Données codées, sans texte libre (section 5). Le module :
1. lit en flux test_result.csv (3,7 Go, Deflate64) sans le stocker, garde les contrôles des véhicules
   particuliers (classe 4, contrôle normal) des modèles cibles ;
2. lit en flux test_item.csv et compte, par modèle et tranche de kilométrage, les contrôles ayant
   au moins un défaut d'échec (codes F et P) dans chaque famille de pièces DALIL ;
3. écrit un agrégat (data/raw/mot/agg_<année>.csv, cache), un tableau de taux
   (data/processed/priors/mot_<année>.csv) et une fiche en français par modèle pour la base de connaissances.
"""
from __future__ import annotations

import csv
import io
import re
from collections.abc import Iterator

import numpy as np

from ..common import PROCESSED, RAW, Record, ZipMemberStream, download
from ..taxonomy_map import categories_en, family_of, taxonomy
from . import SOURCES, Context

S3 = "https://edh-dvsa-data-gov-uk-files-prod.s3.eu-west-1.amazonaws.com/"
YEAR_FILES = {2023: ("dft_test_result_2023.zip", "dft_test_item_2023.zip"),
              2022: ("dft_test_result_2022.zip", "dft_test_item_2022.zip")}

# (marque MOT, premier mot du modèle MOT) -> (marque DALIL, modèle DALIL)
TARGETS = {
    ("DACIA", "SANDERO"): ("Dacia", "Sandero"), ("DACIA", "DUSTER"): ("Dacia", "Duster"),
    ("DACIA", "LOGAN"): ("Dacia", "Logan"), ("RENAULT", "CLIO"): ("Renault", "Clio"),
    ("RENAULT", "KANGOO"): ("Renault", "Kangoo"), ("HYUNDAI", "I10"): ("Hyundai", "i10"),
    ("KIA", "PICANTO"): ("Kia", "Picanto"), ("KIA", "RIO"): ("Kia", "Rio"),
    ("PEUGEOT", "206"): ("Peugeot", "206"), ("PEUGEOT", "208"): ("Peugeot", "208"),
    ("FIAT", "500"): ("Fiat", "500"), ("FIAT", "TIPO"): ("Fiat", "Tipo"), ("FIAT", "DOBLO"): ("Fiat", "Doblo"),
    ("VOLKSWAGEN", "GOLF"): ("Volkswagen", "Golf"), ("VOLKSWAGEN", "POLO"): ("Volkswagen", "Polo"),
    ("SKODA", "OCTAVIA"): ("Skoda", "Octavia"), ("TOYOTA", "HILUX"): ("Toyota", "Hilux"),
    ("VAUXHALL", "CORSA"): ("Opel", "Corsa"), ("MG", "MG5"): ("MG", "MG5"),
}
MODEL_KEYS = list(TARGETS)
# Tranches en miles (relevés britanniques), affichées en km.
BANDS = [(0, 60_000, "moins de 100 000 km"), (60_000, 100_000, "100 000 à 160 000 km"), (100_000, 10**9, "plus de 160 000 km")]
FAMILY_HINTS_EN = [("ampoules", r"\blamps?\b|indicators?|hazard warning|lighting"),
                   ("freinage", r"\bbrak"), ("direction", r"steering"), ("suspension", r"suspension"),
                   ("echappement", r"exhaust"), ("electricite", r"wiring|electrical|battery"),
                   ("train-roulant", r"wheel|hub")]


def _band(miles: np.ndarray) -> np.ndarray:
    out = np.zeros(len(miles), dtype=np.int8)
    for i, (lo, _hi, _) in enumerate(BANDS):
        out[miles >= lo] = i
    return out


def rfr_categories(ctx: Context) -> dict[int, str]:
    """rfr_id (motif de défaut, véhicules particuliers) -> sous-famille ou famille DALIL."""
    det = download(S3 + "dft_item_detail_extract.csv", RAW / "mot" / "dft_item_detail_extract.csv", ctx.refresh, ctx.log)
    grp = download(S3 + "dft_item_group_extract.csv", RAW / "mot" / "dft_item_group_extract.csv", ctx.refresh, ctx.log)
    groups = {}
    with grp.open(encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r["test_class_id"] == "4":
                groups[r["test_item_id"]] = (r["item_name"], r["parent_id"])
    out: dict[int, str] = {}
    with det.open(encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r["test_class_id"] != "4":
                continue
            names, node, guard = [], r["test_item_id"], 0
            while node in groups and node != "0" and guard < 6:  # remonte la hiérarchie pour le contexte
                names.append(groups[node][0])
                node, guard = groups[node][1], guard + 1
            text = " ".join(names) + " " + r["rfr_desc"] + " " + r["rfr_insp_manual_desc"]
            cats = categories_en(" ".join(names[:2]) + " " + r["rfr_insp_manual_desc"]) or categories_en(text)
            if cats:
                out[int(r["rfr_id"])] = cats[0]
                continue
            low = text.lower()
            fam = next((f for f, rx in FAMILY_HINTS_EN if re.search(rx, low)), None)
            if fam:
                out[int(r["rfr_id"])] = fam
    return out


def aggregate(year: int, ctx: Context) -> list[dict]:
    cache = RAW / "mot" / f"agg_{year}.csv"
    if cache.exists() and not ctx.refresh:
        with cache.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))
    import pandas as pd

    res_file, item_file = YEAR_FILES[year]
    index = {f"{mk}|{md}": i for i, (mk, md) in enumerate(MODEL_KEYS)}
    makes = {mk for mk, _ in MODEL_KEYS}
    ids, idxs, bands = [], [], []
    tests = np.zeros((len(MODEL_KEYS), len(BANDS)), dtype=np.int64)

    ctx.log(f"  lecture en flux de {res_file} (≈3,7 Go décompressés)…")
    stream = io.BufferedReader(ZipMemberStream(S3 + res_file), buffer_size=1 << 22)
    reader = pd.read_csv(stream, sep="|", usecols=["test_id", "test_class_id", "test_type", "test_mileage", "make", "model"],
                         dtype=str, chunksize=1_000_000, on_bad_lines="skip")
    for i, chunk in enumerate(reader):
        c = chunk[(chunk.test_class_id == "4") & (chunk.test_type == "NT") & chunk.make.isin(makes)]
        if c.empty:
            continue
        key = c.make + "|" + c.model.fillna("").str.split(" ", n=1).str[0]
        idx = key.map(index)
        c, idx = c[idx.notna()], idx[idx.notna()].astype(np.int16).to_numpy()
        miles = pd.to_numeric(c.test_mileage, errors="coerce").fillna(-1).to_numpy()
        keep = miles >= 0
        b = _band(miles[keep])
        ids.append(pd.to_numeric(c.test_id, errors="coerce").to_numpy()[keep].astype(np.int64))
        idxs.append(idx[keep])
        bands.append(b)
        np.add.at(tests, (idx[keep], b), 1)
        if i % 10 == 0:
            ctx.log(f"    {(i + 1)} M lignes lues, {int(tests.sum()):,} contrôles retenus")
        if ctx.limit and tests.sum() >= ctx.limit * 1000:
            break
    stream.close()
    test_ids = np.concatenate(ids)
    order = np.argsort(test_ids)
    test_ids, model_of, band_of = test_ids[order], np.concatenate(idxs)[order], np.concatenate(bands)[order]

    rfr_cat = rfr_categories(ctx)
    cat_names = sorted(set(rfr_cat.values()))
    cat_index = {c: i for i, c in enumerate(cat_names)}
    rfr_ids = np.array(sorted(rfr_cat), dtype=np.int64)
    rfr_to_cat = np.array([cat_index[rfr_cat[r]] for r in rfr_ids], dtype=np.int32)
    defects = np.zeros((len(MODEL_KEYS), len(BANDS), len(cat_names)), dtype=np.int64)

    ctx.log(f"  lecture en flux de {item_file}…")
    stream = io.BufferedReader(ZipMemberStream(S3 + item_file), buffer_size=1 << 22)
    reader = pd.read_csv(stream, sep="|", usecols=["test_id", "rfr_id", "rfr_type_code"],
                         dtype={"test_id": "Int64", "rfr_id": "Int64", "rfr_type_code": str}, chunksize=2_000_000,
                         on_bad_lines="skip")
    for i, chunk in enumerate(reader):
        c = chunk[chunk.rfr_type_code.isin(["F", "P"])].dropna(subset=["test_id", "rfr_id"])
        t = c.test_id.to_numpy(dtype=np.int64)
        pos = np.searchsorted(test_ids, t)
        pos[pos >= len(test_ids)] = 0
        hit = test_ids[pos] == t
        r = c.rfr_id.to_numpy(dtype=np.int64)[hit]
        rpos = np.searchsorted(rfr_ids, r)
        rpos[rpos >= len(rfr_ids)] = 0
        rhit = rfr_ids[rpos] == r
        frame = pd.DataFrame({"test": t[hit][rhit], "cat": rfr_to_cat[rpos[rhit]], "pos": pos[hit][rhit]})
        frame = frame.drop_duplicates(["test", "cat"])  # un contrôle compte une fois par famille
        np.add.at(defects, (model_of[frame.pos], band_of[frame.pos], frame.cat.to_numpy()), 1)
        if i % 10 == 0:
            ctx.log(f"    {(i + 1) * 2} M lignes de défauts lues")
    stream.close()

    rows = []
    for m, (mk, md) in enumerate(MODEL_KEYS):
        for b in range(len(BANDS)):
            for k, cat in enumerate(cat_names):
                rows.append({"make": mk, "model": md, "band": b, "tests": int(tests[m, b]),
                             "category": cat, "failed_tests": int(defects[m, b, k])})
    cache.parent.mkdir(parents=True, exist_ok=True)
    with cache.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rows


def _n(x: int) -> str:
    return f"{x:,}".replace(",", " ")


def _pct(x: float) -> str:
    return f"{x * 100:.1f} %".replace(".", ",")


def collect(ctx: Context) -> Iterator[Record]:
    spec = SOURCES["mot_uk"]
    year = int(ctx.options.get("mot_year", 2023))
    rows = aggregate(year, ctx)
    names = taxonomy()["names"]
    priors = PROCESSED / "priors" / f"mot_{year}.csv"
    priors.parent.mkdir(parents=True, exist_ok=True)
    out_rows = []
    by_model: dict[tuple, list[dict]] = {}
    for r in rows:
        by_model.setdefault((r["make"], r["model"]), []).append(r)
    for (mk, md), rs in by_model.items():
        brand, model = TARGETS[(mk, md)]
        tests_band = {}
        for r in rs:
            tests_band[int(r["band"])] = int(r["tests"])
        total = sum(tests_band.values())
        if total < 500:  # trop peu de contrôles pour un taux fiable
            continue
        per_cat: dict[str, int] = {}
        for r in rs:
            per_cat[r["category"]] = per_cat.get(r["category"], 0) + int(r["failed_tests"])
            if int(r["tests"]):
                out_rows.append({"year": year, "dalil_brand": brand, "dalil_model": model, "band": BANDS[int(r["band"])][2],
                                 "tests": r["tests"], "category": r["category"], "family": family_of(r["category"]),
                                 "rate": round(int(r["failed_tests"]) / int(r["tests"]), 5)})
        top = sorted(per_cat.items(), key=lambda x: -x[1])[:8]
        lines = [f"{names.get(c, c)} {_pct(n / total)}" for c, n in top if n]
        old = [r for r in rs if int(r["band"]) == 2 and int(r["tests"]) >= 200]
        old_top = sorted(old, key=lambda r: -int(r["failed_tests"]))[:4]
        old_txt = ""
        if old_top:
            old_txt = f" Au-delà de 160 000 km ({_n(int(old_top[0]['tests']))} contrôles) : " + ", ".join(
                f"{names.get(r['category'], r['category']).lower()} {_pct(int(r['failed_tests']) / int(r['tests']))}" for r in old_top
            ) + "."
        text = (f"Contrôle technique britannique {year}, {brand} {model} : {_n(total)} contrôles. "
                f"Part des contrôles en échec à cause de chaque famille de pièces : {', '.join(lines)}.{old_txt}")
        yield Record(
            id=f"mot_uk:{year}:{mk}:{md}", source=spec.id, kind="stat", lang="fr", text=text,
            license=spec.license, attribution=spec.attribution, url="https://open.data.dvsa.gov.uk/mot-anonymised/index.html",
            vehicle={"make": mk.title(), "model": md.title(), "year": None, "dalil_brand": brand, "dalil_model": model},
            categories=[c for c, n in top if n and c in taxonomy()["parent"]][:5], family=None, fault=None,
            label_quality=None, meta={"year": year, "tests": total, "rates": {c: round(n / total, 5) for c, n in top}},
        )
    with priors.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year", "dalil_brand", "dalil_model", "band", "tests", "category", "family", "rate"])
        w.writeheader()
        w.writerows(out_rows)
