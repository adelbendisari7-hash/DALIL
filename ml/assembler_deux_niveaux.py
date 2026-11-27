"""Assemble un classifieur à deux niveaux dont le modèle de familles est un encodeur ONNX (CamemBERT-familles).

    python ml/assembler_deux_niveaux.py --base ml/artifacts/exp/base_reels_forums2.joblib \\
        --familles ml/artifacts/camembert-base_familles --alphas 0.15,0.25,0.5 --out-dir ml/artifacts/exp/camembert

Même principe que ml/train_family_reranker.py (score = p(panne) x p(famille) ** alpha), mais le second niveau est
CamemBERT affiné sur Kaggle (carnet 02_camembert_familles) au lieu du TF-IDF. Le fichier .joblib garde le chemin du
dossier ONNX relatif à lui-même : déplacer les deux ensemble.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml"))

from train_family_reranker import label_families  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="classifieur de pannes (.joblib) ou dossier ONNX de pièces (CamemBERT-pièces)")
    ap.add_argument("--familles", required=True, help="dossier ONNX de CamemBERT-familles (labels.json, model.onnx)")
    ap.add_argument("--alphas", default="0.25")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    base_path = Path(args.base).resolve()
    if base_path.is_dir():   # CamemBERT-pièces : étiquettes = pièces
        bmeta = json.loads((base_path / "labels.json").read_text(encoding="utf-8"))
        base = {"labels": bmeta["labels"], "target": bmeta.get("target", "part"), "version": bmeta.get("version")}
    else:
        base = joblib.load(base_path)
        base["labels"] = list(base["pipeline"].classes_)
    fam_dir = Path(args.familles).resolve()
    meta = json.loads((fam_dir / "labels.json").read_text(encoding="utf-8"))
    if meta.get("target") != "family":
        raise SystemExit(f"{fam_dir} n'est pas un modèle de familles (target = {meta.get('target')})")
    lf = label_families(base.pop("labels"), base.get("target", "fault"))
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rel = os.path.relpath(fam_dir, out.resolve())
    for a in [float(x) for x in args.alphas.split(",")]:
        path = out / f"camembert_rerank_a{a:g}.joblib"
        extra = {"base_onnx": os.path.relpath(base_path, out.resolve())} if base_path.is_dir() else {"base": base}
        joblib.dump({"kind": "family_rerank", **extra, "family_onnx": rel, "alpha": a, "label_family": lf,
                     "version": f"{base.get('version')}+{meta.get('version')}-a{a:g}"}, path)
        print(f"écrit : {path} (alpha {a:g}, familles : {rel})")


if __name__ == "__main__":
    main()
