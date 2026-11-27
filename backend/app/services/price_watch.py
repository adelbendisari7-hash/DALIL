"""Prix suivis (28/11/2026) : le client suit une pièce ; DALIL le prévient quand le prix le plus bas des catalogues
passe sous son prix de référence, ou quand un magasin propose la pièce alors qu'aucun n'avait de prix. « Vu » prend le
prix du moment comme nouvelle référence. Prix lus dans les catalogues, jamais estimés."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import PartCategory, PriceWatch, User
from . import price_history

MAX_WATCHES = 30


def watch_out(db: Session, w: PriceWatch) -> dict:
    cat = db.get(PartCategory, w.category_id)
    low = price_history.lowest(db, w.category_id)
    ref = w.reference_price
    if low is None:
        alert = None
    elif ref is None:
        alert = "available"                      # un magasin propose maintenant la pièce
    elif low["price"] < ref:
        alert = "drop"
    else:
        alert = None
    return {"id": w.id, "category_id": w.category_id, "part": cat.name_fr if cat else None, "variant_id": w.variant_id,
            "reference_price": ref, "lowest": low, "alert": alert,
            "drop_pct": round((ref - low["price"]) / ref * 100) if alert == "drop" and ref else None,
            "since": w.created_at.date().isoformat()}


def watches(db: Session, user: User) -> list[dict]:
    rows = db.scalars(select(PriceWatch).where(PriceWatch.user_id == user.id).order_by(PriceWatch.id.desc()))
    return [watch_out(db, w) for w in rows]


def alert_count(db: Session, user: User) -> int:
    return sum(1 for w in watches(db, user) if w["alert"])
