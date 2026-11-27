"""API DALIL — préfixe /api/v1, documentation OpenAPI sur /docs."""
import logging
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import account, admin, auth, public, shops

app = FastAPI(
    title="DALIL API",
    version="0.1.0",
    description="Diagnostic automobile assisté et localisation de pièces détachées à Oran.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (public.router, shops.router, auth.router, account.router, admin.router):
    app.include_router(r, prefix="/api/v1")


# Modèles de diagnostic chargés ? Le site affiche « DALIL se prépare » tant que ce n'est pas le cas.
READY = threading.Event()


@app.get("/health")
@app.get("/api/v1/health")   # même adresse que le reste de l'API, pour le relais du site
def health():
    return {"status": "ok", "ready": READY.is_set()}


def warmup() -> None:
    """Charge classifieur, index de recherche et modèles de vecteurs avec un diagnostic factice. Les vrais
    diagnostics qui arrivent pendant ce temps attendent la fin du chargement (verrou) au lieu de le refaire."""
    from .db import SessionLocal
    from .services.diagnosis.classifier import get_classifier
    from .services.diagnosis.embeddings import get_embedder, get_reranker
    from .services.diagnosis.pipeline import DiagnosisInput, run_diagnosis
    from .services.diagnosis.retrieval import MODELS_LOCK

    log = logging.getLogger("dalil.warmup")
    t0 = time.time()
    try:
        with MODELS_LOCK:   # les vrais diagnostics attendent ici au lieu de charger les modèles une seconde fois
            # Les trois modèles se chargent en parallèle : 31-39 s -> 13-18 s sur le portable (27/11/2026).
            loaders = [get_classifier]
            if get_settings().retrieval_mode == "hybrid":
                loaders += [get_embedder, get_reranker]
            threads = [threading.Thread(target=f, name=f"dalil-{f.__name__}") for f in loaders]
            for th in threads:
                th.start()
            for th in threads:
                th.join()
            with SessionLocal() as db:   # index des mots-clés et vecteurs, avec un diagnostic factice
                run_diagnosis(db, DiagnosisInput(text="bruit métallique au freinage"), use_llm=False)
        log.warning("Modèles de diagnostic prêts en %.0f s", time.time() - t0)
    except Exception as e:  # base vide ou pas encore migrée : le premier diagnostic chargera les modèles
        log.warning("Préchargement des modèles impossible (%s)", e)
    finally:
        READY.set()   # même en cas d'échec : ne pas annoncer un chargement qui n'aura pas lieu


@app.on_event("startup")
def start_warmup() -> None:
    if get_settings().warmup:
        threading.Thread(target=warmup, name="dalil-warmup", daemon=True).start()
    else:
        READY.set()
