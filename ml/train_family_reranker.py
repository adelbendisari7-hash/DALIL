"""Classifieur à deux niveaux : le modèle en service propose ses pannes, un modèle de familles de pièces les reclasse.

    python ml/train_family_reranker.py                               # alphas 0.25, 0.5, 1 ; niveau « fort »
    python ml/train_family_reranker.py --alphas 0.5 --quality moyen
    python ml/evaluate.py --model A-2niv-0.5=ml/artifacts/famille_rerank_a0.5.joblib ...

Pourquoi : la relecture de L'Argus (24/11/2026) donne la pièce exacte juste dans 28 % des cas seulement, mais la
famille juste dans 75 à 89 % des cas pour les niveaux confirmés par la catégorie du forum. Entraîner le classifieur
de pièces avec ces étiquettes de famille l'a fait reculer (démo 94 -> 77 %). Ici, L'Argus n'apprend que les
familles, à un second modèle, qui ne fait que reclasser les propositions du modèle en service :
score = p(panne) x p(famille de la panne) ** alpha (classe FamilyRerankedClassifier, chargée par load_classifier).

Données du modèle de familles : exemples d'amorçage et fiches (famille de leur pièce principale, poids --seed-weight)
+ L'Argus (règle SOURCE_RULES de build_training_set.py : famille seule, poids = justesse mesurée), sans aucun texte
des jeux de test. Alpha se règle sur dev, démo et audit ; le jeu de contrôle n'est regardé qu'à la fin.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "ml"))

import build_training_set as B  # noqa: E402
from app.services.diagnosis.classifier import build_pipeline  # noqa: E402

ARTIFACTS = ROOT / "ml" / "artifacts"


def part_to_family() -> dict[str, str]:
    data = json.loads((ROOT / "data" / "seed" / "part_categories.json").read_text(encoding="utf-8"))
    out = {}
    for fam in data["families"]:
        out[fam["slug"]] = fam["slug"]
        for child in fam.get("children", []):
            out[child["slug"]] = fam["slug"]
    return out


def fault_to_part() -> dict[str, str]:
    faults = json.loads((ROOT / "data" / "seed" / "faults.json").read_text(encoding="utf-8"))["faults"]
    return {f["slug"]: max(f["parts"].items(), key=lambda x: x[1])[0] for f in faults}


def label_families(labels: list[str], target: str) -> dict[str, str]:
    p2f, f2p = part_to_family(), fault_to_part()
    out = {}
    for label in labels:
        part = f2p.get(label) if target == "fault" else label
        if part and part in p2f:
            out[label] = p2f[part]
    return out


def family_rows(quality: str, seed_weight: float, sources: set[str] | None = None,
                diagnostic_only: bool = False) -> tuple[list[dict], list[dict], dict]:
    """(entraînement, validation, statistiques) au niveau famille."""
    p2f = part_to_family()
    train, val, stats = B.build(quality, sources=sources or {"largus_forum"}, seed_weight=seed_weight,
                                diagnostic_only=diagnostic_only)
    def fam(r):
        return p2f.get(r["label"])   # amorçage : pièce -> famille ; L'Argus : déjà une famille
    train = [{**r, "family": fam(r)} for r in train if fam(r)]
    val = [{**r, "family": fam(r)} for r in val if fam(r)]
    return train, val, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=str(ARTIFACTS / "baseline_tfidf_lr.joblib"), help="classifieur en service (.joblib)")
    ap.add_argument("--alphas", default="0.25,0.5,1")
    ap.add_argument("--quality", choices=list(B.LEVELS), default="fort")
    ap.add_argument("--seed-weight", type=float, default=5.0)
    ap.add_argument("--out-dir", default=str(ARTIFACTS))
    ap.add_argument("--sources", default="largus_forum",
                    help="forums du modèle de familles, séparés par des virgules (ex. largus_forum,techniconnexion)")
    ap.add_argument("--diagnostic-seul", action="store_true",
                    help="écarter des forums les questions de procédure ou d'achat (même règle que Techniconnexion)")
    args = ap.parse_args()
    sources = set(filter(None, args.sources.split(",")))

    base = joblib.load(args.base)
    if not isinstance(base, dict):
        base = {"pipeline": base, "target": "fault", "version": None}
    labels = list(base["pipeline"].classes_)
    lf = label_families(labels, base.get("target", "fault"))
    print(f"classifieur de base : {len(labels)} étiquettes ({base.get('target')}), {len(lf)} reliées à une famille")

    train, val, stats = family_rows(args.quality, args.seed_weight, sources, args.diagnostic_seul)
    print(f"modèle de familles : {len(train)} exemples d'entraînement, {len(val)} de validation, "
          f"{len({r['family'] for r in train})} familles ; par source : {stats['par_source']}")
    pipe = build_pipeline(large=True)
    pipe.fit([r["text"][:1000] for r in train], [r["family"] for r in train],
             clf__sample_weight=np.array([r["weight"] for r in train]))
    if val:
        pred = pipe.predict([r["text"][:1000] for r in val])
        acc = float(np.mean([p == r["family"] for p, r in zip(pred, val)]))
        print(f"validation (familles des forums) : {acc:.1%}")

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = f"{datetime.now(timezone.utc):%Y%m%d}"
    for a in [float(x) for x in args.alphas.split(",")]:
        tag = "largus" if sources == {"largus_forum"} else "+".join(sorted(x.split("_")[0] for x in sources))
        version = f"{base.get('version') or 'tfidf-lr'}+familles-{tag}-{args.quality}-a{a:g}-{stamp}"
        path = out / f"famille_rerank_a{a:g}.joblib"
        joblib.dump({"kind": "family_rerank", "base": base, "family_pipeline": pipe, "alpha": a,
                     "label_family": lf, "version": version,
                     "trained_on": {"quality": args.quality, "seed_weight": args.seed_weight, "stats": stats}}, path)
        print(f"écrit : {path} (alpha {a:g})")


if __name__ == "__main__":
    main()
