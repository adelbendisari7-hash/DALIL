"""Carnet transmis à la revente (28/11/2026), seulement avec l'accord du vendeur.

Le vendeur crée un code (8 caractères, valable 7 jours) ; l'acheteur le saisit avec le matricule de la voiture (il a
la voiture devant lui : un code seul ne suffit pas). Seule l'empreinte du code est gardée, et les essais sont limités.

Passe à l'acheteur : la voiture (matricule, modèle, kilométrage, numéro de châssis), le carnet d'entretien (dates,
kilométrages, opérations, garages) et le contrôle technique. Les prix et les remarques du carnet seulement si le
vendeur l'a choisi. Ne passe pas : l'assurance (contrat du vendeur), l'historique des diagnostics du vendeur (détaché
de la voiture), le surnom de la voiture.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import DiagnosisSession, MaintenanceVisit, User, UserVehicle, VehicleDocument, VehicleTransfer

ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"   # sans 0/O, 1/I/L : lisible au téléphone
VALID_DAYS = 7


def code_hash(code: str) -> str:
    clean = "".join(ch for ch in code.upper() if ch in ALPHABET)
    return hashlib.sha256(f"dalil-transfert:{clean}".encode()).hexdigest()


def new_code() -> str:
    raw = "".join(secrets.choice(ALPHABET) for _ in range(8))
    return f"{raw[:4]}-{raw[4:]}"


def _aware(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def pending(db: Session, car: UserVehicle) -> VehicleTransfer | None:
    t = db.scalar(select(VehicleTransfer).where(VehicleTransfer.user_vehicle_id == car.id, VehicleTransfer.status == "pending")
                  .order_by(VehicleTransfer.id.desc()))
    if t is not None and _aware(t.expires_at) < datetime.now(timezone.utc):
        t.status = "expired"
        return None
    return t


def create(db: Session, car: UserVehicle, user: User, include_prices: bool) -> tuple[VehicleTransfer, str]:
    old = pending(db, car)
    if old is not None:
        old.status = "cancelled"   # un nouveau code remplace l'ancien
    code = new_code()
    t = VehicleTransfer(user_vehicle_id=car.id, from_user_id=user.id, code_hash=code_hash(code),
                        include_prices=include_prices, status="pending",
                        expires_at=datetime.now(timezone.utc) + timedelta(days=VALID_DAYS))
    db.add(t)
    return t, code


def find(db: Session, code: str, plate: str) -> tuple[VehicleTransfer, UserVehicle]:
    """Transfert en attente pour ce code ET ce matricule ; sinon une seule réponse, qui ne dévoile rien."""
    t = db.scalar(select(VehicleTransfer).where(VehicleTransfer.code_hash == code_hash(code), VehicleTransfer.status == "pending"))
    car = db.get(UserVehicle, t.user_vehicle_id) if t else None
    if t is None or car is None or car.plate != plate or _aware(t.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(404, "Code ou matricule incorrect, ou code expiré. Demandez un nouveau code au vendeur.")
    return t, car


def preview(db: Session, t: VehicleTransfer, car: UserVehicle) -> dict:
    from ..routers.account import vehicle_label
    visits = list(db.scalars(select(MaintenanceVisit).where(MaintenanceVisit.user_vehicle_id == car.id)))
    ct = list(db.scalars(select(VehicleDocument).where(VehicleDocument.user_vehicle_id == car.id, VehicleDocument.kind == "controle")))
    return {"vehicle": vehicle_label(car), "mileage_km": car.mileage_km, "visits": len(visits),
            "last_visit": max((v.done_on for v in visits), default=None), "controles": len(ct),
            "include_prices": t.include_prices, "expires_at": _aware(t.expires_at).isoformat()}


def accept(db: Session, t: VehicleTransfer, car: UserVehicle, buyer: User) -> UserVehicle:
    if car.user_id == buyer.id:
        raise HTTPException(409, "Cette voiture est déjà dans votre compte.")
    for s in db.scalars(select(DiagnosisSession).where(DiagnosisSession.user_vehicle_id == car.id)):
        s.user_vehicle_id = None          # l'historique des diagnostics du vendeur reste le sien
    for d in db.scalars(select(VehicleDocument).where(VehicleDocument.user_vehicle_id == car.id, VehicleDocument.kind != "controle")):
        db.delete(d)                      # l'assurance est le contrat du vendeur
    if not t.include_prices:
        for v in db.scalars(select(MaintenanceVisit).where(MaintenanceVisit.user_vehicle_id == car.id)):
            v.price, v.note = None, None
    car.user_id, car.nickname = buyer.id, None
    t.status, t.accepted_by, t.accepted_at = "accepted", buyer.id, datetime.now(timezone.utc)
    return car
