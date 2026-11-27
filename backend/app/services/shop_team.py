"""Équipe d'un magasin (plan côté magasin, phase 3 ; décision du 27/11/2026) : le gérant ajoute autant d'employés
qu'il veut et coche pour chacun ce qu'il peut faire. Lui seul gère l'équipe ; **l'équipe DALIL n'intervient pas**
(aucune route d'administration, et le rôle administrateur ne donne aucun droit sur l'équipe d'un magasin).
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Shop, ShopActivity, ShopMember, User

# Accès qu'un gérant peut donner, dans l'ordre d'affichage
PERMISSIONS = ("requests", "prices", "products", "products_delete", "stats", "profile")
TEMPLATES = {
    "vendeur": ["requests", "prices"],                                   # demandes, prix et stock
    "responsable": ["requests", "prices", "products", "products_delete", "stats", "profile"],   # tout sauf l'équipe
}
# Accès nécessaire par action : changer prix et stock, c'est aussi « prices » ; ajouter ou modifier un produit, « products »
MANAGER = "manager"


def membership(db: Session, shop: Shop, user: User) -> tuple[str | None, list[str]]:
    """(« manager », tous les accès) pour le gérant ; (« employee », ses accès) pour un employé actif ; (None, [])."""
    if shop.owner_user_id == user.id:
        return MANAGER, list(PERMISSIONS)
    m = db.scalar(select(ShopMember).where(ShopMember.shop_id == shop.id, ShopMember.user_id == user.id))
    if m and m.status == "active":
        return "employee", [p for p in m.permissions if p in PERMISSIONS]
    return None, []


def shop_for(db: Session, shop_id: int, user: User, perm: str) -> Shop:
    """Magasin si `user` a l'accès `perm` (le gérant les a tous). L'administrateur garde la main sur les données du
    magasin (modération), jamais sur son équipe (`perm == "team"`)."""
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(404, "Magasin inconnu")
    role, perms = membership(db, shop, user)
    if perm == "team":
        if role != MANAGER:
            raise HTTPException(403, "Seul le gérant du magasin gère son équipe")
        return shop
    if role is None and user.role == "admin":
        return shop
    if role is None:
        raise HTTPException(403, "Ce magasin ne vous appartient pas")
    if perm not in perms:
        raise HTTPException(403, "Le gérant ne vous a pas donné cet accès")
    return shop


def my_shops(db: Session, user: User) -> list[tuple[Shop, str, list[str]]]:
    """Magasins que gère `user` ou où il est employé actif, avec son rôle et ses accès."""
    out = [(s, MANAGER, list(PERMISSIONS)) for s in db.scalars(select(Shop).where(Shop.owner_user_id == user.id))]
    for m in db.scalars(select(ShopMember).where(ShopMember.user_id == user.id, ShopMember.status == "active")):
        shop = db.get(Shop, m.shop_id)
        if shop and shop.owner_user_id != user.id:
            out.append((shop, "employee", [p for p in m.permissions if p in PERMISSIONS]))
    return out


def log(db: Session, shop_id: int, user: User | None, action: str, target: str | None = None) -> None:
    db.add(ShopActivity(shop_id=shop_id, user_id=user.id if user else None, action=action, target=(target or "")[:200] or None))
