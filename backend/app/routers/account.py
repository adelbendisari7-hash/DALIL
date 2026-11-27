"""Compte client : voitures (matricule unique), signalement d'un matricule déjà pris, historique des diagnostics.

Le profil lui-même (prénom, nom, e-mail, commune, langue, date de naissance) passe par PATCH /auth/me.
Ni le propriétaire d'un matricule déjà pris ni sa voiture ne sont jamais montrés à un autre client.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import DiagnosisSession, PlateReport, User, UserVehicle, VehicleVariant
from ..schemas import PlateReportIn, VehicleIn, VehiclePatch, format_plate
from ..security import current_user, feedback_limiter

router = APIRouter(prefix="/me")
MAX_VEHICLES = 20


def vehicle_label(v: UserVehicle) -> str:
    if v.variant:
        m = v.variant.model
        engine = "" if v.variant.engine == "Autre motorisation" else f" {v.variant.engine}"
        return f"{m.brand.name} {m.name}{engine}{f' {v.year}' if v.year else ''}"
    return f"{v.label or 'Voiture'}{f' {v.year}' if v.year else ''}"


def vehicle_out(v: UserVehicle) -> dict:
    return {"id": v.id, "plate": format_plate(v.plate), "variant_id": v.variant_id, "year": v.year, "label": v.label,
            "nickname": v.nickname, "mileage_km": v.mileage_km, "vin": v.vin, "display": vehicle_label(v),
            "brand_id": v.variant.model.brand_id if v.variant else None,
            "model_id": v.variant.model_id if v.variant else None}


def _own(db: Session, user: User, vehicle_id: int) -> UserVehicle:
    v = db.get(UserVehicle, vehicle_id)
    if not v or v.user_id != user.id:   # même réponse qu'une voiture inexistante : rien n'est dévoilé
        raise HTTPException(404, "Voiture inconnue")
    return v


PLATE_TAKEN = {"code": "plate_taken", "message": "Ce matricule est déjà enregistré sur un autre compte. S'il s'agit de "
                                                 "votre voiture, signalez-le : l'équipe DALIL vérifiera."}


def _commit(db: Session) -> None:
    """Deux enregistrements simultanés du même matricule : la contrainte unique de la base tranche."""
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail=PLATE_TAKEN) from None


def _check(db: Session, data: dict, current: UserVehicle | None = None) -> None:
    if data.get("variant_id") is not None and not db.get(VehicleVariant, data["variant_id"]):
        raise HTTPException(422, "Véhicule inconnu dans le référentiel")
    plate = data.get("plate")
    if plate:
        other = db.scalar(select(UserVehicle).where(UserVehicle.plate == plate))
        if other and other is not current:
            raise HTTPException(409, detail=PLATE_TAKEN)


@router.get("/vehicles")
def vehicles(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(UserVehicle).where(UserVehicle.user_id == user.id).order_by(UserVehicle.id))
    return [vehicle_out(v) for v in rows]


@router.post("/vehicles", status_code=201)
def vehicle_add(body: VehicleIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = body.model_dump()
    if not data.get("variant_id") and not data.get("label"):
        raise HTTPException(422, "Choisissez le modèle de la voiture, ou saisissez sa marque et son modèle")
    n = len(list(db.scalars(select(UserVehicle.id).where(UserVehicle.user_id == user.id))))
    if n >= MAX_VEHICLES:
        raise HTTPException(422, f"{MAX_VEHICLES} voitures au plus par compte")
    _check(db, data)
    v = UserVehicle(user_id=user.id, **data)
    db.add(v)
    _commit(db)
    db.refresh(v)
    return vehicle_out(v)


@router.patch("/vehicles/{vehicle_id}")
def vehicle_edit(vehicle_id: int, body: VehiclePatch, user: User = Depends(current_user), db: Session = Depends(get_db)):
    v = _own(db, user, vehicle_id)
    data = body.model_dump(exclude_unset=True)
    if data.get("plate") is None:
        data.pop("plate", None)   # le matricule ne s'efface pas
    _check(db, data, current=v)
    for k, val in data.items():
        setattr(v, k, val)
    if not v.variant_id and not v.label:
        raise HTTPException(422, "Choisissez le modèle de la voiture, ou saisissez sa marque et son modèle")
    _commit(db)
    db.refresh(v)
    return vehicle_out(v)


@router.delete("/vehicles/{vehicle_id}", status_code=204)
def vehicle_delete(vehicle_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    v = _own(db, user, vehicle_id)
    for s in db.scalars(select(DiagnosisSession).where(DiagnosisSession.user_vehicle_id == v.id)):
        s.user_vehicle_id = None   # l'historique reste, sans la voiture
    db.delete(v)
    db.commit()


@router.post("/plate-reports", status_code=201, dependencies=[Depends(feedback_limiter)])
def plate_report(body: PlateReportIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    holder = db.scalar(select(UserVehicle).where(UserVehicle.plate == body.plate))
    if holder is None or holder.user_id == user.id:
        raise HTTPException(422, "Ce matricule n'est pas enregistré sur un autre compte : ajoutez simplement la voiture")
    open_ = db.scalar(select(PlateReport).where(PlateReport.plate == body.plate, PlateReport.reporter_user_id == user.id,
                                                PlateReport.status == "open"))
    if open_ is None:
        open_ = PlateReport(plate=body.plate, reporter_user_id=user.id, message=body.message)
        db.add(open_)
        db.commit()
    return {"id": open_.id, "status": open_.status}


@router.get("/diagnoses")
def diagnoses(vehicle_id: int | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Historique des diagnostics du client, du plus récent au plus ancien (50 au plus)."""
    q = select(DiagnosisSession).where(DiagnosisSession.user_id == user.id)
    if vehicle_id is not None:
        q = q.where(DiagnosisSession.user_vehicle_id == _own(db, user, vehicle_id).id)
    out = []
    for s in db.scalars(q.order_by(DiagnosisSession.id.desc()).limit(50)):
        causes = (s.result_json or {}).get("causes", [])
        out.append({"session_id": s.id, "created_at": s.created_at, "text": s.input_text[:160],
                    "dtc_codes": s.dtc_codes or [], "user_vehicle_id": s.user_vehicle_id,
                    "status": (s.result_json or {}).get("status"),
                    "top": {"name": causes[0]["name"], "part": causes[0]["part"]["name"]} if causes else None})
    return out


def resolve_report(db: Session, report: PlateReport, action: str) -> dict:
    """Administrateur : « released » retire le matricule du compte qui le détenait (revente, erreur) ;
    « rejected » le laisse où il est. Le signalement est clos dans les deux cas."""
    if report.status != "open":
        raise HTTPException(409, "Signalement déjà traité")
    if action == "release":
        holder = db.scalar(select(UserVehicle).where(UserVehicle.plate == report.plate))
        if holder:
            for s in db.scalars(select(DiagnosisSession).where(DiagnosisSession.user_vehicle_id == holder.id)):
                s.user_vehicle_id = None
            db.delete(holder)
        report.status = "released"
    else:
        report.status = "rejected"
    report.resolved_at = datetime.now(timezone.utc)
    return {"id": report.id, "status": report.status}
