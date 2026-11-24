"""Jeu d'affinage du modèle de langage (variante D, section 6.6), construit sur le portable.

    python ml/build_llm_dataset.py            # -> data/processed/llm/train.jsonl et val.jsonl

Chaque exemple reproduit exactement l'appel fait par la chaîne de diagnostic (llm.py) :
- système : SYSTEM_PROMPT ;
- utilisateur : description, véhicule, passages retrouvés dans la base, 6 pannes candidates
  (proposées par le classifieur de référence, la bonne réponse insérée si elle manque) ;
- assistant : le classement JSON attendu, la bonne panne en tête, avec une explication tirée de sa fiche.

Sources : exemples d'amorçage français et corpus traduit de l'étape 6 qui porte une panne type.
Les jeux de test (data/test/, cas de démonstration) n'y entrent jamais.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db import SessionLocal  # noqa: E402
from app.services.diagnosis.classifier import get_classifier, load_examples  # noqa: E402
from app.services.diagnosis.llm import SYSTEM_PROMPT, build_user_message  # noqa: E402
from app.services.diagnosis.retrieval import index  # noqa: E402  (mots-clés : le jeu d affinage est fixe)

OUT = ROOT / "data" / "processed" / "llm"
N_CANDIDATES = 6


def french_examples() -> list[tuple[str, str, str]]:
    """(id, texte français, panne type)."""
    out = []
    texts, faults = load_examples(ROOT / "data" / "seed" / "diagnosis_examples_fr.jsonl")
    out += [(f"seed:{i}", t, f) for i, (t, f) in enumerate(zip(texts, faults))]
    for path in sorted((ROOT / "data" / "processed" / "train").glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").split(chr(10)):
            if not line.strip():
                continue
            r = json.loads(line)
            text = r["text"] if r["lang"] == "fr" else r.get("text_fr")
            if text and r.get("fault"):
                out.append((r["id"], text[:1500], r["fault"]))
    return out


def explanation(fault: dict) -> str:
    first = fault["description"].split(".")[0].strip()
    return f"{fault['name_fr']} : {first[0].lower() + first[1:]}." if first else fault["name_fr"]


def build(seed: int = 7, val_ratio: float = 0.1) -> dict:
    rng = random.Random(seed)
    faults = {f["slug"]: f for f in json.loads((ROOT / "data" / "seed" / "faults.json").read_text(encoding="utf-8"))["faults"]}
    clf = get_classifier()
    examples = [e for e in french_examples() if e[2] in faults]
    rng.shuffle(examples)
    rows = []
    with SessionLocal() as db:
        for ex_id, text, gold in examples:
            probs = clf.predict_proba(text)
            if getattr(clf, "target", "fault") != "fault":
                raise SystemExit("le classifieur par défaut doit prédire des pannes types (cible fault)")
            cands = [s for s, _ in sorted(probs.items(), key=lambda x: -x[1]) if s in faults][:N_CANDIDATES]
            if gold not in cands:
                cands[rng.randrange(len(cands))] = gold  # la bonne réponse est toujours proposée
            hits = [h for h in index.search(db, text, k=6) if h.meta.get("id") != ex_id][:5]
            user = build_user_message(text, "véhicule non précisé", [h.text for h in hits],
                                      {s: faults[s]["name_fr"] for s in cands})
            others = [s for s in cands if s != gold][:2]
            ranking = [{"fault": gold, "confidence": 0.8, "explanation": explanation(faults[gold])}]
            ranking += [{"fault": s, "confidence": round(0.15 / (i + 1), 2), "explanation": explanation(faults[s])}
                        for i, s in enumerate(others)]
            rows.append({"id": ex_id, "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user},
                {"role": "assistant", "content": json.dumps({"ranking": ranking}, ensure_ascii=False)},
            ]})
    n_val = max(1, int(len(rows) * val_ratio))
    OUT.mkdir(parents=True, exist_ok=True)
    for name, part in (("val", rows[:n_val]), ("train", rows[n_val:])):
        with (OUT / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for r in part:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"train": len(rows) - n_val, "val": n_val, "sources": sorted({e[0].split(":")[0] for e in examples})}


if __name__ == "__main__":
    stats = build()
    print(f"Jeu d'affinage : {stats['train']} exemples d'entraînement, {stats['val']} de validation "
          f"(sources : {', '.join(stats['sources'])}) -> {OUT}")
