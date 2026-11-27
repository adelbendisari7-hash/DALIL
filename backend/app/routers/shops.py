"""Magasins : recommandation (F7), fiches, espace magasin (F11, F12), contacts (F8), retours (F9), demandes (F16)."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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
    ShopClaim,
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
    ProductPatch,
    ShopIn,
    ShopPatch,
    shop_out,
)
from ..security import client_hash, current_user, current_user_optional, feedback_limiter, normalize_phone, require_role
from ..services.imports import import_products, product_template, read_table
from ..services import shop_onboarding as onboarding
from ..services import shop_stats
from ..services import shop_team as team
from ..services.media import InvalidImage, storage
from ..services.recommendation import RECOMMENDABLE_STATUSES, category_lineage, offers, recommend

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


def _owned_shop(db: Session, shop_id: int, user: User, perm: str = "profile") -> Shop:
    """Magasin si l'utilisateur en est le gérant, ou un employé qui a l'accès `perm` (services/shop_team.py)."""
    return team.shop_for(db, shop_id, user, perm)


def _can_see(db: Session, shop: Shop, user: User | None) -> bool:
    """Fiche non validée : visible de son équipe et de l'administrateur seulement."""
    if shop.status in RECOMMENDABLE_STATUSES:
        return True
    return bool(user and (user.role == "admin" or team.membership(db, shop, user)[0]))


# --- Public ---------------------------------------------------------------

@router.get("/shops/recommend")
def shops_recommend(
    request: Request, category_id: int, variant_id: int | None = None,
    lat: float | None = Query(None, ge=-90, le=90), lng: float | None = Query(None, ge=-180, le=180),
    limit: int = Query(20, le=50), db: Session = Depends(get_db),
):
    if not db.get(PartCategory, category_id):
        raise HTTPException(404, "Famille de pièces inconnue")
    out = []
    for shop, sc in recommend(db, category_id, variant_id, lat, lng, limit):
        fast = shop_stats.fast_reply(db, shop.id)
        out.append({**shop_out(shop, full=False), "score": sc.score, "breakdown": sc.breakdown,
                    "reasons": sc.reasons + (["répond vite aux demandes"] if fast else []), "stale": sc.stale,
                    "distance_km": sc.distance_km, "fast_reply": fast})
    # Comparer les prix : meilleure offre du catalogue de chaque magasin
    best = offers(db, [x["id"] for x in out], category_id, variant_id)
    for x in out:
        x["offer"] = best.get(x["id"])
    # Statistiques des magasins (sans donnée personnelle) : apparitions, et pièce cherchée près de chez qui
    variant = db.get(VehicleVariant, variant_id) if variant_id else None
    shop_stats.record(db, [x["id"] for x in out], "impression", client_hash(request))
    shop_stats.record_search(db, category_id, variant.model.brand_id if variant else None, lat, lng)
    db.commit()
    return out


@router.get("/shops")
def shops_map(db: Session = Depends(get_db)):
    rows = db.scalars(select(Shop).where(Shop.status.in_(RECOMMENDABLE_STATUSES)))
    return [shop_out(s, full=False) for s in rows]


@router.get("/shops/mine")
def shops_mine(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{**shop_out(s), "my_role": role, "my_permissions": perms} for s, role, perms in team.my_shops(db, user)]


@router.get("/shops/claimable")
def shops_claimable(phone: str, db: Session = Depends(get_db)):
    """Fiches créées par l'équipe que le magasin peut revendiquer avec son numéro."""
    p = normalize_phone(phone)
    return [shop_out(s, full=False) for s in db.scalars(select(Shop).where(Shop.phone == p, Shop.owner_user_id.is_(None)))]


@router.get("/shops/nearby-claimable")
def shops_nearby_claimable(lat: float | None = Query(None, ge=-90, le=90), lng: float | None = Query(None, ge=-180, le=180),
                           phone: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Avant de créer une fiche : celles de l'équipe à moins de 150 m ou au même numéro, à revendiquer."""
    p = normalize_phone(phone) if phone else None
    return [{**shop_out(s, full=False), "distance_m": round(d * 1000) if d is not None else None}
            for s, d in onboarding.nearby_claimable(db, lat, lng, p)]


@router.get("/shops/{shop_id}")
def shop_detail(shop_id: int, request: Request, db: Session = Depends(get_db),
                user: User | None = Depends(current_user_optional)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(404, "Magasin inconnu")
    if not _can_see(db, shop, user):
        raise HTTPException(404, "Magasin inconnu")
    if not (user and (user.role == "admin" or team.membership(db, shop, user)[0])):   # l'équipe ne compte pas ses visites
        shop_stats.record(db, [shop.id], "view", client_hash(request))
        db.commit()
    return {**shop_out(shop), "fast_reply": shop_stats.fast_reply(db, shop.id)}


@router.get("/shops/{shop_id}/stats")
def shop_stats_view(shop_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Tableau de bord du magasin : 30 derniers jours comparés aux 30 précédents, et ce que cherchent les clients
    près du magasin. Gérant, et employés à qui il a donné l'accès « statistiques »."""
    return shop_stats.stats(db, _owned_shop(db, shop_id, user, "stats"))


@router.get("/catalog/template.xlsx")
def catalog_template(db: Session = Depends(get_db)):
    """Modèle Excel du catalogue : feuille « Catalogue » à remplir, plus « Exemples » et « Familles » (aide)."""
    return Response(product_template(db), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="dalil-modele-catalogue.xlsx"'})


@router.get("/shops/{shop_id}/products")
def shop_products(shop_id: int, db: Session = Depends(get_db), user: User | None = Depends(current_user_optional)):
    """Catalogue public d'un magasin visible (même règle que la fiche) ; le gérant et l'administrateur voient
    aussi celui d'une fiche en attente de validation."""
    shop = db.get(Shop, shop_id)
    if not shop or not _can_see(db, shop, user):
        raise HTTPException(404, "Magasin inconnu")
    rows = db.scalars(select(Product).where(Product.shop_id == shop_id).order_by(Product.updated_at.desc()))
    return [
        {"id": p.id, "title": p.title, "category_id": p.category_id, "oem_ref": p.oem_ref, "part_brand": p.part_brand,
         "condition": p.condition, "price": p.price, "in_stock": p.in_stock, "variant_ids": [f.variant_id for f in p.fitments],
         "photo_url": p.photo_url, "price_confirmed_at": p.price_confirmed_at.isoformat() if p.price_confirmed_at else None}
        for p in rows
    ]


@router.post("/contact-events", status_code=201, dependencies=[Depends(feedback_limiter)])
def contact_event(body: ContactEventIn, db: Session = Depends(get_db)):
    if not db.get(Shop, body.shop_id):
        raise HTTPException(404, "Magasin inconnu")
    ev = ContactEvent(**body.model_dump())
    db.add(ev)
    db.commit()
    return {"id": ev.id}


@router.post("/feedback", status_code=201, dependencies=[Depends(feedback_limiter)])
def feedback(body: FeedbackIn, request: Request, db: Session = Depends(get_db)):
    if body.shop_id and not db.get(Shop, body.shop_id):
        raise HTTPException(404, "Magasin inconnu")
    if body.category_id and not db.get(PartCategory, body.category_id):
        raise HTTPException(404, "Pièce inconnue")
    if body.session_id and not db.get(DiagnosisSession, body.session_id):
        raise HTTPException(404, "Diagnostic inconnu")
    fb = Feedback(**body.model_dump(), client_hash=client_hash(request))
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

def _phone_free(db: Session, phone: str | None, shop: Shop | None = None) -> None:
    """Le téléphone d'un magasin est unique. Pris par une fiche sans gérant : on propose de la revendiquer."""
    if not phone:
        return
    other = db.scalar(select(Shop).where(Shop.phone == phone))
    if other is not None and other is not shop:
        if other.owner_user_id is None:
            raise HTTPException(409, detail={"code": "shop_phone_claimable", "shop_id": other.id,
                                             "message": "Une fiche existe déjà avec ce numéro : revendiquez-la plutôt "
                                                        "que d'en créer une nouvelle."})
        raise HTTPException(409, detail=PHONE_TAKEN)


PHONE_TAKEN = {"code": "shop_phone_taken", "message": "Ce numéro est déjà celui d'un autre magasin inscrit sur DALIL."}


def _commit_shop(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:   # deux inscriptions simultanées du même numéro
        db.rollback()
        raise HTTPException(409, detail=PHONE_TAKEN) from None


@router.post("/shops", status_code=201)
def shop_create(body: ShopIn, db: Session = Depends(get_db), user: User = Depends(require_role("shop_owner"))):
    """Inscription en libre-service : la fiche attend la vérification par appel de l'administrateur."""
    data = body.model_dump(exclude={"brand_ids", "category_ids", "surveyor", "survey"})
    data["phone"] = normalize_phone(body.phone) if body.phone else user.phone
    data["whatsapp"] = normalize_phone(body.whatsapp) if body.whatsapp else data["phone"]
    _phone_free(db, data["phone"])
    if data.get("opening"):
        data["hours"] = onboarding.hours_text(data["opening"])
    if not data.get("commune_id") and data.get("lat") is not None:   # commune déduite de la position
        c = onboarding.nearest_commune(db, data["lat"], data["lng"])
        data["commune_id"] = c.id if c else None
    shop = Shop(**data, status="draft", source="declared", owner_user_id=user.id)
    db.add(shop)
    db.flush()
    _set_links(db, shop, body.brand_ids, body.category_ids, "declared")
    _commit_shop(db)
    return shop_out(shop)


@router.patch("/shops/{shop_id}")
def shop_patch(shop_id: int, body: ShopPatch, db: Session = Depends(get_db), user: User = Depends(current_user)):
    shop = _owned_shop(db, shop_id, user, "profile")
    data = body.model_dump(exclude_unset=True, exclude={"brand_ids", "category_ids"})
    for k in ("phone", "whatsapp"):
        if data.get(k):
            data[k] = normalize_phone(data[k])
    _phone_free(db, data.get("phone"), shop)
    if data.get("opening"):
        data["hours"] = onboarding.hours_text(data["opening"])
    if "closed_until" in data and data["closed_until"] is None:
        data["closed_note"] = None
    if data.get("lat") is not None and "commune_id" not in data:
        c = onboarding.nearest_commune(db, data["lat"], data.get("lng", shop.lng))
        data["commune_id"] = c.id if c else shop.commune_id
    if shop.status == "rejected":   # fiche corrigée après un refus : retour dans la file de vérification
        shop.status, shop.reject_reason = "draft", None
    for k, v in data.items():
        setattr(shop, k, v)
    _set_links(db, shop, body.brand_ids, body.category_ids, "declared")
    team.log(db, shop.id, user, "profile.update")
    _commit_shop(db)
    return shop_out(shop)


@router.post("/shops/{shop_id}/reconfirm")
def shop_reconfirm(shop_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """« Mes informations sont à jour » : marques et familles reconfirmées (fraîcheur, six mois)."""
    shop = _owned_shop(db, shop_id, user, "profile")
    now = datetime.now(timezone.utc)
    for link in [*shop.brands, *shop.categories]:
        link.confirmed_at = now
    shop.updated_at = now
    db.commit()
    return shop_out(shop)


@router.post("/shops/{shop_id}/claim")
def shop_claim(shop_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Revendication d'une fiche créée par l'équipe. Numéro de connexion = numéro de la fiche : immédiate.
    Sinon : demande en attente, que l'administrateur accepte après avoir appelé le magasin."""
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(404, "Magasin inconnu")
    if shop.owner_user_id:
        raise HTTPException(409, "Fiche déjà revendiquée")
    if user.role == "driver":
        user.role = "shop_owner"
    if shop.phone != user.phone:
        pending = db.scalar(select(ShopClaim).where(ShopClaim.shop_id == shop.id, ShopClaim.user_id == user.id,
                                                    ShopClaim.status == "pending"))
        if pending is None:
            db.add(ShopClaim(shop_id=shop.id, user_id=user.id))
        db.commit()
        return {**shop_out(shop, full=False), "claim": "pending"}
    shop.owner_user_id = user.id
    if shop.status == "verified":
        shop.status = "claimed"
    db.commit()
    return {**shop_out(shop), "claim": "accepted"}


@router.get("/shops/claims/mine")
def my_claims(db: Session = Depends(get_db), user: User = Depends(current_user)):
    out = []
    for c in db.scalars(select(ShopClaim).where(ShopClaim.user_id == user.id).order_by(ShopClaim.id.desc())):
        shop = db.get(Shop, c.shop_id)
        out.append({"id": c.id, "status": c.status, "reason": c.reason, "shop": shop_out(shop, full=False) if shop else None})
    return out


@router.get("/geo/geocode")
def geocode(q: str = Query(..., min_length=3, max_length=200), user: User = Depends(current_user)):
    """Adresse tapée par un magasin -> lieux de la wilaya d'Oran (OpenStreetMap). Réservé aux comptes connectés."""
    try:
        return onboarding.geocoder.search(q)
    except Exception:   # service indisponible : le magasin place l'épingle lui-même
        return []


def _product_payload(db: Session, body: ProductIn) -> None:
    if not db.get(PartCategory, body.category_id):
        raise HTTPException(422, "Famille de pièces inconnue")
    for vid in body.variant_ids:
        if not db.get(VehicleVariant, vid):
            raise HTTPException(422, f"Véhicule inconnu : {vid}")


@router.post("/shops/{shop_id}/products", status_code=201)
def product_create(shop_id: int, body: ProductIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    shop = _owned_shop(db, shop_id, user, "products")
    _product_payload(db, body)
    p = Product(shop_id=shop.id, **body.model_dump(exclude={"variant_ids"}), price_confirmed_at=datetime.now(timezone.utc))
    p.fitments = [ProductFitment(variant_id=v) for v in set(body.variant_ids)]
    db.add(p)
    team.log(db, shop.id, user, "product.create", p.title)
    db.commit()
    return {"id": p.id}


@router.put("/shops/{shop_id}/products/{product_id}")
def product_update(shop_id: int, product_id: int, body: ProductIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _owned_shop(db, shop_id, user, "products")
    p = db.get(Product, product_id)
    if not p or p.shop_id != shop_id:
        raise HTTPException(404, "Produit inconnu")
    _product_payload(db, body)
    for k, v in body.model_dump(exclude={"variant_ids"}).items():
        setattr(p, k, v)
    p.fitments = [ProductFitment(variant_id=v) for v in set(body.variant_ids)]
    p.price_confirmed_at = datetime.now(timezone.utc)
    team.log(db, shop_id, user, "product.update", p.title)
    db.commit()
    return {"id": p.id}


def _own_product(db: Session, shop_id: int, product_id: int) -> Product:
    p = db.get(Product, product_id)
    if not p or p.shop_id != shop_id:
        raise HTTPException(404, "Produit inconnu")
    return p


@router.patch("/shops/{shop_id}/products/{product_id}")
def product_patch(shop_id: int, product_id: int, body: ProductPatch, db: Session = Depends(get_db),
                  user: User = Depends(current_user)):
    """En un toucher depuis la liste : prix, en stock / rupture, ou confirmation du prix actuel."""
    _owned_shop(db, shop_id, user, "prices")
    p = _own_product(db, shop_id, product_id)
    data = body.model_dump(exclude_unset=True, exclude={"confirm"})
    for k, v in data.items():
        setattr(p, k, v)
    p.price_confirmed_at = datetime.now(timezone.utc)
    what = ", ".join(f"{k} = {v}" for k, v in data.items()) or "prix confirmé"
    team.log(db, shop_id, user, "product.quick", f"{p.title} : {what}")
    db.commit()
    return {"id": p.id, "price": p.price, "in_stock": p.in_stock, "price_confirmed_at": p.price_confirmed_at.isoformat()}


async def _read_photo(file: UploadFile) -> bytes:
    data = await file.read(1_000_001)
    if len(data) > 1_000_000:
        raise HTTPException(413, "Photo trop lourde (1 Mo au plus)")
    return data


@router.post("/shops/{shop_id}/products/{product_id}/photo")
async def product_photo(shop_id: int, product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db),
                        user: User = Depends(current_user)):
    _owned_shop(db, shop_id, user, "products")
    p = _own_product(db, shop_id, product_id)
    try:
        url = storage().save("produits", await _read_photo(file))
    except InvalidImage as e:
        raise HTTPException(422, str(e)) from None
    storage().delete(p.photo_url)   # l'ancienne photo ne reste pas sur le disque
    p.photo_url = url
    db.commit()
    return {"photo_url": url}


@router.delete("/shops/{shop_id}/products/{product_id}/photo", status_code=204)
def product_photo_delete(shop_id: int, product_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _owned_shop(db, shop_id, user, "products")
    p = _own_product(db, shop_id, product_id)
    storage().delete(p.photo_url)
    p.photo_url = None
    db.commit()


@router.post("/shops/{shop_id}/photo")
async def shop_photo(shop_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Photo de la devanture (idée C) : le client reconnaît la boutique dans la rue."""
    shop = _owned_shop(db, shop_id, user, "profile")
    try:
        url = storage().save("devantures", await _read_photo(file))
    except InvalidImage as e:
        raise HTTPException(422, str(e)) from None
    storage().delete(shop.photo_url)
    shop.photo_url = url
    db.commit()
    return {"photo_url": url}


@router.delete("/shops/{shop_id}/photo", status_code=204)
def shop_photo_delete(shop_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    shop = _owned_shop(db, shop_id, user, "profile")
    storage().delete(shop.photo_url)
    shop.photo_url = None
    db.commit()


@router.get("/media/{kind}/{name}")
def media(kind: str, name: str):
    """Photo publique : nom tiré au hasard (introuvable sans le connaître), contenu figé (cache long)."""
    path = storage().path(kind, name)
    if path is None:
        raise HTTPException(404, "Photo introuvable")
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=31536000, immutable"})


@router.delete("/shops/{shop_id}/products/{product_id}", status_code=204)
def product_delete(shop_id: int, product_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _owned_shop(db, shop_id, user, "products_delete")
    p = _own_product(db, shop_id, product_id)
    storage().delete(p.photo_url)
    team.log(db, shop_id, user, "product.delete", p.title)
    db.delete(p)
    db.commit()


@router.post("/shops/{shop_id}/products/import")
async def product_import(shop_id: int, file: UploadFile = File(...), dry_run: bool = False, db: Session = Depends(get_db),
                         user: User = Depends(current_user)):
    """Import Excel ou CSV. `dry_run=true` : aperçu (produits ajoutés, mis à jour, erreurs ligne par ligne) sans rien
    enregistrer ; le magasin confirme ensuite."""
    shop = _owned_shop(db, shop_id, user, "products")
    content = await file.read()
    if len(content) > MAX_IMPORT_BYTES:
        raise HTTPException(413, "Fichier trop lourd (5 Mo maximum)")
    rows = read_table(content, file.filename or "import.csv")
    rep = import_products(db, shop, rows)
    if dry_run:
        db.rollback()
    else:
        team.log(db, shop.id, user, "product.import", f"{rep.created} ajoutés, {rep.updated} mis à jour")
        db.commit()
    return {"created": rep.created, "updated": rep.updated, "errors": rep.errors, "total": len(rows), "dry_run": dry_run}


# --- Demandes diffusées (F16) ---------------------------------------------

@router.post("/part-requests", status_code=201)
def part_request_create(body: PartRequestIn, db: Session = Depends(get_db), user: User | None = Depends(current_user_optional)):
    if not db.get(PartCategory, body.category_id):
        raise HTTPException(404, "Famille de pièces inconnue")
    req = PartRequest(**body.model_dump(), user_id=user.id if user else None, token=secrets.token_urlsafe(16))
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
    return {"id": req.id, "token": req.token, "notified_shops": n}


@router.get("/part-requests/pending-count")
def part_request_pending(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Nombre de demandes en attente de réponse, pour le compteur de l'onglet « Magasin »."""
    shop_ids = [s.id for s, _, perms in team.my_shops(db, user) if "requests" in perms]
    if not shop_ids:
        return {"pending": 0}
    n = len(list(db.scalars(select(RequestResponse.request_id).where(RequestResponse.shop_id.in_(shop_ids),
                                                                     RequestResponse.available.is_(None)))))
    return {"pending": n}


@router.get("/part-requests/inbox")
def part_request_inbox(db: Session = Depends(get_db), user: User = Depends(current_user)):
    shop_ids = [s.id for s, _, perms in team.my_shops(db, user) if "requests" in perms]
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
    _owned_shop(db, shop_id, user, "requests")
    rr = db.get(RequestResponse, (request_id, shop_id))
    if not rr:
        raise HTTPException(404, "Demande inconnue pour ce magasin")
    rr.available, rr.price, rr.responded_at = body.available, body.price, datetime.now(timezone.utc)
    req = db.get(PartRequest, request_id)
    req.status = "answered"
    if body.available:
        _mark_observed(db, shop_id, req.category_id, req.variant_id)
    cat = db.get(PartCategory, req.category_id)
    team.log(db, shop_id, user, "request.answer",
             f"{cat.name_fr if cat else ''} : {'disponible' if body.available else 'pas en stock'}"
             f"{f', {body.price:g} DA' if body.available and body.price else ''}")
    db.commit()
    return {"ok": True}


def request_out(db: Session, req: PartRequest) -> dict:
    """Une demande vue par le client : la pièce, le véhicule, les magasins contactés et leurs réponses (disponibles
    d'abord, du moins cher au plus cher), avec de quoi les appeler."""
    cat = db.get(PartCategory, req.category_id)
    v = db.get(VehicleVariant, req.variant_id) if req.variant_id else None
    rows = list(db.scalars(select(RequestResponse).where(RequestResponse.request_id == req.id)))
    answers = [r for r in rows if r.responded_at]
    answers.sort(key=lambda r: (not r.available, r.price if r.price is not None else 1e12))
    seen = req.seen_at.replace(tzinfo=timezone.utc) if req.seen_at and not req.seen_at.tzinfo else req.seen_at
    return {"id": req.id, "status": req.status, "created_at": req.created_at.isoformat(),
            "category_id": req.category_id, "part": cat.name_fr if cat else None, "variant_id": req.variant_id,
            "vehicle": f"{v.model.brand.name} {v.model.name} {v.engine}" if v else None,
            "notified": len(rows), "answered": len(answers),
            "unseen": sum(1 for r in answers if seen is None or
                          (r.responded_at.replace(tzinfo=timezone.utc) if not r.responded_at.tzinfo else r.responded_at) > seen),
            "responses": [{"shop": shop_out(db.get(Shop, r.shop_id), full=False), "available": r.available, "price": r.price,
                           "responded_at": r.responded_at.isoformat()} for r in answers]}


def _readable(db: Session, request_id: int, token: str | None, user: User | None) -> PartRequest:
    req = db.get(PartRequest, request_id)
    owner = req is not None and user is not None and req.user_id == user.id
    if not req or not (owner or (token and req.token and secrets.compare_digest(token, req.token))):
        raise HTTPException(404, "Demande inconnue")   # même réponse sans le bon jeton : rien n'est dévoilé
    return req


@router.get("/part-requests/{request_id}")
def part_request_status(request_id: int, token: str | None = None, db: Session = Depends(get_db),
                        user: User | None = Depends(current_user_optional)):
    """Réponses à une demande : pour son auteur connecté, ou avec le jeton reçu à la création (sans compte)."""
    return request_out(db, _readable(db, request_id, token, user))


@router.post("/part-requests/{request_id}/seen", status_code=204)
def part_request_seen(request_id: int, token: str | None = None, db: Session = Depends(get_db),
                      user: User | None = Depends(current_user_optional)):
    req = _readable(db, request_id, token, user)
    req.seen_at = datetime.now(timezone.utc)
    db.commit()


@router.get("/me/part-requests")
def my_part_requests(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """« Mes demandes » : les 30 dernières demandes du client connecté, avec les réponses des magasins."""
    rows = db.scalars(select(PartRequest).where(PartRequest.user_id == user.id).order_by(PartRequest.id.desc()).limit(30))
    return [request_out(db, r) for r in rows]


@router.get("/me/part-requests/unseen")
def my_unseen(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Réponses de magasins pas encore lues (repère sur l'onglet Compte)."""
    rows = db.scalars(select(PartRequest).where(PartRequest.user_id == user.id).order_by(PartRequest.id.desc()).limit(30))
    return {"unseen": sum(request_out(db, r)["unseen"] for r in rows)}