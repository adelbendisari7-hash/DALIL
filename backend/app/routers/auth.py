"""Connexion par code à usage unique reçu par SMS."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Commune, DiagnosisSession, OtpCode, PlateReport, Shop, User, UserVehicle
from ..schemas import MePatch, OtpRequest, OtpVerify
from ..security import (
    create_token,
    current_user,
    get_sms_sender,
    hash_code,
    new_otp,
    normalize_phone,
    otp_limiter,
)

router = APIRouter(prefix="/auth")
MAX_ATTEMPTS = 5


def _user_out(u: User) -> dict:
    return {"id": u.id, "phone": u.phone, "role": u.role, "name": u.name, "lang": u.lang,
            "consent": u.consent_at is not None,
            "first_name": u.first_name, "last_name": u.last_name, "email": u.email, "commune_id": u.commune_id,
            "birth_date": u.birth_date.isoformat() if u.birth_date else None,
            # compte client complet : prénom, nom (et téléphone, vérifié par SMS) ; le site le demande sinon
            "complete": bool(u.first_name and u.last_name)}


@router.post("/otp/request", dependencies=[Depends(otp_limiter)])
def otp_request(body: OtpRequest, db: Session = Depends(get_db)):
    phone = normalize_phone(body.phone)
    db.execute(update(OtpCode).where(OtpCode.phone == phone, OtpCode.used.is_(False)).values(used=True))
    code = new_otp()
    db.add(OtpCode(phone=phone, code_hash=hash_code(phone, code),
                   expires_at=datetime.now(timezone.utc) + timedelta(minutes=get_settings().otp_ttl_minutes)))
    db.commit()
    get_sms_sender().send(phone, f"DALIL : votre code est {code}")
    # « console » : aucun SMS ne part (prototype) ; la page de connexion dit où lire le code. Jamais le code lui-même.
    return {"sent": True, "phone": phone, "delivery": "console" if get_settings().sms_provider == "console" else "sms"}


@router.post("/otp/verify")
def otp_verify(body: OtpVerify, db: Session = Depends(get_db)):
    phone = normalize_phone(body.phone)
    otp = db.scalar(select(OtpCode).where(OtpCode.phone == phone, OtpCode.used.is_(False)).order_by(OtpCode.id.desc()))
    if otp is None:
        raise HTTPException(400, "Aucun code en attente : demandez un nouveau code")
    exp = otp.expires_at if otp.expires_at.tzinfo else otp.expires_at.replace(tzinfo=timezone.utc)
    if exp < datetime.now(timezone.utc) or otp.attempts >= MAX_ATTEMPTS:
        otp.used = True
        db.commit()
        raise HTTPException(400, "Code expiré : demandez un nouveau code")
    if otp.code_hash != hash_code(phone, body.code):
        otp.attempts += 1
        db.commit()
        raise HTTPException(400, "Code incorrect")
    otp.used = True
    user = db.scalar(select(User).where(User.phone == phone))
    if user is None:
        admins = {normalize_phone(p) for p in get_settings().admin_phones.split(",") if p.strip()}
        user = User(phone=phone, role="admin" if phone in admins else "driver")
        db.add(user)
    db.commit()
    return {"token": create_token(user), "user": _user_out(user)}


@router.get("/me")
def me(user: User = Depends(current_user)):
    return _user_out(user)


@router.patch("/me")
def me_patch(body: MePatch, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if body.name is not None:
        user.name = body.name
    if body.first_name is not None:
        user.first_name = body.first_name
    if body.last_name is not None:
        user.last_name = body.last_name
    if body.first_name is not None or body.last_name is not None:
        user.name = " ".join(x for x in (user.first_name, user.last_name) if x) or user.name
    if body.email is not None:
        user.email = body.email
    if body.commune_id is not None:
        if not db.get(Commune, body.commune_id):
            raise HTTPException(422, "Commune inconnue")
        user.commune_id = body.commune_id
    if body.birth_date is not None:
        user.birth_date = body.birth_date
    if body.lang is not None:
        user.lang = body.lang
    for field in body.clear:   # champs facultatifs effacés à la demande
        setattr(user, field, None)
    if body.role and user.role != "admin":
        user.role = body.role
    if body.consent:
        user.consent_at = datetime.now(timezone.utc)
    db.commit()
    return {"token": create_token(user), "user": _user_out(user)}


@router.delete("/me", status_code=204)
def me_delete(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Suppression du compte sur demande (loi 18-07). Les fiches magasin restent, sans propriétaire."""
    for shop in db.scalars(select(Shop).where(Shop.owner_user_id == user.id)):
        shop.owner_user_id = None
    # Voitures et matricules supprimés ; les diagnostics restent, anonymes (sans compte ni voiture)
    for s in db.scalars(select(DiagnosisSession).where(DiagnosisSession.user_id == user.id)):
        s.user_id, s.user_vehicle_id = None, None
    for v in db.scalars(select(UserVehicle).where(UserVehicle.user_id == user.id)):
        db.delete(v)
    for r in db.scalars(select(PlateReport).where(PlateReport.reporter_user_id == user.id)):
        r.reporter_user_id, r.message = None, None
    user.phone = f"supprime-{user.id}"
    user.name, user.role, user.consent_at = None, "driver", None
    user.first_name = user.last_name = user.email = None
    user.commune_id, user.birth_date = None, None
    db.commit()
