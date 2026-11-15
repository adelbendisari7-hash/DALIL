"""Connexion par code à usage unique reçu par SMS."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import OtpCode, Shop, User
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
            "consent": u.consent_at is not None}


@router.post("/otp/request", dependencies=[Depends(otp_limiter)])
def otp_request(body: OtpRequest, db: Session = Depends(get_db)):
    phone = normalize_phone(body.phone)
    db.execute(update(OtpCode).where(OtpCode.phone == phone, OtpCode.used.is_(False)).values(used=True))
    code = new_otp()
    db.add(OtpCode(phone=phone, code_hash=hash_code(phone, code),
                   expires_at=datetime.now(timezone.utc) + timedelta(minutes=get_settings().otp_ttl_minutes)))
    db.commit()
    get_sms_sender().send(phone, f"DALIL : votre code est {code}")
    return {"sent": True, "phone": phone}


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
    user.phone = f"supprime-{user.id}"
    user.name, user.role, user.consent_at = None, "driver", None
    db.commit()
