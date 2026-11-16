"""Installe les sorties du carnet Kaggle 05_vecteurs et vérifie le portage.

    python ml/kaggle/kaggle_run.py output 05_vecteurs     # télécharge dans ml/kaggle/_outputs/05_vecteurs/
    python ml/load_vectors.py                              # installe dans ml/artifacts/ et contrôle
    python ml/load_vectors.py --db                         # PostgreSQL : remplit aussi knowledge_chunks.embedding

Contrôles : (1) les identifiants des vecteurs existent tous dans la base ; (2) les vecteurs de requêtes
recalculés ici (processeur, float32) retrouvent ceux de Kaggle (GPU, float16) : cosinus > 0,98. Sans (2), le
portage de la méthode (dernier jeton, remplissage à gauche, instruction) est faux et la recherche aussi.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import select, update  # noqa: E402

from app.db import SessionLocal  # noqa: E402
from app.models import KnowledgeChunk  # noqa: E402
from app.services.diagnosis.embeddings import EMBED_TASK, Embedder  # noqa: E402

SRC = ROOT / "ml" / "kaggle" / "_outputs" / "05_vecteurs"
ART = ROOT / "ml" / "artifacts"


def install(src: Path) -> None:
    for name in ("qwen3-embedding-0.6b", "bge-reranker-v2-m3"):
        archive = src / f"{name}.zip"
        if not archive.exists():
            raise SystemExit(f"manquant : {archive}")
        target = ART / name
        if target.exists():
            shutil.rmtree(target)
        with zipfile.ZipFile(archive) as z:
            z.extractall(target)
        print("installé :", target)
    (ART / "vectors").mkdir(parents=True, exist_ok=True)
    for f in ("chunk_vectors.npy", "chunk_ids.json"):
        shutil.copy(src / f, ART / "vectors" / f)
    print("installé :", ART / "vectors")


def check_ids() -> list[int]:
    ids = json.loads((ART / "vectors" / "chunk_ids.json").read_text(encoding="utf-8"))
    vectors = np.load(ART / "vectors" / "chunk_vectors.npy", mmap_mode="r")
    assert vectors.shape[0] == len(ids), f"{vectors.shape[0]} vecteurs pour {len(ids)} identifiants"
    with SessionLocal() as db:
        in_db = set(db.scalars(select(KnowledgeChunk.id)))
    missing = [i for i in ids if i not in in_db]
    print(f"vecteurs : {vectors.shape}, {len(ids) - len(missing)} passages retrouvés dans la base, {len(missing)} absents")
    if missing:
        print("  la base a été rechargée depuis l'export : refaire `python ml/export_kb_chunks.py` et le carnet 05")
    return ids


def check_queries(src: Path) -> float:
    ref = json.loads((src / "check_queries.json").read_text(encoding="utf-8"))
    assert ref["task"] == EMBED_TASK, "l'instruction du carnet diffère de celle de embeddings.py"
    emb = Embedder(ART / "qwen3-embedding-0.6b")
    local = np.stack([emb.encode_query(q) for q in ref["texts"]])
    kaggle = np.array(ref["vectors"], dtype=np.float32)
    cos = (local * kaggle).sum(axis=1) / (np.linalg.norm(local, axis=1) * np.linalg.norm(kaggle, axis=1))
    print(f"portage : cosinus local / Kaggle sur {len(cos)} requêtes, min {cos.min():.4f}, moyenne {cos.mean():.4f}")
    return float(cos.min())


def fill_db(ids: list[int]) -> None:
    with SessionLocal() as db:
        if db.bind.dialect.name != "postgresql":
            print("--db : ignoré hors PostgreSQL (la colonne JSON de SQLite pèserait plus de 100 Mo)")
            return
        vectors = np.load(ART / "vectors" / "chunk_vectors.npy")
        for s in range(0, len(ids), 500):
            db.execute(update(KnowledgeChunk), [{"id": i, "embedding": v.astype(float).tolist()}
                                                for i, v in zip(ids[s:s + 500], vectors[s:s + 500])])
        db.commit()
        print(f"colonne embedding remplie pour {len(ids)} passages")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=SRC)
    ap.add_argument("--db", action="store_true")
    ap.add_argument("--skip-install", action="store_true", help="contrôler sans réinstaller")
    args = ap.parse_args()
    if not args.skip_install:
        install(args.src)
    ids = check_ids()
    worst = check_queries(args.src)
    if worst < 0.98:
        raise SystemExit("portage incorrect : cosinus minimal sous 0,98")
    if args.db:
        fill_db(ids)
    print("OK")


if __name__ == "__main__":
    main()
