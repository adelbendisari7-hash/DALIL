"""Back-office administrateur (F10) et indicateurs."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (
    AdminAction,
    Brand,
    Model,
    VehicleRequest,
    VehicleVariant,
    ContactEvent,
    DiagnosisSession,
    Feedback,
    PartCategory,
    PartReference,
    PartRequest,
    PlateReport,
    Product,
    Shop,
    ShopBrand,
    ShopCategory,
    User,
    UserVehicle,
)
from ..schemas import ShopIn, format_plate, shop_out
from ..security import log_admin, normalize_phone, require_admin
from ..services.catalog import resolve_category, resolve_variants
from ..services.imports import import_shops, read_table
from ..services.recommendation import STALE_DAYS

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])


@router.get("/shops")
def admin_shops(status: str | None = None, q: str | None = None, db: Session = Depends(get_db)):
    query = select(Shop).order_by(Shop.updated_at.desc())
    if status:
        query = query.where(Shop.status == status)
    if q:
        query = query.where(Shop.name.ilike(f"%{q}%") | Shop.phone.ilike(f"%{q}%"))
    return [shop_out(s) for s in db.scalars(query.limit(500))]


@router.post("/shops", status_code=201)
def admin_shop_create(body: ShopIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Saisie terrain (formulaire mobile) : la fiche est vérifiée d'office, l'enquêteur était sur place."""
    now = datetime.now(timezone.utc)
    data = body.model_dump(exclude={"brand_ids", "category_ids", "surveyor"})
    for k in ("phone", "whatsapp"):
        if data.get(k):
            data[k] = normalize_phone(data[k])
    if data.get("phone") and not data.get("whatsapp"):
        data["whatsapp"] = data["phone"]
    if data.get("phone") and db.scalar(select(Shop).where(Shop.phone == data["phone"])):
        raise HTTPException(409, "Un magasin avec ce numéro existe déjà : utilisez la fusion")
    shop = Shop(**data, status="verified", source="terrain", visited_at=now, verified_at=now,
                surveyor=body.surveyor or admin.name or admin.phone)
    db.add(shop)
    db.flush()
    for bid in set(body.brand_ids):
        db.add(ShopBrand(shop_id=shop.id, brand_id=bid, source="terrain", confirmed_at=now))
    for cid in set(body.category_ids):
        db.add(ShopCategory(shop_id=shop.id, category_id=cid, source="terrain", confirmed_at=now))
    log_admin(db, admin, "shop.create", str(shop.id))
    db.commit()
    db.refresh(shop)
    return shop_out(shop)


@router.post("/shops/{shop_id}/verify")
def admin_verify(shop_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(404, "Magasin inconnu")
    shop.status = "claimed" if shop.owner_user_id else "verified"
    shop.verified_at = datetime.now(timezone.utc)
    log_admin(db, admin, "shop.verify", str(shop_id))
    db.commit()
    return shop_out(shop)


@router.post("/shops/{shop_id}/reject")
def admin_reject(shop_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(404, "Magasin inconnu")
    shop.status = "rejected"
    log_admin(db, admin, "shop.reject", str(shop_id))
    db.commit()
    return shop_out(shop)


@router.post("/shops/{shop_id}/merge")
def admin_merge(shop_id: int, into: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Fusionne la fiche `shop_id` dans `into` (doublon OSM / terrain / inscription)."""
    src, dst = db.get(Shop, shop_id), db.get(Shop, into)
    if not src or not dst or src.id == dst.id:
        raise HTTPException(404, "Fiches invalides")
    for col in ("phone", "whatsapp", "commune_id", "lat", "lng", "address", "hours", "osm_id", "photo_url", "owner_user_id", "sale_mode"):
        if getattr(dst, col) in (None, "") and getattr(src, col) not in (None, ""):
            value = getattr(src, col)
            if col in ("phone", "osm_id"):
                setattr(src, col, None)
                db.flush()
            setattr(dst, col, value)
    dst.parts_origin = sorted(set(dst.parts_origin or []) | set(src.parts_origin or []))
    have_b = {b.brand_id for b in dst.brands}
    dst.brands += [ShopBrand(brand_id=b.brand_id, source=b.source, confirmed_at=b.confirmed_at) for b in src.brands if b.brand_id not in have_b]
    have_c = {c.category_id for c in dst.categories}
    dst.categories += [ShopCategory(category_id=c.category_id, source=c.source, confidence=c.confidence, confirmed_at=c.confirmed_at)
                       for c in src.categories if c.category_id not in have_c]
    for model in (Product, ContactEvent, Feedback):
        for row in db.scalars(select(model).where(model.shop_id == src.id)):
            row.shop_id = dst.id
    db.delete(src)
    log_admin(db, admin, "shop.merge", f"{shop_id}->{into}")
    db.commit()
    return shop_out(dst)


@router.post("/shops/import")
async def admin_import(file: UploadFile = File(...), source: str = "terrain", db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    content = await file.read()
    rows = read_table(content, file.filename or "import.csv")
    rep = import_shops(db, rows, default_source=source)
    log_admin(db, admin, "shop.import", file.filename, {"created": rep.created, "updated": rep.updated, "errors": len(rep.errors)})
    db.commit()
    return {"created": rep.created, "updated": rep.updated, "errors": rep.errors, "total": len(rows)}


@router.post("/part-references/import")
async def admin_refs_import(file: UploadFile = File(...), db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Références du pilote (F14) saisies avec les magasins : colonnes famille, vehicule, reference, marque_piece, source."""
    rows = read_table(await file.read(), file.filename or "refs.csv")
    created, errors = 0, []
    for line, r in enumerate(rows, start=2):
        cat = resolve_category(db, str(r.get("famille") or ""))
        variants = resolve_variants(db, str(r.get("vehicule") or ""))
        ref = str(r.get("reference") or "").strip()
        if not cat or not variants or not ref:
            errors.append({"line": line, "error": "famille, véhicule ou référence non reconnus"})
            continue
        for v in variants:
            db.add(PartReference(category_id=cat.id, variant_id=v.id, oem_ref=ref, part_brand=r.get("marque_piece"),
                                 source=str(r.get("source") or "magasin"), verified_at=datetime.now(timezone.utc)))
            created += 1
    log_admin(db, admin, "refs.import", file.filename, {"created": created})
    db.commit()
    return {"created": created, "errors": errors}


@router.get("/stale")
def admin_stale(db: Session = Depends(get_db)):
    """Fiches non confirmées depuis six mois (section 4, fraîcheur)."""
    limit = datetime.now(timezone.utc) - timedelta(days=STALE_DAYS)
    rows = db.scalars(select(Shop).where(Shop.status.in_(("verified", "claimed"))))
    out = []
    for s in rows:
        last = s.verified_at or s.visited_at
        if last and last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        if last is None or last < limit:
            out.append(shop_out(s, full=False))
    return out


@router.get("/metrics")
def admin_metrics(db: Session = Depends(get_db)):
    def count(model, *where):
        return db.scalar(select(func.count()).select_from(model).where(*where)) or 0

    statuses = dict(db.execute(select(Shop.status, func.count()).group_by(Shop.status)).all())
    since = datetime.now(timezone.utc) - timedelta(days=30)
    found_yes = count(Feedback, Feedback.part_found.is_(True))
    found_all = count(Feedback, Feedback.part_found.is_not(None))
    diag_ok = count(Feedback, Feedback.diagnosis_correct.is_(True))
    diag_all = count(Feedback, Feedback.diagnosis_correct.is_not(None))
    status_expr = (
        func.json_extract(DiagnosisSession.result_json, "$.status") if db.bind.dialect.name == "sqlite"
        else DiagnosisSession.result_json.op("->>")("status")
    ).label("status")
    by_status = dict(db.execute(select(status_expr, func.count()).group_by(status_expr)).all())
    top_parts = db.execute(
        select(PartCategory.name_fr, func.count()).join(ContactEvent, ContactEvent.category_id == PartCategory.id)
        .group_by(PartCategory.name_fr).order_by(func.count().desc()).limit(10)
    ).all()
    return {
        "shops": {"total": sum(statuses.values()), "by_status": statuses,
                  "demo": count(Shop, Shop.is_demo.is_(True)), "with_owner": count(Shop, Shop.owner_user_id.is_not(None))},
        "products": count(Product),
        "users": count(User),
        "diagnoses": {"total": count(DiagnosisSession), "last_30_days": count(DiagnosisSession, DiagnosisSession.created_at >= since),
                      "by_status": by_status},
        "contacts": {"total": count(ContactEvent), "whatsapp": count(ContactEvent, ContactEvent.channel == "whatsapp"),
                     "call": count(ContactEvent, ContactEvent.channel == "call")},
        "feedback": {"part_found_rate": round(found_yes / found_all, 3) if found_all else None, "part_found_n": found_all,
                     "diagnosis_correct_rate": round(diag_ok / diag_all, 3) if diag_all else None, "diagnosis_n": diag_all},
        "part_requests": count(PartRequest),
        "top_contacted_parts": [{"part": p, "count": n} for p, n in top_parts],
        # Référentiel : véhicules les plus diagnostiqués, et véhicules saisis car absents de la liste (à ajouter)
        "top_diagnosed_vehicles": [{"vehicle": f"{b} {m}", "count": n} for b, m, n in db.execute(
            select(Brand.name, Model.name, func.count()).select_from(DiagnosisSession)
            .join(VehicleVariant, VehicleVariant.id == DiagnosisSession.variant_id).join(Model).join(Brand)
            .group_by(Brand.name, Model.name).order_by(func.count().desc()).limit(10))],
        "requested_missing_vehicles": [{"vehicle": f"{b} {m}", "count": n} for b, m, n in db.execute(
            select(VehicleRequest.brand, VehicleRequest.model, func.count()).group_by(VehicleRequest.brand, VehicleRequest.model)
            .order_by(func.count().desc()).limit(10))],
    }


@router.get("/actions")
def admin_actions(db: Session = Depends(get_db)):
    rows = db.scalars(select(AdminAction).order_by(AdminAction.id.desc()).limit(200))
    return [{"id": a.id, "user_id": a.user_id, "action": a.action, "target": a.target, "details": a.details,
             "created_at": a.created_at.isoformat()} for a in rows]


@router.get("/plate-reports")
def admin_plate_reports(status: str = "open", db: Session = Depends(get_db)):
    """Signalements « ce matricule est le mien » : qui signale, qui détient le matricule, depuis quand."""
    out = []
    for r in db.scalars(select(PlateReport).where(PlateReport.status == status).order_by(PlateReport.id)):
        holder = db.scalar(select(UserVehicle).where(UserVehicle.plate == r.plate))
        reporter = db.get(User, r.reporter_user_id) if r.reporter_user_id else None
        owner = db.get(User, holder.user_id) if holder else None
        out.append({"id": r.id, "plate": format_plate(r.plate), "status": r.status, "message": r.message,
                    "created_at": r.created_at,
                    "reporter": {"name": reporter.name, "phone": reporter.phone} if reporter else None,
                    "holder": {"name": owner.name, "phone": owner.phone, "since": holder.created_at} if owner else None})
    return out


@router.post("/plate-reports/{report_id}/{action}")
def admin_plate_report_resolve(report_id: int, action: str, db: Session = Depends(get_db),
                               admin: User = Depends(require_admin)):
    from .account import resolve_report

    if action not in ("release", "reject"):
        raise HTTPException(404, "Action inconnue")
    report = db.get(PlateReport, report_id)
    if not report:
        raise HTTPException(404, "Signalement inconnu")
    out = resolve_report(db, report, action)
    log_admin(db, admin, f"plate.{action}", str(report_id))
    db.commit()
    return out
