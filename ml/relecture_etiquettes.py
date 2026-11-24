"""Relecture humaine d'un échantillon d'étiquettes (L'Argus ou toute source du pipeline), puis mesure de leur justesse.

    python ml/relecture_etiquettes.py tirer --source largus_forum [--n 100]
        -> data/relecture/<source>_relecture.xlsx (à remplir : colonne « Juste ? »)
    python ml/relecture_etiquettes.py mesurer data/relecture/largus_forum_relecture.xlsx
        -> justesse par niveau de confiance, poids conseillés, ml/results/<date>-relecture-<source>.md

**Pourquoi** : l'étiquette d'une discussion (la pièce en cause) est déduite automatiquement de la solution, des
réponses ou de la question (`label_quality`). La relecture dit combien de ces étiquettes sont justes pour chaque
niveau, ce qui fixe les niveaux à garder pour l'entraînement et leur poids (ml/build_training_set.py, QUALITY_WEIGHT).

**Tirage stratifié** : le même nombre de discussions par niveau de confiance (au hasard, graine fixe), pour mesurer
chaque niveau ; la justesse d'ensemble est ensuite repondérée par la taille réelle de chaque niveau.

Réponses acceptées dans « Juste ? » : oui (bonne pièce), partiel (bonne famille, mauvaise pièce), non, ? (impossible
à dire : écarté du calcul).
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUT_DIR = ROOT / "data" / "relecture"
RESULTS = ROOT / "ml" / "results"
SEED = 2026
COLUMNS = [("N°", 5), ("Niveau de confiance", 18), ("Question du conducteur", 70), ("Solution donnée sur le forum", 45),
           ("Pièce proposée", 26), ("Famille", 16), ("Juste ?", 9), ("Bonne pièce (si non)", 24), ("Remarque", 28),
           ("Lien", 8), ("ID", 22)]
ANSWERS = {"oui": 1.0, "o": 1.0, "partiel": 0.5, "p": 0.5, "non": 0.0, "n": 0.0}


def part_names() -> dict[str, str]:
    data = json.loads((ROOT / "data" / "seed" / "part_categories.json").read_text(encoding="utf-8"))
    names = {}
    for fam in data["families"]:
        names[fam["slug"]] = fam["name_fr"]
        for c in fam.get("children", []):
            names[c["slug"]] = c["name_fr"]
    return names


def labelled(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").split(chr(10)):
        if line.strip():
            r = json.loads(line)
            if r.get("categories") or r.get("family"):
                rows.append(r)
    return rows


def sample(rows: list[dict], n: int, seed: int = SEED) -> tuple[list[dict], dict[str, int]]:
    by_q: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_q[r.get("label_quality") or "?"].append(r)
    rng = random.Random(seed)
    tiers = sorted(by_q)
    share, extra = divmod(n, len(tiers))
    picked: list[dict] = []
    rest: list[dict] = []
    for i, q in enumerate(tiers):
        pool = by_q[q][:]
        rng.shuffle(pool)
        k = share + (1 if i < extra else 0)
        picked += pool[:k]
        rest += pool[k:]
    if len(picked) < n:  # niveaux trop petits : compléter au hasard
        rng.shuffle(rest)
        picked += rest[: n - len(picked)]
    rng.shuffle(picked)
    return picked, {q: len(v) for q, v in by_q.items()}


def write_sheet(picked: list[dict], population: dict[str, int], path: Path, source: str) -> None:
    names = part_names()
    wb = Workbook()
    ws = wb.active
    ws.title = "Relecture"
    ws.append([c for c, _ in COLUMNS])
    yellow = PatternFill("solid", start_color="FFF2CC")
    for i, (name, width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=i)
        cell.font = Font(bold=True)
        if name in ("Juste ?", "Bonne pièce (si non)", "Remarque"):
            cell.fill = yellow
        ws.column_dimensions[cell.column_letter].width = width
    for i, r in enumerate(picked, start=1):
        text = r["text"] if r.get("lang") == "fr" else (r.get("text_fr") or r["text"])
        part = (r.get("categories") or [None])[0]
        ws.append([i, r.get("label_quality") or "?", text[:1500], ((r.get("meta") or {}).get("solution") or "")[:800],
                   names.get(part, part or "—"), names.get(r.get("family"), r.get("family") or "—"), "", "", "",
                   "Ouvrir" if r.get("url") else "", r["id"]])
        if r.get("url"):
            c = ws.cell(row=ws.max_row, column=10)
            c.hyperlink, c.font = r["url"], Font(color="0563C1", underline="single")
        for col in (3, 4):
            ws.cell(row=ws.max_row, column=col).alignment = Alignment(wrap_text=True, vertical="top")
    dv = DataValidation(type="list", formula1='"oui,partiel,non,?"', allow_blank=True)
    dv.add(f"G2:G{ws.max_row}")
    ws.add_data_validation(dv)
    ws.freeze_panes = "C2"

    info = wb.create_sheet("Lisez-moi")
    for line in [
        f"Relecture de {len(picked)} étiquettes tirées au hasard ({source}), le même nombre par niveau de confiance.",
        "Pour chaque ligne, lire la question (et la solution si elle existe), puis dire si la « Pièce proposée » est "
        "bien la pièce en cause :",
        "  oui = bonne pièce ; partiel = bonne famille mais pas la bonne pièce ; non = mauvaise ; ? = impossible à dire.",
        "Si non : écrire la bonne pièce si vous la connaissez (colonne « Bonne pièce »).",
        "Ne pas regarder le niveau de confiance avant de répondre : il est là pour le calcul, pas pour guider.",
        "Ensuite : python ml/relecture_etiquettes.py mesurer <ce fichier>",
    ]:
        info.append([line])
    info.column_dimensions["A"].width = 120
    strata = wb.create_sheet("Strates")
    strata.append(["niveau", "population", "tirés", "source"])
    drawn = Counter(r.get("label_quality") or "?" for r in picked)
    for q, n in sorted(population.items()):
        strata.append([q, n, drawn.get(q, 0), source])
    strata.sheet_state = "hidden"
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def wilson(k: float, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(max(0.0, c - h), 3), round(min(1.0, c + h), 3)


def measure(path: Path) -> dict:
    wb = load_workbook(path, data_only=True)
    ws = wb["Relecture"]
    header = [c.value for c in ws[1]]
    iq, ia, icorr = header.index("Niveau de confiance"), header.index("Juste ?"), header.index("Bonne pièce (si non)")
    population = {}
    source = "?"
    for row in wb["Strates"].iter_rows(min_row=2, values_only=True):
        population[row[0]] = row[1]
        source = row[3]
    per: dict[str, dict] = defaultdict(lambda: {"n": 0, "oui": 0, "partiel": 0, "non": 0, "ignores": 0})
    corrections: Counter = Counter()
    for row in ws.iter_rows(min_row=2, values_only=True):
        q = row[iq]
        ans = str(row[ia] or "").strip().lower()
        if ans not in ANSWERS:
            per[q]["ignores"] += 1
            continue
        per[q]["n"] += 1
        per[q][{1.0: "oui", 0.5: "partiel", 0.0: "non"}[ANSWERS[ans]]] += 1
        if ANSWERS[ans] == 0.0 and row[icorr]:
            corrections[str(row[icorr]).strip()] += 1
    tiers = {}
    for q, s in sorted(per.items()):
        if not s["n"]:
            continue
        exact = s["oui"] / s["n"]
        family = (s["oui"] + s["partiel"]) / s["n"]
        lo, hi = wilson(s["oui"], s["n"])
        decision = "garder" if exact >= 0.8 else ("garder avec un poids réduit" if exact >= 0.6 else "écarter")
        tiers[q] = {**s, "piece_juste": round(exact, 3), "intervalle_95": [lo, hi], "famille_juste": round(family, 3),
                    "population": population.get(q, 0), "poids_conseille": round(exact, 2) if exact >= 0.6 else 0.0,
                    "decision": decision}
    tot = sum(t["population"] for t in tiers.values()) or 1
    overall = round(sum(t["piece_juste"] * t["population"] for t in tiers.values()) / tot, 3)
    return {"source": source, "fichier": str(path), "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "justesse_globale_repondérée": overall, "niveaux": tiers, "corrections_frequentes": corrections.most_common(10)}


def report_md(res: dict) -> str:
    lines = [f"# Relecture des étiquettes : {res['source']} ({res['date']})", "",
             f"Justesse de la pièce, repondérée par la taille de chaque niveau : **{res['justesse_globale_repondérée']:.0%}**", "",
             "| Niveau | Relus | Pièce juste | Intervalle 95 % | Famille juste | Population | Décision | Poids conseillé |",
             "| --- | ---: | ---: | --- | ---: | ---: | --- | ---: |"]
    for q, t in res["niveaux"].items():
        lines.append(f"| {q} | {t['n']} | {t['piece_juste']:.0%} | {t['intervalle_95'][0]:.0%}–{t['intervalle_95'][1]:.0%} "
                     f"| {t['famille_juste']:.0%} | {t['population']} | {t['decision']} | {t['poids_conseille']} |")
    lines += ["", "Règle : pièce juste ≥ 80 % -> garder ; 60 à 80 % -> garder avec un poids égal à la justesse ; "
              "moins de 60 % -> écarter. Reporter les poids dans ml/build_training_set.py (QUALITY_WEIGHT).",
              "Avec une dizaine de lectures par niveau, l'intervalle est large : relire plus (--n 200) si une décision "
              "tient à quelques points."]
    if res["corrections_frequentes"]:
        lines += ["", "Corrections les plus fréquentes : " + ", ".join(f"{c} ({n})" for c, n in res["corrections_frequentes"])]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tirer")
    t.add_argument("--source", default="largus_forum")
    t.add_argument("--n", type=int, default=100)
    t.add_argument("--out", default=None)
    m = sub.add_parser("mesurer")
    m.add_argument("fichier")
    args = ap.parse_args()
    if args.cmd == "tirer":
        src = PROCESSED / f"{args.source}.jsonl"
        if not src.exists():
            raise SystemExit(f"{src} introuvable : lancer d'abord data/pipeline/run.py collect --sources {args.source}")
        picked, population = sample(labelled(src), args.n)
        out = Path(args.out) if args.out else OUT_DIR / f"{args.source}_relecture.xlsx"
        if out.exists():
            raise SystemExit(f"{out} existe déjà (peut-être déjà rempli) : choisir --out ou le déplacer")
        write_sheet(picked, population, out, args.source)
        print(f"{len(picked)} étiquettes à relire : {out}")
        print("par niveau :", dict(Counter(r.get("label_quality") for r in picked)), "population :", population)
    else:
        res = measure(Path(args.fichier))
        RESULTS.mkdir(parents=True, exist_ok=True)
        stem = f"{datetime.now():%Y%m%d-%H%M}-relecture-{res['source']}"
        (RESULTS / f"{stem}.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        md = report_md(res)
        (RESULTS / f"{stem}.md").write_text(md, encoding="utf-8")
        print(md)


if __name__ == "__main__":
    main()
