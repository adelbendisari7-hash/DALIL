"""Jeu d'entraînement commun aux variantes A (TF-IDF + LR) et B (encodeur affiné : CamemBERT, mmBERT).

    python ml/build_training_set.py                      # étiquettes sûres, amorçage x5 (défaut, voir ci-dessous)
    python ml/build_training_set.py --quality moyen      # + étiquettes moins sûres (réponses du forum…)
    python ml/build_training_set.py --quality tout --max-per-label 3000

Les deux variantes lisent le même fichier : la comparaison porte sur le modèle, pas sur les données.

Contenu (cible = famille ou pièce, comme `category or family` du pipeline) :
- exemples d'amorçage (`data/seed/diagnosis_examples_fr.jsonl`) et fiches de pannes : toujours, poids 1 ;
- corpus de l'étape 6 (`data/processed/train/*.jsonl`, dont L'Argus) en français (d'origine ou traduit),
  avec un **poids selon la confiance de l'étiquette** (`label_quality`, voir QUALITY_WEIGHT).

Garde-fous :
- **Aucun texte des jeux de test** (data/test/*.jsonl, demo_cases.json) : retiré s'il apparaît dans le corpus,
  les exemples d'amorçage ou les fiches (comparaison après normalisation). Le jeu d'Oran n'entre jamais ici.
- Doublons retirés (même texte normalisé, on garde l'étiquette la plus sûre).
- Validation = 1 exemple de corpus sur 10, choisi par l'identifiant (stable d'une exécution à l'autre).

Réglages par défaut (18/11/2026, ml/results/*remedes-jeu-commun*, chaîne complète, top-1) : avec tout le corpus
pondéré « moyen », la variante A perd 17 points sur les cas de démonstration (94 -> 77 %) : les étiquettes
approximatives noient les exemples écrits pour DALIL. « fort » + amorçage x5 revient au niveau du modèle en service
(dev 90 %, démo 88 %, audit 84 %, contrôle 88 %). À remesurer avec L'Argus.

Sortie : data/processed/train_set/{train,val}.jsonl et stats.json ({text, label, weight, source, quality}).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

TRAIN_DIR = ROOT / "data" / "processed" / "train"
OUT_DIR = ROOT / "data" / "processed" / "train_set"
TEST_FILES = [*sorted((ROOT / "data" / "test").glob("*.jsonl")), ROOT / "data" / "seed" / "demo_cases.json"]

# Poids d'un exemple selon la provenance de son étiquette. 1 = aussi sûr qu'un exemple écrit à la main.
QUALITY_WEIGHT = {
    "manual": 1.0, "solution+component": 1.0, "keyword+component": 1.0,   # deux indices concordants
    "solution": 0.8,                                                       # solution confirmée, catégorie muette
    "reponses+component": 0.7, "auteur+component": 0.7, "keyword": 0.6, "component": 0.5, "auteur": 0.4,  # auteur : à régler par la relecture
    "reponses": 0.4, "question+component": 0.4, "question": 0.2,
}
# Règles propres à une source, mesurées par relecture (ml/relecture_etiquettes.py) ; elles remplacent QUALITY_WEIGHT.
# L'Argus, 24/11/2026 (200 étiquettes relues par Claude, sans voir le niveau ; ml/results/*relecture-largus_forum*) :
# la pièce exacte n'est juste que dans 28 % des cas, mais la famille l'est dans 75 à 89 % des cas pour les niveaux
# confirmés par la catégorie du forum. On n'en garde que la famille, avec un poids égal à sa justesse mesurée ; les
# autres niveaux (famille juste dans 11 à 67 % des cas) sont écartés.
SOURCE_RULES = {
    "largus_forum": {"label": "family", "weights": {
        "component": 0.89, "reponses+component": 0.85, "question+component": 0.82,
        "solution+component": 0.78, "auteur+component": 0.75}},
}
LEVELS = {"fort": 0.8, "moyen": 0.5, "tout": 0.0}
MAX_CHARS = 2000  # le symptôme est au début ; chaque modèle tronque encore à sa façon


def norm(text: str) -> str:
    t = unicodedata.normalize("NFD", (text or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def test_texts() -> set[str]:
    out: set[str] = set()
    for p in TEST_FILES:
        if not p.exists():
            continue
        if p.suffix == ".json":
            rows = json.loads(p.read_text(encoding="utf-8")).get("cases", [])
        else:
            rows = [json.loads(line) for line in p.read_text(encoding="utf-8").split(chr(10)) if line.strip()]
        out.update(norm(r.get("text", "")) for r in rows if r.get("text"))
    out.discard("")
    return out


def seed_rows(weight: float = 1.0) -> list[dict]:
    from app.services.diagnosis.classifier import fiche_examples, load_examples

    faults = json.loads((ROOT / "data" / "seed" / "faults.json").read_text(encoding="utf-8"))["faults"]
    f2p = {f["slug"]: max(f["parts"].items(), key=lambda x: x[1])[0] for f in faults}
    st, sl = load_examples(ROOT / "data" / "seed" / "diagnosis_examples_fr.jsonl")
    ft, fl = fiche_examples()
    return ([{"text": t, "label": f2p[f], "fault": f, "weight": weight, "source": "seed", "quality": "manual"} for t, f in zip(st, sl)]
            + [{"text": t, "label": f2p[f], "fault": f, "weight": weight, "source": "fiche", "quality": "manual"} for t, f in zip(ft, fl)])


def is_val(rid: str) -> bool:
    return int(hashlib.sha1(rid.encode()).hexdigest(), 16) % 10 == 0


def build(quality: str = "fort", max_per_label: int = 0, sources: set[str] | None = None,
          train_dir: Path = TRAIN_DIR, seed_weight: float = 5.0) -> tuple[list[dict], list[dict], dict]:
    floor = LEVELS[quality]
    banned = test_texts()
    stats: dict = {"quality": quality, "max_per_label": max_per_label, "seed_weight": seed_weight, "par_source": {}, "ecartes": Counter()}
    train = [r for r in seed_rows(seed_weight) if norm(r["text"]) not in banned]   # même règle pour l'amorçage et les fiches
    stats["ecartes"]["amorçage ou fiche présent dans un jeu de test"] = len(seed_rows()) - len(train)
    seen = {norm(r["text"]): r for r in train}
    corpus: list[dict] = []
    for path in sorted(train_dir.glob("*.jsonl")):
        if sources and path.stem not in sources:
            continue
        kept = 0
        for line in path.read_text(encoding="utf-8").split(chr(10)):
            if not line.strip():
                continue
            r = json.loads(line)
            text = r["text"] if r["lang"] == "fr" else r.get("text_fr")
            label = r.get("category") or r.get("family")
            q = r.get("label_quality") or ("manual" if r.get("synthetic") else "keyword")
            w = QUALITY_WEIGHT.get(q, 0.2)
            rule = SOURCE_RULES.get(r["source"])
            if rule:
                label = r.get("family") if rule["label"] == "family" else label
                w = rule["weights"].get(q, 0.0)
                if not w:
                    stats["ecartes"]["niveau écarté par la relecture"] += 1
                    continue
            if not text or not label:
                stats["ecartes"]["sans texte français ou étiquette"] += 1
                continue
            if w < floor:
                stats["ecartes"][f"confiance < {quality}"] += 1
                continue
            key = norm(text)
            if key in banned:
                stats["ecartes"]["présent dans un jeu de test"] += 1
                continue
            if key in seen:
                if seen[key]["weight"] < w and seen[key]["source"] not in ("seed", "fiche"):
                    seen[key].update(label=label, weight=w, quality=q)
                stats["ecartes"]["doublon"] += 1
                continue
            row = {"id": r["id"], "text": text[:MAX_CHARS], "label": label, "fault": r.get("fault"), "weight": w,
                   "source": r["source"], "quality": q}
            seen[key] = row
            corpus.append(row)
            kept += 1
        stats["par_source"][path.stem] = kept
    if max_per_label:  # plafond par étiquette : les plus sûrs d'abord, puis ordre stable
        by_label: dict[str, list[dict]] = defaultdict(list)
        for r in sorted(corpus, key=lambda r: (-r["weight"], hashlib.sha1(r["id"].encode()).hexdigest())):
            by_label[r["label"]].append(r)
        capped = [r for rows in by_label.values() for r in rows[:max_per_label]]
        stats["ecartes"]["plafond par étiquette"] += len(corpus) - len(capped)
        corpus = capped
    val = [r for r in corpus if is_val(r["id"])]
    train += [r for r in corpus if not is_val(r["id"])]
    stats["ecartes"] = dict(stats["ecartes"])
    stats.update(train=len(train), val=len(val), labels=len({r["label"] for r in train}),
                 par_qualite=dict(Counter(r["quality"] for r in train)),
                 top_labels=Counter(r["label"] for r in train).most_common(15))
    return train, val, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quality", choices=list(LEVELS), default="fort", help="confiance minimale des étiquettes du corpus")
    ap.add_argument("--max-per-label", type=int, default=0, help="plafond d'exemples de corpus par étiquette (0 = aucun)")
    ap.add_argument("--sources", default="", help="sources du corpus à garder, séparées par des virgules (défaut : toutes)")
    ap.add_argument("--seed-weight", type=float, default=5.0,
                    help="poids des exemples d'amorçage et des fiches (écrits pour DALIL) face au corpus")
    ap.add_argument("--out", default=str(OUT_DIR))
    args = ap.parse_args()
    train, val, stats = build(args.quality, args.max_per_label, set(filter(None, args.sources.split(","))) or None,
                              seed_weight=args.seed_weight)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in (("train", train), ("val", val)):
        with (out / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (out / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
