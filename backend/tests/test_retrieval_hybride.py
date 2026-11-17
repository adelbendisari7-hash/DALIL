"""Recherche hybride (étape 8) : fusion, reclassement et repli, avec de faux modèles (sans torch ni fichiers lourds)."""
import json
import zlib

import numpy as np
import pytest
from sqlalchemy import select

from app.config import get_settings
from app.models import KnowledgeChunk
from app.services.diagnosis import retrieval
from app.services.diagnosis.pipeline import DiagnosisInput, run_diagnosis

DIM = 64


def _vec(text: str) -> np.ndarray:
    """Faux vecteur : sac de mots haché, normalisé (deux textes de mots communs sont proches)."""
    v = np.zeros(DIM, dtype=np.float32)
    for w in text.lower().split():
        v[zlib.crc32(w.encode()) % DIM] += 1.0
    n = np.linalg.norm(v)
    return v / n if n else v


class FakeEmbedder:
    def encode_query(self, q: str) -> np.ndarray:
        return _vec(q)

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.stack([_vec(t) for t in texts]) if texts else np.zeros((0, DIM), dtype=np.float32)


class FakeReranker:
    """Score = part des mots de la requête présents dans le passage."""

    def __init__(self):
        self.calls = 0

    def score(self, query: str, passages: list[str]) -> list[float]:
        self.calls += 1
        words = set(query.lower().split())
        return [len(words & set(p.lower().split())) / max(len(words), 1) for p in passages]


@pytest.fixture()
def hybrid(db, tmp_path, monkeypatch):
    rows = list(db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.lang == "fr").order_by(KnowledgeChunk.id)))
    assert rows, "la base de test doit contenir des passages (fiches et codes OBD du seed)"
    np.save(tmp_path / "chunk_vectors.npy", np.stack([_vec(r.text) for r in rows]).astype(np.float16))
    (tmp_path / "chunk_ids.json").write_text(json.dumps([r.id for r in rows]), encoding="utf-8")
    s = get_settings()
    monkeypatch.setattr(s, "vectors_path", str(tmp_path))
    monkeypatch.setattr(s, "retrieval_mode", "hybrid")
    reranker = FakeReranker()
    monkeypatch.setattr(retrieval, "get_embedder", lambda: FakeEmbedder())
    monkeypatch.setattr(retrieval, "get_reranker", lambda: reranker)
    retrieval.dense_index.signature = None  # recharge depuis tmp_path
    retrieval.hybrid_index.cache.clear()
    yield reranker
    retrieval.dense_index.signature = None
    retrieval.hybrid_index.cache.clear()


def test_repli_sur_les_mots_cles_sans_vecteurs(monkeypatch, tmp_path):
    s = get_settings()
    monkeypatch.setattr(s, "vectors_path", str(tmp_path / "vide"))
    monkeypatch.setattr(s, "retrieval_mode", "hybrid")
    retrieval.dense_index.signature = None
    assert retrieval.get_index() is retrieval.index


def test_mode_mots_cles_par_defaut(monkeypatch):
    monkeypatch.setattr(get_settings(), "retrieval_mode", "keyword")
    assert retrieval.get_index() is retrieval.index


def test_recherche_hybride_fusionne_et_reclasse(db, hybrid):
    assert retrieval.get_index() is retrieval.hybrid_index
    hits = retrieval.hybrid_index.search(db, "plaquettes de frein usées frottement métallique", k=5)
    assert hits and len(hits) <= 5
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)  # trié par reclassement
    assert all({"rrf", "rerank"} <= set(h.detail) for h in hits)
    assert hybrid.calls == 1
    assert len(retrieval.hybrid_index.candidates(db, "frein")) <= get_settings().rerank_pool


def test_recherche_hybride_mise_en_cache(db, hybrid):
    retrieval.hybrid_index.search(db, "démarreur fait un clic", k=5)
    retrieval.hybrid_index.search(db, "démarreur fait un clic", k=5)
    assert hybrid.calls == 1  # la deuxième question identique ne repasse pas par le reclassement


def test_diagnostic_en_mode_hybride(db, hybrid):
    r, ids = run_diagnosis(db, DiagnosisInput(text="le voyant batterie s'allume et le démarreur ne tourne plus"))
    assert r["status"] in ("ok", "clarify", "unknown")
    assert ids and all(isinstance(i, int) for i in ids)
    assert hybrid.calls >= 1


def test_mode_classifieur_ne_cherche_pas_en_hybride(db, hybrid):
    run_diagnosis(db, DiagnosisInput(text="plaquettes de frein usées"), mode="classifier")
    assert hybrid.calls == 0


def test_garde_fou_vectoriel_du_domaine(db, hybrid, monkeypatch):
    fiche = db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.source == "dalil-fiches")).first()
    assert retrieval.dense_index.domain_similarity(db, fiche.text, {"dalil-fiches"}) == pytest.approx(1.0, abs=1e-3)

    class Contraire(FakeEmbedder):
        def encode_query(self, q):
            return -_vec(q)  # opposé de tout vocabulaire du jeu : ressemblance négative avec les fiches

    monkeypatch.setattr(retrieval, "get_embedder", lambda: Contraire())
    retrieval.dense_index.qcache.clear()
    r = _diag(db, "bonjour, vous êtes ouverts le vendredi ?")
    assert r["status"] == "unknown" and r["causes"] == []


def _diag(db, text):
    return run_diagnosis(db, DiagnosisInput(text=text))[0]


def test_garde_fou_vectoriel_absent_en_mode_mots_cles(db, monkeypatch):
    monkeypatch.setattr(get_settings(), "retrieval_mode", "keyword")
    assert retrieval.get_index() is retrieval.index  # le garde-fou vectoriel n'est consulté qu'en mode hybride
    r = _diag(db, "plaquettes de frein usées, frottement métallique à l'avant")
    assert r["status"] in ("ok", "clarify")


def test_rechargement_des_referentiels_garde_les_identifiants(db):
    """Les vecteurs sont rangés par identifiant de passage : `python -m app.seed` (relancé à chaque démarrage
    par le lanceur) ne doit pas renuméroter les fiches (incident du 17/11/2026)."""
    from app.seed import seed_knowledge

    def ids():
        return sorted(db.scalars(select(KnowledgeChunk.id).where(KnowledgeChunk.source.in_(retrieval.DOMAIN_SOURCES))))

    avant = ids()
    seed_knowledge(db)
    db.commit()
    assert ids() == avant


def test_vecteurs_des_fiches_manquants_recalcules(db, hybrid, tmp_path):
    """Fiches de référence sans vecteur (identifiants changés) : la recherche les recalcule, retire les vecteurs
    de passages disparus, enregistre le résultat, et le garde-fou du domaine refonctionne."""
    fiches = set(db.scalars(select(KnowledgeChunk.id).where(KnowledgeChunk.source.in_(retrieval.DOMAIN_SOURCES))))
    ids = json.loads((tmp_path / "chunk_ids.json").read_text(encoding="utf-8"))
    vec = np.load(tmp_path / "chunk_vectors.npy")
    keep = [i for i, cid in enumerate(ids) if cid not in fiches]
    np.save(tmp_path / "chunk_vectors.npy", np.concatenate([vec[keep], vec[:3]]))  # 3 vecteurs orphelins
    (tmp_path / "chunk_ids.json").write_text(json.dumps([ids[i] for i in keep] + [10**9, 10**9 + 1, 10**9 + 2]),
                                              encoding="utf-8")
    retrieval.dense_index.signature = None
    retrieval.dense_index.domain_rows = None
    fiche = db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.source == "dalil-fiches")).first()

    assert retrieval.dense_index.domain_similarity(db, fiche.text, {"dalil-fiches"}) == pytest.approx(1.0, abs=1e-3)
    saved = json.loads((tmp_path / "chunk_ids.json").read_text(encoding="utf-8"))
    assert fiches <= set(saved) and 10**9 not in saved
    assert retrieval.dense_index.ensure_reference(db) == 0  # rien à refaire ensuite
