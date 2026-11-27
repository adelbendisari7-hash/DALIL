"""Papiers des voitures du compte client (28/11/2026) : contrôle technique et assurance.

Le client note la date où le papier a été fait et la date jusqu'à laquelle il est valable, lue sur le procès-verbal
du contrôle ou l'attestation d'assurance : DALIL ne devine pas la durée (elle dépend de la voiture et du contrat).
Rappels : dès 30 jours avant la fin (« bientôt »), urgent à 7 jours, puis « expiré ».
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import UserVehicle, VehicleDocument

KINDS = ("controle", "assurance")
SOON_DAYS = 30
URGENT_DAYS = 7


def status(valid_until: date, today: date | None = None) -> tuple[str, int]:
    days = (valid_until - (today or date.today())).days
    if days < 0:
        return "expired", days
    if days <= URGENT_DAYS:
        return "urgent", days
    if days <= SOON_DAYS:
        return "soon", days
    return "ok", days


def doc_out(d: VehicleDocument, today: date | None = None) -> dict:
    st, days = status(d.valid_until, today)
    return {"id": d.id, "kind": d.kind, "done_on": d.done_on.isoformat() if d.done_on else None,
            "valid_until": d.valid_until.isoformat(), "provider": d.provider, "price": d.price, "note": d.note,
            "status": st, "days_left": days}


def history(db: Session, car: UserVehicle) -> list[VehicleDocument]:
    return list(db.scalars(select(VehicleDocument).where(VehicleDocument.user_vehicle_id == car.id)
                           .order_by(VehicleDocument.valid_until.desc(), VehicleDocument.id.desc())))


def current(db: Session, car: UserVehicle, today: date | None = None) -> dict[str, dict | None]:
    """Le papier en cours pour chaque sorte : celui qui finit le plus tard (un renouvellement noté en avance compte)."""
    docs = history(db, car)
    return {k: next((doc_out(d, today) for d in docs if d.kind == k), None) for k in KINDS}


def alerts(db: Session, car: UserVehicle, today: date | None = None) -> list[dict]:
    """Papiers qui finissent dans 30 jours au plus, ou déjà expirés : rappel sur l'accueil et l'onglet Compte."""
    return [d for d in current(db, car, today).values() if d and d["status"] != "ok"]
