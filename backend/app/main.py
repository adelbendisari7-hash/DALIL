"""API DALIL — préfixe /api/v1, documentation OpenAPI sur /docs."""
import logging
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import admin, auth, public, shops

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

for r in (public.router, shops.router, auth.router, admin.router):
    app.include_router(r, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


def warmup() -> None:
    """Charge classifieur, index de recherche et modèles de vecteurs avec un diagnostic factice. Les vrais
    diagnostics qui arrivent pendant ce temps attendent la fin du chargement (verrou) au lieu de le refaire."""
    from .db import SessionLocal
    from .services.diagnosis.pipeline import DiagnosisInput, run_diagnosis

    log = logging.getLogger("dalil.warmup")
    t0 = time.time()
    try:
        with SessionLocal() as db:
            run_diagnosis(db, DiagnosisInput(text="bruit métallique au freinage"), use_llm=False)
        log.warning("Modèles de diagnostic prêts en %.0f s", time.time() - t0)
    except Exception as e:  # base vide ou pas encore migrée : le premier diagnostic chargera les modèles
        log.warning("Préchargement des modèles impossible (%s)", e)


@app.on_event("startup")
def start_warmup() -> None:
    if get_settings().warmup:
        threading.Thread(target=warmup, name="dalil-warmup", daemon=True).start()
