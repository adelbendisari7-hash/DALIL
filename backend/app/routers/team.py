"""Équipe d'un magasin (plan côté magasin, phase 3) : tout est réservé au gérant. Aucune route d'administration :
l'équipe DALIL n'intervient pas dans l'équipe d'un magasin (décision du 27/11/2026)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ShopActivity, ShopMember, User
from ..security import current_user, normalize_phone, verify_password
from ..services import shop_team as team

router = APIRouter(prefix="/shops/{shop_id}/team")


def _perms(v: list[str]) -> list[str]:
    bad = [p for p in v if p not in team.PERMISSIONS]
    if bad:
        raise ValueError(f"Accès inconnu : {', '.join(bad)}")
    return [p for p in team.PERMISSIONS if p in v]   # ordre fixe, sans doublon


class MemberIn(BaseModel):
    phone: str = Field(..., max_length=24)
    permissions: list[str] = Field(default_factory=lambda: list(team.TEMPLATES["vendeur"]))

    @field_validator("permissions")
    @classmethod
    def check_permissions(cls, v):
        return _perms(v)


class MemberPatch(BaseModel):
    permissions: list[str] | None = None
    status: str | None = Field(None, pattern="^(active|suspended)$")

    @field_validator("permissions")
    @classmethod
    def check_permissions(cls, v):
        return v if v is None else _perms(v)


class TransferIn(BaseModel):
    user_id: int
    password: str = Field(..., max_length=128)


def _member_out(db: Session, m: ShopMember) -> dict:
    u = db.get(User, m.user_id)
    return {"user_id": m.user_id, "name": u.name if u else None, "phone": u.phone if u else None,
            "permissions": m.permissions, "status": m.status, "created_at": m.created_at.isoformat()}


def _member(db: Session, shop_id: int, user_id: int) -> ShopMember:
    m = db.scalar(select(ShopMember).where(ShopMember.shop_id == shop_id, ShopMember.user_id == user_id))
    if not m:
        raise HTTPException(404, "Cette personne ne fait pas partie de l'équipe")
    return m


@router.get("")
def team_list(shop_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    shop = team.shop_for(db, shop_id, user, "team")
    members = db.scalars(select(ShopMember).where(ShopMember.shop_id == shop.id).order_by(ShopMember.created_at))
    return {"manager": {"user_id": user.id, "name": user.name, "phone": user.phone},
            "members": [_member_out(db, m) for m in members],
            "permissions": list(team.PERMISSIONS), "templates": team.TEMPLATES}


@router.post("", status_code=201)
def team_add(shop_id: int, body: MemberIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """L'employé crée d'abord son compte DALIL ; le gérant tape son numéro (pas de SMS pour inviter)."""
    shop = team.shop_for(db, shop_id, user, "team")
    other = db.scalar(select(User).where(User.phone == normalize_phone(body.phone)))
    if other is None:
        raise HTTPException(404, "Aucun compte DALIL avec ce numéro : demandez à votre employé de créer son compte, puis réessayez")
    if other.id == user.id:
        raise HTTPException(422, "Vous êtes déjà le gérant de ce magasin")
    if db.scalar(select(ShopMember).where(ShopMember.shop_id == shop.id, ShopMember.user_id == other.id)):
        raise HTTPException(409, "Cette personne fait déjà partie de l'équipe")
    m = ShopMember(shop_id=shop.id, user_id=other.id, permissions=body.permissions, added_by=user.id)
    db.add(m)
    team.log(db, shop.id, user, "team.add", other.name or other.phone)
    db.commit()
    return _member_out(db, m)


@router.patch("/{member_id}")
def team_update(shop_id: int, member_id: int, body: MemberPatch, db: Session = Depends(get_db), user: User = Depends(current_user)):
    shop = team.shop_for(db, shop_id, user, "team")
    m = _member(db, shop.id, member_id)
    if body.permissions is not None:
        m.permissions = body.permissions
    if body.status is not None:
        m.status = body.status
    who = db.get(User, m.user_id)
    team.log(db, shop.id, user, "team.update", f"{who.name if who else ''} : {', '.join(m.permissions) or 'aucun accès'} ({m.status})")
    db.commit()
    return _member_out(db, m)


@router.delete("/{member_id}", status_code=204)
def team_remove(shop_id: int, member_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Retiré : l'accès s'arrête immédiatement (chaque requête relit l'équipe)."""
    shop = team.shop_for(db, shop_id, user, "team")
    m = _member(db, shop.id, member_id)
    who = db.get(User, m.user_id)
    team.log(db, shop.id, user, "team.remove", who.name if who else None)
    db.delete(m)
    db.commit()


@router.post("/transfer")
def team_transfer(shop_id: int, body: TransferIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Passer la main à un membre de l'équipe, confirmé par le mot de passe du gérant. L'ancien gérant reste dans
    l'équipe avec les accès « Responsable » ; le nouveau gérant pourra les changer ou le retirer."""
    shop = team.shop_for(db, shop_id, user, "team")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(403, "Mot de passe incorrect")
    m = _member(db, shop.id, body.user_id)
    new_manager = db.get(User, m.user_id)
    db.delete(m)
    db.flush()
    shop.owner_user_id = new_manager.id
    if new_manager.role == "driver":
        new_manager.role = "shop_owner"
    db.add(ShopMember(shop_id=shop.id, user_id=user.id, permissions=list(team.TEMPLATES["responsable"]), added_by=new_manager.id))
    team.log(db, shop.id, user, "team.transfer", new_manager.name or new_manager.phone)
    db.commit()
    return {"manager_user_id": new_manager.id}


ACTIONS = {
    "profile.update": "a modifié la fiche du magasin", "product.create": "a ajouté un produit",
    "product.update": "a modifié un produit", "product.quick": "a changé prix ou stock",
    "product.delete": "a retiré un produit", "product.import": "a importé un fichier", "request.answer": "a répondu à une demande",
    "team.add": "a ajouté à l'équipe", "team.update": "a changé les accès de", "team.remove": "a retiré de l'équipe",
    "team.transfer": "a passé la main à",
}


@router.get("/activity")
def team_activity(shop_id: int, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Journal du magasin (100 dernières actions) : qui a fait quoi. Réservé au gérant."""
    shop = team.shop_for(db, shop_id, user, "team")
    rows = db.scalars(select(ShopActivity).where(ShopActivity.shop_id == shop.id)
                      .order_by(ShopActivity.created_at.desc(), ShopActivity.id.desc()).limit(min(limit, 200)))
    out = []
    for a in rows:
        who = db.get(User, a.user_id) if a.user_id else None
        out.append({"at": a.created_at.isoformat(), "who": (who.name or who.phone) if who else "compte supprimé",
                    "action": a.action, "label": ACTIONS.get(a.action, a.action), "target": a.target})
    return out
