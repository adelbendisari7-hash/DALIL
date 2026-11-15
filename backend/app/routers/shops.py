"""Magasins : recommandation (F7), fiches, espace magasin (F11, F12), contacts (F8), retours (F9), demandes (F16)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (
    ContactEvent,
    DiagnosisSession,
    Feedback,
    PartCategory,
    PartRequest,
    Product,
    ProductFitment,
    RequestResponse,
    Shop,
    ShopBrand,
    ShopCategory,
    User,
    VehicleVariant,
)
from ..schemas import (
    ContactEventIn,
    FeedbackIn,
    PartRequestIn,
    PartResponseIn,
    ProductIn,
    ShopIn,
    ShopPatch,
    shop_out,
)
from ..security import current_user, current_user_optional, normalize_phone, require_role
from ..services.imports import import_products, read_table
from ..services.recommendation import RECOMMENDABLE_STATUSES, category_lineage, recommend

router = APIRouter()
MAX_IMPORT_BYTES = 5 * 1024 * 1024


def _mark_observed(db: Session, shop_id: int, category_id: int | None, variant_id: int | None) -> None:
    """Écrit source = observed quand un magasin a réellement la pièce (section 8, règles)."""
    now = datetime.now(timezone.utc)
    if category_id:
        sc = db.get(ShopCategory, (shop_id, category_id))
        if sc is None:
            db.add(ShopCategory(shop_id=shop_id, category_id=category_id, source="observed", confidence=0.8, confirmed_at=now))
        else:
            sc.confirmed_at = now
    if variant_id:
        brand_id = db.get(VehicleVariant, variant_id).model.brand_id
        sb = db.get(ShopBrand, (shop_id, brand_id))
        if sb is None:
            db.add(ShopBrand(shop_id=shop_id, brand_id=brand_id, source="observed", confirmed_at=now))
        else:
            sb.confirmed_at = now


def _set_links(db: Session, shop: Shop, brand_ids: list[int] | None, category_ids: list[int] | None, source: str) -> None:
    now = datetime.now(timezone.utc)
    if brand_ids is not None:
        keep = set(brand_ids)
        shop.brands[:] = [b for b in shop.brands if b.brand_id in keep]
        have = {b.brand_id for b in shop.brands}
        shop.brands += [ShopBrand(brand_id=i, source=source, confirmed_at=now) for i in keep - have]
        for b in shop.brands:
            b.confirmed_at = now
    if category_ids is not None:
        keep = set(category_ids)
        if any(db.get(PartCategory, i) is None for i in keep):
            raise HTTPException(422, "Famille de pièces inconnue")
        shop.categories[:] = [c for c in shop.categories if c.category_id in keep]
        have = {c.category_id for c in shop.categories}
        shop.categories += [ShopCategory(category_id=i, source=source, confirmed_at=now) for i in keep - have]
        for c in shop.categories:
            c.confirmed_at = now


def _owned_shop(db: Session, shop_id: int, user: User) -> Shop:
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(404, "Magasin inconnu")
    if user.role != "admin" and shop.owner_user_id != user.id:
        raise HTTPException(403, "Ce magasin ne vous appartient pas")
    return shop


# --- Public ---------------------------------------------------------------

@router.get("/shops/recommend")
def shops_recommend(
    category_id: int, variant_id: int | None = None,
    lat: float | None = Query(None, ge=-90, le=90), lng: float | None = Query(None, ge=-180, le=180),
    limit: int = Query(20, le=50), db: Session = Depends(get_db),
):
    if not db.get(PartCategory, category_id):
        raise HTTPException(404, "Famille de pièces inconnue")
    out = []
    for shop, sc in recommend(db, category_id, variant_id, lat, lng, limit):
        out.append({**shop_out(shop, full=False), "score": sc.score, "breakdown": sc.breakdown,
                    "reasons": sc.reasons, "stale": sc.stale, "distance_km": sc.distance_km})
    return out


@router.get("/shops")
def shops_map(db: Session = Depends(get_db)):
    rows = db.scalars(select(Shop).where(Shop.status.in_(RECOMMENDABLE_STATUSES)))
    return [shop_out(s, full=False) for s in rows]


@router.get("/shops/mine")
def shops_mine(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [shop_out(s) for s in db.scalars(select(Shop).where(Shop.owner_user_id == user.id))]


@router.get("/shops/claimable")
def shops_claimable(phone: str, db: Session = Depends(get_db)):
    """Fiches créées par l'équipe que le magasin peut revendiquer avec son numéro."""
    p = normalize_phone(phone)
    return [shop_out(s, full=False) for s in db.scalars(select(Shop).where(Shop.phone == p, Shop.owner_user_id.is_(None)))]


@router.get("/shops/{shop_id}")
def shop_detail(shop_id: int, db: Session = Depends(get_db), user: User | None = Depends(current_user_optional)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(404, "Magasin inconnu")
    if shop.status not in RECOMMENDABLE_STATUSES and not (user and (user.role == "admin" or user.id == shop.owner_user_id)):
        raise HTTPException(404, "Magasin inconnu")
    return shop_out(shop)


@router.get("/shops/{shop_id}/products")
def shop_products(shop_id: int, db: Session = Depends(get_db)):
    rows = db.scalars(select(Product).where(Product.shop_id == shop_id).order_by(Product.updated_at.desc()))
    return [
        {"id": p.id, "title": p.title, "category_id": p.category_id, "oem_ref": p.oem_ref, "part_brand": p.part_brand,
         "condition": p.condition, "price": p.price, "in_stock": p.in_stock, "variant_ids": [f.variant_id for f in p.fitments]}
        for p in rows
    ]


@router.post("/contact-events", status_code=201)
def contact_event(body: ContactEventIn, db: Session = Depends(get_db)):
    if not db.get(Shop, body.shop_id):
        raise HTTPException(404, "Magasin inconnu")
    ev = ContactEvent(**body.model_dump())
    db.add(ev)
    db.commit()
    return {"id": ev.id}


@router.post("/feedback", status_code=201)
def feedback(body: FeedbackIn, db: Session = Depends(get_db)):
    if body.shop_id and not db.get(Shop, body.shop_id):
        raise HTTPException(404, "Magasin inconnu")
    fb = Feedback(**body.model_dump())
    db.add(fb)
    if body.part_found and body.shop_id:
        variant_id = None
        if body.session_id:
            sess = db.get(DiagnosisSession, body.session_id)
            variant_id = sess.variant_id if sess else None
        _mark_observed(db, body.shop_id, body.category_id, variant_id)
    db.commit()
    return {"id": fb.id}


# --- Espace magasin -------------------------------------------------------

@router.post("/shops", status_code=201)
def shop_create(body: ShopIn, db: Session = Depends(get_db), user: User = Depends(require_role("shop_owner"))):
    """Inscription en libre-service : la fiche attend la validation de l'administrateur."""
    data = body.model_dump(exclude={"brand_ids", "category_ids", "surveyor", "survey"})
    data["phone"] = normalize_phone(body.phone) if body.phone else user.phone
    data["whatsapp"] = normalize_phone(body.whatsapp) if body.whatsapp else data["phone"]
    shop = Shop(**data, status="draft", source="declared", owner_user_id=user.id)
    db.add(shop)
    db.flush()
    _set_links(db, shop, body.brand_ids, body.category_ids, "declared")
    db.commit()
    return shop_out(shop)


@router.patch("/shops/{shop_id}")
def shop_patch(shop_id: int, body: ShopPatch, db: Session = Depends(get_db), user: User = Depends(current_user)):
    shop = _owned_shop(db, shop_id, user)
    data = body.model_dump(exclude_unset=True, exclude={"brand_ids", "category_ids"})
    for k in ("phone", "whatsapp"):
        if data.get(k):
            data[k] = normalize_phone(data[k])
    for k, v in data.items():
        setattr(shop, k, v)
    _set_links(db, shop, body.brand_ids, body.category_ids, "declared")
    db.commit()
    return shop_out(shop)


@router.post("/shops/{shop_id}/claim")
def shop_claim(shop_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Revendication d'une fiche créée par l'équipe : le numéro de connexion doit être celui de la fiche."""
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(404, "Magasin inconnu")
    if shop.owner_user_id:
        raise HTTPException(409, "Fiche déjà revendiquée")
    if shop.phone != user.phone:
        raise HTTPException(403, "Le numéro de la fiche ne correspond pas à votre numéro ; contactez l'équipe DALIL")
    shop.owner_user_id = user.id
    if shop.status == "verified":
        shop.status = "claimed"
    if user.role == "driver":
        user.role = "shop_owner"
    db.commit()
    return shop_out(shop)


def _product_payload(db: Session, body: ProductIn) -> None:
    if not db.get(PartCategory, body.category_id):
        raise HTTPException(422, "Famille de pièces inconnue")
    for vid in body.variant_ids:
        if not db.get(VehicleVariant, vid):
            raise HTTPException(422, f"Véhicule inconnu : {vid}")


@router.post("/shops/{shop_id}/products", status_code=201)
def product_create(shop_id: int, body: ProductIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    shop = _owned_shop(db, shop_id, user)
    _product_payload(db, body)
    p = Product(shop_id=shop.id, **body.model_dump(exclude={"variant_ids"}))
    p.fitments = [ProductFitment(variant_id=v) for v in set(body.variant_ids)]
    db.add(p)
    db.commit()
    return {"id": p.id}


@router.put("/shops/{shop_id}/products/{product_id}")
def product_update(shop_id: int, product_id: int, body: ProductIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _owned_shop(db, shop_id, user)
    p = db.get(Product, product_id)
    if not p or p.shop_id != shop_id:
        raise HTTPException(404, "Produit inconnu")
    _product_payload(db, body)
    for k, v in body.model_dump(exclude={"variant_ids"}).items():
        setattr(p, k, v)
    p.fitments = [ProductFitment(variant_id=v) for v in set(body.variant_ids)]
    db.commit()
    return {"id": p.id}


@router.delete("/shops/{shop_id}/products/{product_id}", status_code=204)
def product_delete(shop_id: int, product_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _owned_shop(db, shop_id, user)
    p = db.get(Product, product_id)
    if not p or p.shop_id != shop_id:
        raise HTTPException(404, "Produit inconnu")
    db.delete(p)
    db.commit()


@router.post("/shops/{shop_id}/products/import")
async def product_import(shop_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(current_user)):
    shop = _owned_shop(db, shop_id, user)
    content = await file.read()
    if len(content) > MAX_IMPORT_BYTES:
        raise HTTPException(413, "Fichier trop lourd (5 Mo maximum)")
    rows = read_table(content, file.filename or "import.csv")
    rep = import_products(db, shop, rows)
    db.commit()
    return {"created": rep.created, "updated": rep.updated, "errors": rep.errors, "total": len(rows)}


# --- Demandes diffusées (F16) ---------------------------------------------

@router.post("/part-requests", status_code=201)
def part_request_create(body: PartRequestIn, db: Session = Depends(get_db), user: User | None = Depends(current_user_optional)):
    if not db.get(PartCategory, body.category_id):
        raise HTTPException(404, "Famille de pièces inconnue")
    req = PartRequest(**body.model_dump(), user_id=user.id if user else None)
    db.add(req)
    db.flush()
    ancestors, _ = category_lineage(db, body.category_id)
    shop_ids = set(db.scalars(select(ShopCategory.shop_id).where(ShopCategory.category_id.in_(ancestors))))
    if body.variant_id:
        brand_id = db.get(VehicleVariant, body.variant_id).model.brand_id
        shop_ids &= set(db.scalars(select(ShopBrand.shop_id).where(ShopBrand.brand_id == brand_id)))
    owned = db.scalars(select(Shop).where(Shop.id.in_(shop_ids), Shop.status.in_(RECOMMENDABLE_STATUSES), Shop.owner_user_id.is_not(None)))
    n = 0
    for shop in owned:
        db.add(RequestResponse(request_id=req.id, shop_id=shop.id))
        n += 1
    db.commit()
    return {"id": req.id, "notified_shops": n}


@router.get("/part-requests/inbox")
def part_request_inbox(db: Session = Depends(get_db), user: User = Depends(require_role("shop_owner"))):
    shop_ids = [s.id for s in db.scalars(select(Shop).where(Shop.owner_user_id == user.id))]
    rows = db.execute(
        select(RequestResponse, PartRequest).join(PartRequest, PartRequest.id == RequestResponse.request_id)
        .where(RequestResponse.shop_id.in_(shop_ids)).order_by(PartRequest.created_at.desc()).limit(100)
    ).all()
    out = []
    for rr, req in rows:
        cat = db.get(PartCategory, req.category_id)
        v = db.get(VehicleVariant, req.variant_id) if req.variant_id else None
        out.append({"request_id": req.id, "shop_id": rr.shop_id, "part": cat.name_fr,
                    "vehicle": f"{v.model.brand.name} {v.model.name} {v.engine}" if v else None,
                    "available": rr.available, "price": rr.price, "created_at": req.created_at.isoformat()})
    return out


@router.post("/part-requests/{request_id}/responses")
def part_request_respond(request_id: int, body: PartResponseIn, shop_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _owned_shop(db, shop_id, user)
    rr = db.get(RequestResponse, (request_id, shop_id))
    if not rr:
        raise HTTPException(404, "Demande inconnue pour ce magasin")
    rr.available, rr.price, rr.responded_at = body.available, body.price, datetime.now(timezone.utc)
    req = db.get(PartRequest, request_id)
    req.status = "answered"
    if body.available:
        _mark_observed(db, shop_id, req.category_id, req.variant_id)
    db.commit()
    return {"ok": True}


@router.get("/part-requests/{request_id}")
def part_request_status(request_id: int, db: Session = Depends(get_db)):
    req = db.get(PartRequest, request_id)
    if not req:
        raise HTTPException(404, "Demande inconnue")
    rows = db.scalars(select(RequestResponse).where(RequestResponse.request_id == request_id))
    return {"id": req.id, "status": req.status, "responses": [
        {"shop": shop_out(db.get(Shop, r.shop_id), full=False), "available": r.available, "price": r.price}
        for r in rows if r.responded_at
    ]}
