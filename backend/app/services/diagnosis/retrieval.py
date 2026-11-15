"""Étape 2 : recherche dans la base de connaissances.

Version actuelle : recherche par mots-clés (TF-IDF, cosinus), en mémoire.
Prévu (étape 6-7) : recherche hybride avec vecteurs Qwen3-Embedding stockés dans
`knowledge_chunks.embedding` (pgvector) et reclassement bge-reranker-v2-m3.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...models import KnowledgeChunk
from .normalize import normalize


@dataclass
class Hit:
    chunk_id: int
    score: float
    text: str
    source: str
    meta: dict


class KeywordIndex:
    """Index par mots-clés. `only_sources` restreint l'index lui-même (et donc le calcul des poids
    TF-IDF) à certaines sources : les scores ne dépendent alors pas de la taille du reste de la base."""

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


index = KeywordIndex()
# Garde-fou « est-ce une panne automobile ? » : index des seules fiches de référence de l'équipe,
# pour que le seuil réglé sur le jeu dev reste valable quand la base de connaissances grandit.
DOMAIN_SOURCES = {"dalil-fiches", "dalil-dtc"}
domain_index = KeywordIndex(only_sources=DOMAIN_SOURCES)
