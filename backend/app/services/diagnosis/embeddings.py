"""Étape 8 : vecteurs de recherche (Qwen3-Embedding-0.6B) et reclassement (bge-reranker-v2-m3).

Les deux modèles sont préparés par le carnet Kaggle `05_vecteurs` et chargés depuis le disque
(`python ml/load_vectors.py`). Ils demandent `torch` et `transformers`, absents de
`requirements.txt` : sans eux, ou sans les fichiers, `get_embedder()` et `get_reranker()` rendent
None et la recherche reste par mots-clés.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import numpy as np

from ...config import get_settings

log = logging.getLogger("dalil.embeddings")

# Même chaîne que dans le carnet 05 : un vecteur de requête n'a de sens que comparé à des
# vecteurs de passages calculés avec la même méthode.
EMBED_TASK = "Given a description of a car problem, retrieve passages describing the same fault"


class Embedder:
    """Qwen3-Embedding : vecteur du dernier jeton (remplissage à gauche), normalisé."""

    def __init__(self, folder: Path):
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(str(folder), padding_side="left")
        self.model = AutoModel.from_pretrained(str(folder), dtype=torch.float32).eval()

    def encode(self, texts: list[str], max_len: int = 384, batch: int = 16) -> np.ndarray:
        torch = self.torch
        out = []
        for s in range(0, len(texts), batch):
            enc = self.tok(texts[s:s + batch], padding=True, truncation=True, max_length=max_len, return_tensors="pt")
            with torch.no_grad():
                h = self.model(**enc).last_hidden_state[:, -1]
            out.append(torch.nn.functional.normalize(h.float(), dim=-1).numpy())
        return np.concatenate(out) if out else np.zeros((0, self.model.config.hidden_size), dtype=np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        return self.encode([f"Instruct: {EMBED_TASK}\nQuery:{query}"])[0]


class Reranker:
    """bge-reranker-v2-m3 : probabilité (0 à 1) qu'un passage réponde à la requête."""

    def __init__(self, folder: Path):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(str(folder))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(folder), dtype=torch.float32).eval()

    def score(self, query: str, passages: list[str], max_len: int = 512, batch: int = 8) -> list[float]:
        torch = self.torch
        out: list[float] = []
        for s in range(0, len(passages), batch):
            part = passages[s:s + batch]
            enc = self.tok([query] * len(part), part, padding=True, truncation=True, max_length=max_len, return_tensors="pt")
            with torch.no_grad():
                out += torch.sigmoid(self.model(**enc).logits.view(-1).float()).tolist()
        return out


def _load(cls, folder: str):
    path = Path(folder)
    if not (path / "config.json").exists():
        return None
    try:
        return cls(path)
    except Exception as e:  # torch ou transformers absents, fichiers incomplets
        log.warning("Chargement de %s impossible (%s) : recherche par mots-clés seulement", cls.__name__, e)
        return None


@lru_cache
def get_embedder() -> Embedder | None:
    return _load(Embedder, get_settings().embedding_model_path)


@lru_cache
def get_reranker() -> Reranker | None:
    return _load(Reranker, get_settings().reranker_model_path)
