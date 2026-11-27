"""Points d'entrée publics : véhicules, pièces, codes OBD, diagnostic."""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import SessionLocal, get_db
from ..models import (
    Brand, Commune, DiagnosisSession, DtcCode, DtcPart, Model, PartCategory, PartReference, Product, User, UserVehicle,
    VehicleRequest, VehicleVariant,
)
from ..schemas import AnswersRequest, DiagnosisRequest, VehicleRequestIn
from ..security import client_hash, current_user_optional, diagnosis_limiter, feedback_limiter
from ..services.catalog import search_categories
from ..services.diagnosis.llm import get_llm
from ..services.diagnosis.pipeline import DiagnosisInput, run_diagnosis

router = APIRouter()


# --- Véhicules (F1) -------------------------------------------------------

@router.get("/vehicles/brands")
def brands(db: Session = Depends(get_db)):
    rows = db.scalars(select(Brand).order_by(Brand.priority.desc(), Brand.name))
    return [{"id": b.id, "name": b.name, "country": b.country} for b in rows]


@router.get("/vehicles/models")
def models(brand_id: int, db: Session = Depends(get_db)):
    # Les modèles les plus courants d'abord (nombre d'annonces), puis par nom
    rows = db.scalars(select(Model).where(Model.brand_id == brand_id).order_by(Model.priority.desc(), Model.name))
    return [{"id": m.id, "name": m.name, "pilot": m.pilot} for m in rows]


def _flat(s: str) -> str:
    import unicodedata

    s = "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")
    return "".join(ch for ch in s if ch.isalnum() or ch == " ")


@router.get("/vehicles/search")
def vehicles_search(q: str = Query(min_length=2, max_length=60), db: Session = Depends(get_db)):
    """Recherche par saisie (« clio 2 », « 206 hdi ») : marque et modèle, les plus courants d'abord."""
    tokens = [t for t in _flat(q).split() if t]
    out = []
    for m in db.scalars(select(Model).join(Brand).order_by(Model.priority.desc(), Model.name)):
        hay = _flat(f"{m.brand.name} {m.name}")
        compact = hay.replace(" ", "")
        if all(t in hay or t in compact for t in tokens):
            out.append({"brand_id": m.brand_id, "brand": m.brand.name, "model_id": m.id, "model": m.name})
            if len(out) >= 8:
                break
    return out


@router.post("/vehicles/requests", status_code=201, dependencies=[Depends(feedback_limiter)])
def vehicle_request(body: VehicleRequestIn, request: Request, db: Session = Depends(get_db)):
    """« Mon véhicule n'est pas dans la liste » : enregistré pour compléter le référentiel (Indicateurs)."""
    vr = VehicleRequest(**body.model_dump(), client_hash=client_hash(request))
    db.add(vr)
    db.commit()
    return {"id": vr.id}


@router.get("/vehicles/variants")
def variants(model_id: int, year: int | None = None, db: Session = Depends(get_db)):
    q = select(VehicleVariant).where(VehicleVariant.model_id == model_id)
    if year:
        q = q.where(VehicleVariant.year_from <= year).where((VehicleVariant.year_to.is_(None)) | (VehicleVariant.year_to >= year))
    return [
        {"id": v.id, "engine": v.engine, "fuel": v.fuel, "year_from": v.year_from, "year_to": v.year_to,
         "label": f"{v.engine} ({'' if v.fuel == 'inconnu' else v.fuel + ', '}{v.year_from}–{v.year_to or 'auj.'})"}
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


def _refine(session_id: int) -> None:
    """Tâche d'arrière-plan : refait le diagnostic avec le modèle de langage et remplace le résultat provisoire.
    Ouvre sa propre session de base (celle de la requête est déjà fermée). Quoi qu'il arrive, `llm` quitte
    « pending » : sinon l'écran attendrait indéfiniment."""
    with SessionLocal() as db:
        sess = db.get(DiagnosisSession, session_id)
        if sess is None:
            return
        prev = sess.result_json or {}
        try:
            inp = DiagnosisInput(text=sess.input_text, variant_id=sess.variant_id, dtc_codes=sess.dtc_codes or [],
                                 answers=sess.answers or {})
            result, chunks = run_diagnosis(db, inp, mode=prev.get("mode", "full"))
            sess.result_json, sess.retrieved_chunk_ids = result, chunks
        except Exception:
            sess.result_json = {**prev, "llm": "fallback"}
        db.add(sess)
        db.commit()


def _defer(body_defer: bool, mode: str) -> bool:
    """On ne diffère que s'il y a un modèle de langage à attendre."""
    return body_defer and mode in ("full", "retrieval") and get_llm().name != "none"


@router.post("/diagnosis", dependencies=[Depends(diagnosis_limiter)])
def diagnosis(body: DiagnosisRequest, background: BackgroundTasks, db: Session = Depends(get_db),
              user: User | None = Depends(current_user_optional)):
    if not body.text.strip() and not body.dtc_codes:
        raise HTTPException(422, "Décrivez le problème ou saisissez un code OBD-II")
    variant_id, uv = body.variant_id, None
    if body.user_vehicle_id is not None:   # voiture du compte : son modèle remplace celui du sélecteur
        uv = db.get(UserVehicle, body.user_vehicle_id)
        if not user or not uv or uv.user_id != user.id:
            raise HTTPException(404, "Voiture inconnue")
        variant_id = uv.variant_id or variant_id
    if variant_id and not db.get(VehicleVariant, variant_id):
        raise HTTPException(422, "Véhicule inconnu")
    inp = DiagnosisInput(text=body.text, variant_id=variant_id, dtc_codes=body.dtc_codes)
    defer = _defer(body.defer_llm, body.mode)
    result, chunks = run_diagnosis(db, inp, mode=body.mode, use_llm=not defer)
    if uv is not None and not uv.variant_id:   # voiture absente du référentiel : le nom saisi par le client
        from .account import vehicle_label
        result["vehicle"] = vehicle_label(uv)
    sess = DiagnosisSession(user_id=user.id if user else None, variant_id=variant_id, input_text=body.text,
                            user_vehicle_id=body.user_vehicle_id,
                            lang=result["lang"], dtc_codes=body.dtc_codes, answers={},
                            model_version=get_settings().model_version)
    saved = _save(db, sess, result, chunks)
    if defer and result["llm"] == "pending":
        background.add_task(_refine, sess.id)
    return saved


@router.post("/diagnosis/{session_id}/answers", dependencies=[Depends(diagnosis_limiter)])
def diagnosis_answers(session_id: int, body: AnswersRequest, background: BackgroundTasks, db: Session = Depends(get_db)):
    sess = db.get(DiagnosisSession, session_id)
    if not sess:
        raise HTTPException(404, "Session inconnue")
    answers = {**(sess.answers or {}), **body.answers}
    inp = DiagnosisInput(text=sess.input_text, variant_id=sess.variant_id, dtc_codes=sess.dtc_codes or [], answers=answers)
    mode = (sess.result_json or {}).get("mode", "full")
    defer = _defer(body.defer_llm, mode)
    result, chunks = run_diagnosis(db, inp, mode=mode, use_llm=not defer)
    sess.answers = answers
    saved = _save(db, sess, result, chunks)
    if defer and result["llm"] == "pending":
        background.add_task(_refine, sess.id)
    return saved


@router.get("/diagnosis/{session_id}")
def diagnosis_get(session_id: int, db: Session = Depends(get_db)):
    sess = db.get(DiagnosisSession, session_id)
    if not sess:
        raise HTTPException(404, "Session inconnue")
    return {"session_id": sess.id, "input_text": sess.input_text, "variant_id": sess.variant_id, **(sess.result_json or {})}
