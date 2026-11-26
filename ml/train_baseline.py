"""Variante A (section 6.2) : TF-IDF + régression logistique, entraînée sur le portable.

    python ml/train_baseline.py                          # cible = panne type, exemples d'amorçage (modèle par défaut)
    python ml/train_baseline.py --target part            # cible = famille de pièce (section 6.1)
    python ml/train_baseline.py --target part --corpus   # + corpus traduit de l'étape 6 (data/processed/train/)
    python ml/train_baseline.py --grid                   # petite recherche d'hyperparamètres
    python ml/train_baseline.py --set                    # jeu commun aux variantes (ml/build_training_set.py), pondéré

Le modèle est exporté avec sa cible et sa version ; la chaîne de diagnostic sait utiliser les deux cibles.
La validation croisée porte sur les exemples d'amorçage synthétiques : elle valide le code. Les mesures
comparables entre variantes se font avec `ml/evaluate.py` sur data/test/.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.diagnosis.classifier import build_pipeline, fiche_examples, load_examples  # noqa: E402

ARTIFACTS = ROOT / "ml" / "artifacts"
TRAIN_DIR = ROOT / "data" / "processed" / "train"


def fault_to_part() -> dict[str, str]:
    data = json.loads((ROOT / "data" / "seed" / "faults.json").read_text(encoding="utf-8"))
    return {f["slug"]: max(f["parts"].items(), key=lambda x: x[1])[0] for f in data["faults"]}


def relabel(labels: list[str], target: str) -> list[str]:
    if target == "fault":
        return list(labels)
    f2p = fault_to_part()
    return [f2p[x] for x in labels]


def corpus_examples(target: str, include_synthetic: bool = True) -> tuple[list[str], list[str], dict]:
    """Exemples du corpus de l'étape 6, en français seulement (texte d'origine français ou traduit)."""
    texts, labels, stats = [], [], {}
    for path in sorted(TRAIN_DIR.glob("*.jsonl")):
        n = 0
        for line in path.read_text(encoding="utf-8").split(chr(10)):
            if not line.strip():
                continue
            r = json.loads(line)
            text = r.get("text_fr") if r["lang"] != "fr" else r["text"]
            if not text or (r.get("synthetic") and not include_synthetic):
                continue
            label = r.get("fault") if target == "fault" else (r.get("category") or r.get("family"))
            if not label:
                continue
            texts.append(text[:1000])  # le symptôme est au début ; au-delà, surtout du récit
            labels.append(label)
            n += 1
        stats[path.stem] = n
    return texts, labels, stats


def evaluate(texts, labels, target: str, extra: tuple[list, list], C: float = 20.0, folds: int = 3, seed: int = 0) -> dict:
    """Validation croisée sur les exemples d'amorçage ; fiches et corpus ajoutés aux plis d'entraînement seulement."""
    texts, labels = np.array(texts, dtype=object), np.array(labels)
    ft, fl = fiche_examples()
    fl = relabel(fl, target)
    xt, xl = extra
    f2p = fault_to_part()
    to_part = (lambda x: f2p.get(x, x)) if target == "fault" else (lambda x: x)
    top1 = top3 = part1 = n = 0
    top_probs = []
    for tr, te in StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed).split(texts, labels):
        pipe = build_pipeline(large=bool(xt))
        pipe.set_params(clf__C=C)
        pipe.fit(list(texts[tr]) + ft + xt, list(labels[tr]) + fl + xl)
        proba = pipe.predict_proba(list(texts[te]))
        for i, row in enumerate(proba):
            order = pipe.classes_[np.argsort(-row)]
            gold = labels[te][i]
            top1 += order[0] == gold
            top3 += gold in order[:3]
            part1 += to_part(order[0]) == to_part(gold)
            top_probs.append(row.max())
            n += 1
    return {"target": target, "C": C, "n": n, "top1": round(top1 / n, 3), "top3": round(top3 / n, 3),
            "part_top1": round(part1 / n, 3), "median_top_prob": round(float(np.median(top_probs)), 3)}


def train_on_set(set_dir: Path, out: Path | None) -> Path:
    """Variante A sur le jeu commun (cible = pièce), chaque exemple pondéré par la confiance de son étiquette."""
    rows = [json.loads(line) for line in (set_dir / "train.jsonl").read_text(encoding="utf-8").split(chr(10)) if line.strip()]
    stats = json.loads((set_dir / "stats.json").read_text(encoding="utf-8"))
    texts = [r["text"][:1000] for r in rows]
    pipe = build_pipeline(large=True)
    pipe.fit(texts, [r["label"] for r in rows], clf__sample_weight=np.array([r["weight"] for r in rows]))
    val = [json.loads(line) for line in (set_dir / "val.jsonl").read_text(encoding="utf-8").split(chr(10)) if line.strip()]
    res: dict = {"target": "part", "set": stats.get("quality"), "train": len(rows), "val": len(val)}
    if val:
        proba = pipe.predict_proba([r["text"][:1000] for r in val])
        order = pipe.classes_[np.argsort(-proba, axis=1)]
        res.update(val_top1=round(float(np.mean([o[0] == r["label"] for o, r in zip(order, val)])), 3),
                   val_top3=round(float(np.mean([r["label"] in o[:3] for o, r in zip(order, val)])), 3))
    version = f"tfidf-lr-set-{stats.get('quality')}-{datetime.now(timezone.utc):%Y%m%d}"
    out = out or ARTIFACTS / "baseline_tfidf_lr_set.joblib"
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipe, "target": "part", "version": version, "trained_on": stats}, out)
    out.with_suffix(".metrics.json").write_text(json.dumps({**res, "version": version}, indent=2), encoding="utf-8")
    print(res)
    print(f"Poids exportés : {out} (version {version})")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["fault", "part"], default="fault")
    ap.add_argument("--corpus", action="store_true", help="ajouter le corpus traduit de l'étape 6")
    ap.add_argument("--no-synthetic", action="store_true", help="exclure les exemples synthétiques du corpus")
    ap.add_argument("--grid", action="store_true")
    ap.add_argument("--cv", action="store_true", help="validation croisée même avec le corpus (lent)")
    ap.add_argument("--out", default=None, help="fichier de sortie (défaut : ml/artifacts/baseline_tfidf_lr[_part].joblib)")
    ap.add_argument("--set", nargs="?", const=str(ROOT / "data" / "processed" / "train_set"), default=None,
                    help="entraîner sur le jeu commun (dossier de ml/build_training_set.py)")
    ap.add_argument("--exemples-reels", default=None,
                    help="JSONL {text, fault} d'exemples réels vérifiés à ajouter (ex. data/processed/largus_causes_verifiees.jsonl)")
    args = ap.parse_args()
    if args.set:
        train_on_set(Path(args.set), Path(args.out) if args.out else None)
        return

    seed_texts, seed_faults = load_examples(ROOT / "data" / "seed" / "diagnosis_examples_fr.jsonl")
    seed_labels = relabel(seed_faults, args.target)
    extra: tuple[list, list] = ([], [])
    corpus_stats: dict = {}
    if args.exemples_reels:  # vrais textes de conducteurs, cause confirmée et vérifiée (L'Argus, 26/11/2026)
        reels = [json.loads(l) for l in Path(args.exemples_reels).read_text(encoding="utf-8").split(chr(10)) if l.strip()]
        extra = ([r["text"][:1000] for r in reels], relabel([r["fault"] for r in reels], args.target))
        corpus_stats = {"exemples_reels": len(reels)}
        print(f"exemples réels vérifiés : {len(reels)}")
    if args.corpus:
        ct, cl, corpus_stats = corpus_examples(args.target, include_synthetic=not args.no_synthetic)
        extra = (ct, cl)
        print(f"corpus de l'étape 6 : {len(ct)} exemples en français {corpus_stats}")
        if not ct:
            print("  aucun texte traduit : lancer d'abord la traduction (ml/kaggle/README.md)")
    print(f"{len(seed_texts)} exemples d'amorçage, {len(set(seed_labels))} classes, cible = {args.target}")
    if args.grid:
        for C in (1, 4, 8, 20, 50):
            print(evaluate(seed_texts, seed_labels, args.target, extra, C=C))
        return
    if args.corpus and not args.cv:
        res = {"target": args.target, "cv": "non calculée (corpus) : mesurer avec ml/evaluate.py"}
    else:
        res = evaluate(seed_texts, seed_labels, args.target, extra)
    print("Validation croisée :", res)

    ft, fl = fiche_examples()
    pipe = build_pipeline(large=args.corpus)
    pipe.fit(seed_texts + ft + extra[0], seed_labels + relabel(fl, args.target) + extra[1])
    version = (f"tfidf-lr-{args.target}{'-corpus' if args.corpus else ''}{'-reels' if args.exemples_reels else ''}"
               f"-{datetime.now(timezone.utc):%Y%m%d}")
    suffix = "" if args.target == "fault" and not args.corpus else f"_{args.target}{'_corpus' if args.corpus else ''}"
    out = Path(args.out) if args.out else ARTIFACTS / f"baseline_tfidf_lr{suffix}.joblib"
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipe, "target": args.target, "version": version,
                 "trained_on": {"seed": len(seed_texts), "fiches": len(ft), "corpus": corpus_stats}}, out)
    out.with_suffix(".metrics.json").write_text(json.dumps({**res, "version": version, "corpus": corpus_stats}, indent=2), encoding="utf-8")
    print(f"Poids exportés : {out} (version {version})")


if __name__ == "__main__":
    main()
