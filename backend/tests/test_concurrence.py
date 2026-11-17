"""Démarrage de l'API : préchargement des modèles et diagnostics simultanés (incident du 17/11/2026).

Juste après le démarrage, plusieurs diagnostics arrivaient pendant que les index et les modèles se chargeaient
encore : erreurs 500. Le préchargement (`app.main.warmup`) et le verrou `MODELS_LOCK` doivent l'empêcher.
"""
from concurrent.futures import ThreadPoolExecutor

from app.db import SessionLocal
from app.main import warmup
from app.services.diagnosis import retrieval
from app.services.diagnosis.pipeline import DiagnosisInput, run_diagnosis

TEXTS = ["ça grince quand je freine", "le moteur chauffe", "la batterie est à plat le matin", "le volant vibre"] * 3


def _diagnose(text: str) -> str:
    with SessionLocal() as db:
        return run_diagnosis(db, DiagnosisInput(text=text), use_llm=False)[0]["status"]


def test_diagnostics_simultanes_pendant_la_reconstruction_des_index():
    # Forcer la reconstruction des index au prochain appel, comme juste après un démarrage
    retrieval.index.signature = None
    retrieval.domain_index.signature = None
    with ThreadPoolExecutor(max_workers=6) as pool:
        statuses = list(pool.map(_diagnose, TEXTS))
    assert all(s in ("ok", "clarify", "unknown") for s in statuses), statuses


def test_prechargement_sans_erreur():
    warmup()  # ne lève jamais : journalise un avertissement en cas d'échec
    assert retrieval.index.signature is not None  # l'index des mots-clés est construit
