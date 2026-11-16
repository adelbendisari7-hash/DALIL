"""Étape 2 : recherche dans la base de connaissances.

Deux modes (réglage `retrieval_mode`) :
- keyword : TF-IDF par fragments de caractères, en mémoire, sans modèle à charger ;
- hybrid  : mots-clés + vecteurs Qwen3-Embedding, fusionnés (RRF), puis reclassés par
  bge-reranker-v2-m3 (étape 8). Le score d'un passage est alors la probabilité du reclassement.
"""
from __future__ import annotations

import json
import logging
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...config import get_settings
from ...models import KnowledgeChunk
from .embeddings import get_embedder, get_reranker
from .normalize import normalize

log = logging.getLogger("dalil.retrieval")


@dataclass
class Hit:
    chunk_id: int
    score: float
    text: str
    source: str
    meta: dict
    detail: dict = field(default_factory=dict)  # scores intermédiaires (mots-clés, vecteur, reclassement)


class KeywordIndex:
    """Index par mots-clés. `only_sources` restreint l'index lui-même (et donc le calcul des poids
    TF-IDF) à certaines sources : les scores ne dépendent alors pas de la taille du reste de la base."""

    name = "keyword"

    def __init__(self, only_sources: set[str] | None = None):
        self.only_sources = only_sources
        self.signature: tuple[int, int] | None = None
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        self.rows: list[KnowledgeChunk] = []

    def _refresh(self, db: Session) -> None:
        # Recherche par mots-clés : seulement les passages en français (même langue que la requête).
        # Les passages en anglais ou en chinois attendent leur traduction ou les vecteurs multilingues.
        fr = KnowledgeChunk.lang == "fr"
        if self.only_sources:
            fr = fr & KnowledgeChunk.source.in_(self.only_sources)
        sig = tuple(db.execute(select(func.count(KnowledgeChunk.id), func.max(KnowledgeChunk.id)).where(fr)).one())
        if sig == self.signature:
            return
        self.rows = list(db.scalars(select(KnowledgeChunk).where(fr).order_by(KnowledgeChunk.id)))
        self.signature = sig
        if not self.rows:
            self.vectorizer, self.matrix = None, None
            return
        self.vectorizer = TfidfVectorizer(preprocessor=normalize, analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([r.text for r in self.rows])

    def search(self, db: Session, query: str, k: int = 5, sources: set[str] | None = None) -> list[Hit]:
        """Passages les plus proches ; `sources` restreint la recherche à certaines sources."""
        self._refresh(db)
        if self.vectorizer is None or not query.strip():
            return []
        q = self.vectorizer.transform([query])
        sims = (self.matrix @ q.T).toarray().ravel()
        if sources is not None:
            mask = np.array([r.source in sources for r in self.rows])
            sims = np.where(mask, sims, 0.0)
        top = np.argsort(-sims)[:k]
        return [
            Hit(self.rows[i].id, float(sims[i]), self.rows[i].text, self.rows[i].source, self.rows[i].meta or {})
            for i in top if sims[i] > 0
        ]


class DenseIndex:
    """Vecteurs des passages (carnet Kaggle 05) : matrice en mémoire (~19 000 x 1024), recherche exacte.

    Les vecteurs sont lus dans `vectors_path` (chunk_vectors.npy + chunk_ids.json), pas dans la colonne
    `knowledge_chunks.embedding` : en JSON sur SQLite elle pèserait plus de 100 Mo. Sur PostgreSQL,
    `ml/load_vectors.py --db` remplit aussi cette colonne (pgvector) pour une recherche côté base."""

    def __init__(self):
        self.signature = None
        self.ids: list[int] = []
        self.matrix: np.ndarray | None = None
        self.qcache: OrderedDict[str, np.ndarray] = OrderedDict()  # vecteurs de requêtes déjà calculés
        self.domain_rows: tuple | None = None  # (signature, sources, indices des lignes de la matrice)

    def query_vector(self, query: str) -> np.ndarray:
        """Vecteur de la requête, mis en cache : la recherche et le garde-fou du domaine le demandent tous deux."""
        if query in self.qcache:
            self.qcache.move_to_end(query)
            return self.qcache[query]
        v = get_embedder().encode_query(query)
        self.qcache[query] = v
        while len(self.qcache) > 256:
            self.qcache.popitem(last=False)
        return v

    def domain_similarity(self, db: Session, query: str, sources: set[str]) -> float | None:
        """Plus forte ressemblance (cosinus) entre la requête et les passages des sources de référence
        (fiches de pannes et codes OBD rédigés par l'équipe). None sans vecteurs : on retombe sur le garde-fou
        par mots-clés. Sert à dire « est-ce une panne automobile ? » : bien plus net que les mots-clés
        (data/test/dev_fr_synthetique.jsonl : pannes >= 0,492, hors-sujet <= 0,482)."""
        if not query.strip() or not self.available():
            return None
        key = (self.signature, frozenset(sources))
        if self.domain_rows is None or self.domain_rows[0] != key:
            wanted = set(db.scalars(select(KnowledgeChunk.id).where(KnowledgeChunk.source.in_(sources))))
            self.domain_rows = (key, np.array([i for i, cid in enumerate(self.ids) if cid in wanted], dtype=int))
        rows = self.domain_rows[1]
        if not len(rows):
            return None
        return float((self.matrix[rows] @ self.query_vector(query)).max())

    def _load(self) -> None:
        folder = Path(get_settings().vectors_path)
        vec, ids = folder / "chunk_vectors.npy", folder / "chunk_ids.json"
        if not (vec.exists() and ids.exists()):
            self.signature, self.ids, self.matrix = None, [], None
            return
        sig = (vec.stat().st_mtime_ns, ids.stat().st_mtime_ns)
        if sig == self.signature:
            return
        self.matrix = np.load(vec).astype(np.float32)
        self.ids = json.loads(ids.read_text(encoding="utf-8"))
        self.signature = sig
        log.info("Vecteurs chargés : %s passages", len(self.ids))

    def available(self) -> bool:
        self._load()
        return self.matrix is not None and get_embedder() is not None

    def search(self, db: Session, query: str, k: int = 30) -> list[Hit]:
        if not query.strip() or not self.available():
            return []
        sims = self.matrix @ self.query_vector(query)
        top = np.argsort(-sims)[:k]
        rows = {r.id: r for r in db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.id.in_([self.ids[i] for i in top])))}
        return [
            Hit(self.ids[i], float(sims[i]), rows[self.ids[i]].text, rows[self.ids[i]].source, rows[self.ids[i]].meta or {})
            for i in top if self.ids[i] in rows
        ]


RRF_K = 60          # constante de la fusion par rangs réciproques (valeur usuelle)
KEYWORD_POOL = 30   # passages gardés de chaque recherche avant fusion
DENSE_POOL = 30
RERANK_POOL = 20    # passages passés au modèle de reclassement (le coût du reclassement suit ce nombre)


class HybridIndex:
    """Mots-clés + vecteurs, fusionnés par rangs réciproques, puis reclassés par bge-reranker-v2-m3."""

    name = "hybrid"

    def __init__(self, keyword: KeywordIndex, dense: DenseIndex, cache_size: int = 256):
        self.keyword, self.dense = keyword, dense
        self.cache: OrderedDict[str, list[Hit]] = OrderedDict()
        self.cache_size = cache_size

    def available(self) -> bool:
        return self.dense.available() and get_reranker() is not None

    def candidates(self, db: Session, query: str) -> list[Hit]:
        """Passages candidats après fusion, avant reclassement (plus proches d'abord)."""
        kw = self.keyword.search(db, query, k=KEYWORD_POOL)
        dn = self.dense.search(db, query, k=DENSE_POOL)
        fused: dict[int, float] = {}
        hits: dict[int, Hit] = {}
        for rank, h in enumerate(kw):
            fused[h.chunk_id] = fused.get(h.chunk_id, 0.0) + 1.0 / (RRF_K + rank + 1)
            hits[h.chunk_id] = h
            h.detail["keyword"] = h.score
        for rank, h in enumerate(dn):
            fused[h.chunk_id] = fused.get(h.chunk_id, 0.0) + 1.0 / (RRF_K + rank + 1)
            if h.chunk_id in hits:
                hits[h.chunk_id].detail["dense"] = h.score
            else:
                h.detail["dense"] = h.score
                hits[h.chunk_id] = h
        order = sorted(fused, key=lambda i: -fused[i])[:RERANK_POOL]
        for i in order:
            hits[i].detail["rrf"] = fused[i]
        return [hits[i] for i in order]

    def search(self, db: Session, query: str, k: int = 5) -> list[Hit]:
        if not query.strip():
            return []
        key = f"{query}|{k}"
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        cand = self.candidates(db, query)
        if not cand:
            return []
        scores = get_reranker().score(query, [h.text for h in cand])
        for h, s in zip(cand, scores):
            h.detail["rerank"] = s
            h.score = s
        out = sorted(cand, key=lambda h: -h.score)[:k]
        self.cache[key] = out
        while len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)
        return out


index = KeywordIndex()
# Garde-fou « est-ce une panne automobile ? » : index des seules fiches de référence de l'équipe,
# pour que le seuil réglé sur le jeu dev reste valable quand la base de connaissances grandit.
DOMAIN_SOURCES = {"dalil-fiches", "dalil-dtc"}
domain_index = KeywordIndex(only_sources=DOMAIN_SOURCES)
dense_index = DenseIndex()
hybrid_index = HybridIndex(index, dense_index)


def get_index():
    """Index de recherche selon `retrieval_mode`. Repli sur les mots-clés si les modèles ou les vecteurs manquent."""
    if get_settings().retrieval_mode == "hybrid" and hybrid_index.available():
        return hybrid_index
    return index
