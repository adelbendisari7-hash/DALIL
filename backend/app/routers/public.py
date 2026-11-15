"""Points d'entrée publics : véhicules, pièces, codes OBD, diagnostic."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Brand, Commune, DiagnosisSession, DtcCode, DtcPart, Model, PartCategory, PartReference, Product, User, VehicleVariant
from ..schemas import AnswersRequest, DiagnosisRequest
from ..security import current_user_optional, diagnosis_limiter
from ..services.catalog import search_categories
from ..services.diagnosis.pipeline import DiagnosisInput, run_diagnosis

router = APIRouter()


# --- Véhicules (F1) -------------------------------------------------------

@router.get("/vehicles/brands")
def brands(db: Session = Depends(get_db)):
    rows = db.scalars(select(Brand).order_by(Brand.priority.desc(), Brand.name))
    return [{"id": b.id, "name": b.name, "country": b.country} for b in rows]


@router.get("/vehicles/models")
def models(brand_id: int, db: Session = Depends(get_db)):
    rows = db.scalars(select(Model).where(Model.brand_id == brand_id).order_by(Model.name))
    return [{"id": m.id, "name": m.name, "pilot": m.pilot} for m in rows]


@router.get("/vehicles/variants")
def variants(model_id: int, year: int | None = None, db: Session = Depends(get_db)):
    q = select(VehicleVariant).where(VehicleVariant.model_id == model_id)
    if year:
        q = q.where(VehicleVariant.year_from <= year).where((VehicleVariant.year_to.is_(None)) | (VehicleVariant.year_to >= year))
    return [
        {"id": v.id, "engine": v.engine, "fuel": v.fuel, "year_from": v.year_from, "year_to": v.year_to,
         "label": f"{v.engine} ({v.fuel}, {v.year_from}–{v.year_to or 'auj.'})"}
        for v in db.scalars(q.order_by(VehicleVariant.year_from, VehicleVariant.engine))
    ]


@router.get("/vehicles/variants/{variant_id}")
def variant_detail(variant_id: int, db: Session = Depends(get_db)):
    v = db.get(VehicleVariant, variant_id)
    if not v:
        raise HTTPException(404, "Variante inconnue")
    return {"id": v.id, "brand": v.model.brand.name, "brand_id": v.model.brand_id, "model": v.model.name,
            "model_id": v.model_id, "engine": v.engine, "fuel": v.fuel, "year_from": v.year_from, "year_to": v.year_to}


@router.get("/geo/communes")
def communes(wilaya: str = "31", db: Session = Depends(get_db)):
    rows = db.scalars(select(Commune).where(Commune.wilaya_code == wilaya).order_by(Commune.nom_fr))
    return [{"id": c.id, "code": c.code, "nom_fr": c.nom_fr, "lat": c.lat, "lng": c.lng} for c in rows]


# --- Pièces (F5, F14) -----------------------------------------------------

@router.get("/parts/categories")
def categories(db: Session = Depends(get_db)):
    cats = list(db.scalars(select(PartCategory).order_by(PartCategory.id)))
    tree = []
    for fam in [c for c in cats if c.parent_id is None]:
        tree.append({
            "id": fam.id, "slug": fam.slug, "name": fam.name_fr,
            "children": [{"id": c.id, "slug": c.slug, "name": c.name_fr, "pilot": c.pilot} for c in cats if c.parent_id == fam.id],
        })
    return tree


@router.get("/parts/search")
def parts_search(q: str = Query(..., min_length=2, max_length=80), db: Session = Depends(get_db)):
    return [
        {"id": c.id, "slug": c.slug, "name": c.name_fr, "parent_id": c.parent_id, "score": s}
        for c, s in search_categories(db, q)
    ]


@router.get("/parts/references")
def references(ref: str = Query(..., min_length=3, max_length=60), db: Session = Depends(get_db)):
    """Recherche par numéro gravé sur l'ancienne pièce (F14)."""
    key = ref.replace(" ", "").replace("-", "").upper()
    out = []
    for r in db.scalars(select(PartReference)):
        if key in r.oem_ref.replace(" ", "").replace("-", "").upper():
            v = db.get(VehicleVariant, r.variant_id)
            out.append({"oem_ref": r.oem_ref, "category_id": r.category_id, "variant_id": r.variant_id,
                        "vehicle": f"{v.model.brand.name} {v.model.name} {v.engine}", "level": 2, "source": r.source})
    for p in db.scalars(select(Product).where(Product.oem_ref.is_not(None))):
        if key in p.oem_ref.replace(" ", "").replace("-", "").upper():
            out.append({"oem_ref": p.oem_ref, "category_id": p.category_id, "shop_id": p.shop_id, "title": p.title,
                        "level": 3, "source": "catalogue magasin"})
    return out[:50]


# --- Codes OBD (F3) -------------------------------------------------------

@router.get("/dtc/{code}")
def dtc(code: str, db: Session = Depends(get_db)):
    row = db.get(DtcCode, code.strip().upper())
    if not row:
        raise HTTPException(404, "Code inconnu : code constructeur ou faute de frappe ?")
    parts = []
    for dp in db.scalars(select(DtcPart).where(DtcPart.code == row.code).order_by(DtcPart.weight.desc())):
        c = db.get(PartCategory, dp.category_id)
        parts.append({"category_id": c.id, "slug": c.slug, "name": c.name_fr, "weight": dp.weight})
    return {"code": row.code, "title_fr": row.title_fr, "title_en": row.title_en, "description": row.description,
            "causes": row.causes, "symptoms": row.symptoms, "parts": parts, "source": row.source}


# --- Diagnostic (F2, F4) --------------------------------------------------

def _save(db: Session, sess: DiagnosisSession, result: dict, chunks: list[int]) -> dict:
    sess.result_json, sess.retrieved_chunk_ids = result, chunks
    db.add(sess)
    db.commit()
    return {"session_id": sess.id, **result}


@router.post("/diagnosis", dependencies=[Depends(diagnosis_limiter)])
def diagnosis(body: DiagnosisRequest, db: Session = Depends(get_db), user: User | None = Depends(current_user_optional)):
    if not body.text.strip() and not body.dtc_codes:
        raise HTTPException(422, "Décrivez le problème ou saisissez un code OBD-II")
    if body.variant_id and not db.get(VehicleVariant, body.variant_id):
        raise HTTPException(422, "Véhicule inconnu")
    inp = DiagnosisInput(text=body.text, variant_id=body.variant_id, dtc_codes=body.dtc_codes)
    result, chunks = run_diagnosis(db, inp, mode=body.mode)
    sess = DiagnosisSession(user_id=user.id if user else None, variant_id=body.variant_id, input_text=body.text,
                            lang=result["lang"], dtc_codes=body.dtc_codes, answers={},
                            model_version=get_settings().model_version)
    return _save(db, sess, result, chunks)


@router.post("/diagnosis/{session_id}/answers", dependencies=[Depends(diagnosis_limiter)])
def diagnosis_answers(session_id: int, body: AnswersRequest, db: Session = Depends(get_db)):
    sess = db.get(DiagnosisSession, session_id)
    if not sess:
        raise HTTPException(404, "Session inconnue")
    answers = {**(sess.answers or {}), **body.answers}
    inp = DiagnosisInput(text=sess.input_text, variant_id=sess.variant_id, dtc_codes=sess.dtc_codes or [], answers=answers)
    result, chunks = run_diagnosis(db, inp, mode=(sess.result_json or {}).get("mode", "full"))
    sess.answers = answers
    return _save(db, sess, result, chunks)


@router.get("/diagnosis/{session_id}")
def diagnosis_get(session_id: int, db: Session = Depends(get_db)):
    sess = db.get(DiagnosisSession, session_id)
    if not sess:
        raise HTTPException(404, "Session inconnue")
    return {"session_id": sess.id, "input_text": sess.input_text, "variant_id": sess.variant_id, **(sess.result_json or {})}
