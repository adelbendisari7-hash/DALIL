"""Banc d'évaluation des variantes (section 6.2) : mêmes jeux de test, mêmes mesures pour toutes.

    python ml/evaluate.py                                    # variantes A et D du modèle par défaut, jeux dev + démo
    python ml/evaluate.py --model A=ml/artifacts/baseline_tfidf_lr.joblib \
                          --model B=ml/artifacts/mmbert_part --modes classifier,full \
                          --test data/test/oran_test.jsonl

Variantes : mode « classifier » = A ou B selon le modèle (classifieur seul) ; « retrieval » = C (recherche
+ modèle de langage, sans classifieur) ; « full » = D (chaîne complète). Le modèle de langage utilisé est
celui de la configuration (DALIL_LLM_PROVIDER) ; sans fournisseur, C et D tournent sans modèle de langage.

Mesures (sur la famille de pièce, comme le demande la section 6.2) :
- top-1 / top-3 : la pièce attendue est la pièce principale de la 1re cause / d'une des 3 premières ;
- abstention : part des vraies pannes auxquelles l'outil répond « je ne sais pas » ;
- hors sujet : part des entrées hors sujet correctement refusées ;
- temps de réponse moyen et 95e centile.
Les résultats sont écrits dans ml/results/ et ajoutés à ml/results/historique.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.seed import _variant  # noqa: E402
from app.services.diagnosis import pipeline as P  # noqa: E402
from app.services.diagnosis.classifier import load_classifier  # noqa: E402

RESULTS = ROOT / "ml" / "results"
DEFAULT_TESTS = [ROOT / "data" / "test" / "dev_fr_synthetique.jsonl", ROOT / "data" / "seed" / "demo_cases.json"]
VARIANT_NAME = {"classifier": "classifieur seul", "retrieval": "C (recherche + LM)", "full": "D (chaîne complète)"}


def load_cases(path: Path) -> list[dict]:
    if path.suffix == ".json":
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        return [{"id": f"{path.stem}{i:03d}", "text": c["text"], "variant": c.get("variant"), "dtc": c.get("dtc", []),
                 "expect": c.get("expect_parts", []), "expect_status": c.get("expect_status")} for i, c in enumerate(cases, 1)]
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            c = json.loads(line)
            out.append({"id": c["id"], "text": c.get("text", ""), "variant": c.get("variant"), "dtc": c.get("dtc", []),
                        "expect": c.get("expect", []), "expect_status": c.get("expect_status")})
    return out


def ranked_parts(result: dict) -> list[str]:
    seen: list[str] = []
    for c in result["causes"]:
        if c["part"]["slug"] not in seen:
            seen.append(c["part"]["slug"])
    return seen


def run(db, cases: list[dict], mode: str) -> dict:
    pos = [c for c in cases if c.get("expect_status") != "unknown"]
    neg = [c for c in cases if c.get("expect_status") == "unknown"]
    top1 = top3 = abstain = neg_ok = 0
    times, errors = [], []
    for c in cases:
        v = _variant(db, *c["variant"]) if c.get("variant") else None
        vid = v.id if v else None  # véhicule inconnu du référentiel : diagnostic sans véhicule
        t0 = time.perf_counter()
        r, _ = P.run_diagnosis(db, P.DiagnosisInput(text=c["text"], variant_id=vid, dtc_codes=c["dtc"]), mode=mode)
        times.append((time.perf_counter() - t0) * 1000)
        if c.get("expect_status") == "unknown":
            neg_ok += r["status"] == "unknown"
            if r["status"] != "unknown":
                errors.append({"id": c["id"], "text": c["text"], "attendu": "je ne sais pas", "obtenu": ranked_parts(r)[:3]})
            continue
        parts = ranked_parts(r) if r["status"] != "unknown" else []
        abstain += r["status"] == "unknown"
        hit1 = bool(parts[:1]) and parts[0] in c["expect"]
        hit3 = any(p in c["expect"] for p in parts[:3])
        top1 += hit1
        top3 += hit3
        if not hit3:
            errors.append({"id": c["id"], "text": c["text"], "attendu": c["expect"], "obtenu": parts[:3] or r["status"]})
    n = max(len(pos), 1)
    return {
        "n": len(pos), "n_hors_sujet": len(neg),
        "top1": round(top1 / n, 3), "top3": round(top3 / n, 3), "abstention": round(abstain / n, 3),
        "hors_sujet_refuse": round(neg_ok / len(neg), 3) if neg else None,
        "ms_moyen": round(statistics.mean(times), 1), "ms_p95": round(sorted(times)[int(0.95 * (len(times) - 1))], 1),
        "erreurs": errors,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="append", default=[], help="NOM=chemin (fichier .joblib ou dossier ONNX) ; répétable")
    ap.add_argument("--modes", default="classifier,full")
    ap.add_argument("--test", action="append", default=[], help="jeu de test (.jsonl ou demo_cases.json) ; répétable")
    ap.add_argument("--tag", default="", help="étiquette libre ajoutée au nom du fichier de résultats")
    args = ap.parse_args()

    models = dict(m.split("=", 1) for m in args.model) or {"A": get_settings().classifier_path}
    tests = [Path(t) for t in args.test] or DEFAULT_TESTS
    modes = [m.strip() for m in args.modes.split(",")]
    llm = get_settings().llm_provider
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    rows, details = [], {}

    done_c = False  # la variante C n'utilise pas le classifieur : on ne la mesure qu'une fois
    with SessionLocal() as db:
        for name, path in models.items():
            model = load_classifier(Path(path))
            P.get_classifier = lambda model=model: model  # la chaîne utilise ce modèle pendant l'évaluation
            version = getattr(model, "version", None) or Path(path).stem
            for mode in modes:
                if mode == "retrieval" and done_c:
                    continue
                done_c = done_c or mode == "retrieval"
                for test in tests:
                    cases = load_cases(test)
                    res = run(db, cases, mode)
                    label = f"{name} / {VARIANT_NAME.get(mode, mode)}" if mode != "retrieval" else VARIANT_NAME[mode]
                    row = {"date": stamp, "variante": label, "modele": version, "cible": getattr(model, "target", "fault"),
                           "mode": mode, "llm": llm, "jeu": test.stem,
                           **{k: v for k, v in res.items() if k != "erreurs"}}
                    rows.append(row)
                    details[f"{label} | {test.stem}"] = res["erreurs"]
                    print(f"{label:38} {test.stem:22} top1 {res['top1']:.2f}  top3 {res['top3']:.2f}  "
                          f"abst. {res['abstention']:.2f}  hors sujet {res['hors_sujet_refuse']}  {res['ms_moyen']} ms")

    RESULTS.mkdir(parents=True, exist_ok=True)
    md = [f"# Résultats {stamp}{(' ' + args.tag) if args.tag else ''}", "",
          f"Modèle de langage : `{llm}`. Jeux : {', '.join(t.stem for t in tests)}.", "",
          "| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |",
          "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rows:
        hs = "–" if r["hors_sujet_refuse"] is None else f"{r['hors_sujet_refuse']:.0%}"
        md.append(f"| {r['variante']} | {r['modele']} | {r['jeu']} | {r['n']} | {r['top1']:.0%} | {r['top3']:.0%} | "
                  f"{r['abstention']:.0%} | {hs} | {r['ms_moyen']} / {r['ms_p95']} |")
    md += ["", "## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)", ""]
    for key, errs in details.items():
        md.append(f"### {key} ({len(errs)})")
        md += [f"- `{e['id']}` {e['text'][:90]!r} : attendu {e['attendu']}, obtenu {e['obtenu']}" for e in errs] or ["- aucune"]
        md.append("")
    base = RESULTS / f"{stamp}{('-' + args.tag) if args.tag else ''}"
    base.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    base.with_suffix(".json").write_text(json.dumps({"rows": rows, "erreurs": details}, ensure_ascii=False, indent=2), encoding="utf-8")
    hist = RESULTS / "historique.csv"
    new = not hist.exists()
    with hist.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"\nRésultats : {base.with_suffix('.md')}")


if __name__ == "__main__":
    main()
