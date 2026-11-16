"""Exporte les passages français de la base de connaissances pour le carnet Kaggle 05_vecteurs.

    python ml/export_kb_chunks.py        # écrit data/processed/kb/chunks.jsonl (id, source, texte)

Rejouable. Le carnet calcule un vecteur par passage ; les identifiants servent à rattacher
les vecteurs à la base au retour (`python ml/load_vectors.py`). Si la base est rechargée,
les identifiants changent : refaire l'export et le carnet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import select  # noqa: E402

from app.db import SessionLocal  # noqa: E402
from app.models import KnowledgeChunk  # noqa: E402

OUT = ROOT / "data" / "processed" / "kb" / "chunks.jsonl"


def export() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with SessionLocal() as db, OUT.open("w", encoding="utf-8") as f:
        for c in db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.lang == "fr").order_by(KnowledgeChunk.id)):
            f.write(json.dumps({"id": c.id, "source": c.source, "text": c.text[:1500]}, ensure_ascii=False) + "\n")
            n += 1
    return n


if __name__ == "__main__":
    print(f"{export()} passages exportés dans {OUT}")
