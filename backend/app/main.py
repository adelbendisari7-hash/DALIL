"""API DALIL — préfixe /api/v1, documentation OpenAPI sur /docs."""
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
