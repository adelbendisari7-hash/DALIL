"""Compte client : voitures (matricule unique), signalement d'un matricule déjà pris, historique des diagnostics.

Le profil lui-même (prénom, nom, e-mail, commune, langue, date de naissance) passe par PATCH /auth/me.
Ni le propriétaire d'un matricule déjà pris ni sa voiture ne sont jamais montrés à un autre client.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (ContactEvent, DiagnosisSession, MaintenanceRecord, MaintenanceVisit, PartRequest, PlateReport,
                      PartCategory, PriceWatch, RequestResponse, Shop, User, UserVehicle, VehicleDocument,
                      VehicleVariant)
from ..schemas import PlateReportIn, VehicleIn, VehiclePatch, format_plate
from ..security import client_hash, current_user, feedback_limiter
from ..services import maintenance, price_history, price_watch, recalls, vehicle_papers
from ..services.recommendation import RECOMMENDABLE_STATUSES

router = APIRouter(prefix="/me")
MAX_VEHICLES = 20


def vehicle_label(v: UserVehicle) -> str:
    if v.variant:
        m = v.variant.model
        engine = "" if v.variant.engine == "Autre motorisation" else f" {v.variant.engine}"
        return f"{m.brand.name} {m.name}{engine}{f' {v.year}' if v.year else ''}"
    return f"{v.label or 'Voiture'}{f' {v.year}' if v.year else ''}"


def vehicle_out(v: UserVehicle, db: Session | None = None) -> dict:
    extra = {}
    if db is not None:
        due = maintenance.due_items(db, v)
        extra = {"maintenance_due": len(due), "maintenance_items": due,
                 "papers": vehicle_papers.current(db, v), "papers_alerts": vehicle_papers.alerts(db, v),
                 "recalls_count": len(recalls.for_car(db, v))}
    return {**extra, "id": v.id, "plate": format_plate(v.plate), "variant_id": v.variant_id, "year": v.year, "label": v.label,
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
    return [vehicle_out(v, db) for v in rows]


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



class MaintenanceIn(BaseModel):
    """Passage au garage : une ou plusieurs opérations (`items`, ou `item` seul comme avant), opération libre
    (`other` : « pneus avant », « amortisseurs »...), date, kilométrage, prix payé, garage, remarque."""
    item: str | None = Field(None, max_length=40)
    items: list[str] = Field(default_factory=list, max_length=20)
    other: str | None = Field(None, max_length=80)
    km: int | None = Field(None, ge=0, le=2_000_000)
    done_on: date | None = None
    price: float | None = Field(None, ge=0, le=10_000_000)
    place: str | None = Field(None, max_length=120)
    note: str | None = Field(None, max_length=300)
    shop_id: int | None = None   # magasin DALIL (parmi ceux que le client a contactés)


OTHER = "autre"


def _clean(v: str | None) -> str | None:
    v = (v or "").strip()
    return v or None


def _visit_values(body: MaintenanceIn) -> tuple[list[str], str | None, date]:
    known = {it["slug"] for it in maintenance.items()}
    items = list(dict.fromkeys([*([body.item] if body.item else []), *body.items]))
    if any(i not in known for i in items):
        raise HTTPException(422, "Entretien inconnu")
    other = _clean(body.other)
    if not items and not other:
        raise HTTPException(422, "Choisissez au moins une opération, ou écrivez ce qui a été fait")
    done_on = body.done_on or date.today()
    if done_on > date.today():
        raise HTTPException(422, "La date ne peut pas être dans le futur")
    return items, other, done_on


def _fill_visit(db: Session, visit: MaintenanceVisit, car: UserVehicle, body: MaintenanceIn) -> None:
    items, other, done_on = _visit_values(body)
    shop = None
    if body.shop_id is not None:
        shop = db.get(Shop, body.shop_id)
        if not shop or shop.status not in RECOMMENDABLE_STATUSES:
            raise HTTPException(422, "Magasin inconnu")
    visit.done_on, visit.km, visit.price, visit.shop_id = done_on, body.km, body.price, shop.id if shop else None
    visit.place, visit.note = _clean(body.place) or (shop.name if shop else None), _clean(body.note)
    visit.records = [MaintenanceRecord(user_vehicle_id=car.id, item=i, km=body.km, done_on=done_on) for i in items] +         ([MaintenanceRecord(user_vehicle_id=car.id, item=OTHER, label=other, km=body.km, done_on=done_on)] if other else [])
    if body.km is not None and (car.mileage_km is None or body.km > car.mileage_km):
        car.mileage_km = body.km   # un kilométrage plus grand met la voiture à jour


def visit_out(v: MaintenanceVisit, db: Session | None = None) -> dict:
    names = {it["slug"]: it["name"] for it in maintenance.items()}
    shop = db.get(Shop, v.shop_id) if db is not None and v.shop_id else None
    return {"id": v.id, "done_on": v.done_on.isoformat(), "km": v.km, "price": v.price, "place": v.place, "note": v.note,
            "shop": {"id": shop.id, "name": shop.name} if shop else None,
            "operations": [{"id": r.id, "item": r.item, "name": r.label if r.item == OTHER else names.get(r.item, r.item)}
                           for r in v.records]}


@router.get("/vehicles/{vehicle_id}/maintenance")
def vehicle_maintenance(vehicle_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Prochains entretiens d'une voiture (intervalles indicatifs ; le carnet du constructeur fait foi)."""
    car = _own(db, user, vehicle_id)
    return {"mileage_km": car.mileage_km, "items": maintenance.schedule(db, car)}


@router.get("/vehicles/{vehicle_id}/maintenance/history")
def maintenance_history(vehicle_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Carnet d'entretien : passages du plus récent au plus ancien, total payé, total des 12 derniers mois."""
    car = _own(db, user, vehicle_id)
    visits = list(db.scalars(select(MaintenanceVisit).where(MaintenanceVisit.user_vehicle_id == car.id)
                             .order_by(MaintenanceVisit.done_on.desc(), MaintenanceVisit.id.desc())))
    year_ago = maintenance.add_months(date.today(), -12)
    return {"visits": [visit_out(v, db) for v in visits],
            "total": sum(v.price or 0 for v in visits),
            "total_12_months": sum(v.price or 0 for v in visits if v.done_on > year_ago),
            "priced": sum(1 for v in visits if v.price is not None)}


@router.post("/vehicles/{vehicle_id}/maintenance", status_code=201)
def maintenance_done(vehicle_id: int, body: MaintenanceIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Noter un passage au garage (aujourd'hui par défaut) avec ses opérations, son prix et son kilométrage."""
    car = _own(db, user, vehicle_id)
    visit = MaintenanceVisit(user_vehicle_id=car.id, done_on=date.today())
    _fill_visit(db, visit, car, body)
    db.add(visit)
    db.commit()
    return {"id": visit.records[0].id, "visit_id": visit.id}


def _own_visit(db: Session, car: UserVehicle, visit_id: int) -> MaintenanceVisit:
    v = db.get(MaintenanceVisit, visit_id)
    if not v or v.user_vehicle_id != car.id:
        raise HTTPException(404, "Entretien inconnu")
    return v


@router.put("/vehicles/{vehicle_id}/maintenance/visits/{visit_id}")
def maintenance_visit_update(vehicle_id: int, visit_id: int, body: MaintenanceIn, user: User = Depends(current_user),
                             db: Session = Depends(get_db)):
    """Corriger un passage : date, kilométrage, prix, garage, remarque, opérations."""
    car = _own(db, user, vehicle_id)
    visit = _own_visit(db, car, visit_id)
    _fill_visit(db, visit, car, body)
    db.commit()
    return visit_out(visit, db)


@router.delete("/vehicles/{vehicle_id}/maintenance/visits/{visit_id}", status_code=204)
def maintenance_visit_delete(vehicle_id: int, visit_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    car = _own(db, user, vehicle_id)
    db.delete(_own_visit(db, car, visit_id))
    db.commit()


@router.delete("/vehicles/{vehicle_id}/maintenance/{record_id}", status_code=204)
def maintenance_undo(vehicle_id: int, record_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """« Annuler » une opération ; le passage disparaît avec sa dernière opération."""
    car = _own(db, user, vehicle_id)
    rec = db.get(MaintenanceRecord, record_id)
    if not rec or rec.user_vehicle_id != car.id:
        raise HTTPException(404, "Entretien inconnu")
    visit = rec.visit
    db.delete(rec)
    db.flush()
    if visit is not None and not db.scalars(select(MaintenanceRecord).where(MaintenanceRecord.visit_id == visit.id)).first():
        db.delete(visit)
    db.commit()


# --- Rappels des constructeurs -------------------------------------------------

@router.get("/vehicles/{vehicle_id}/recalls")
def vehicle_recalls(vehicle_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Rappels publiés en France (RappelConso) pour le modèle de la voiture : « rappel possible », à vérifier avec le
    numéro de châssis sur la fiche officielle ou chez le concessionnaire."""
    car = _own(db, user, vehicle_id)
    return {"recalls": recalls.for_car(db, car), "vin": car.vin,
            "source": "RappelConso (DGCCRF), Licence Ouverte v2.0"}


# --- Magasins contactés (pour le carnet) -------------------------------------

def _naive(d: datetime) -> datetime:
    return d.replace(tzinfo=None) if d.tzinfo else d


@router.get("/contacted-shops")
def contacted_shops(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Magasins DALIL que le client a contactés : appels et WhatsApp depuis cet appareil (empreinte, 6 mois) et
    magasins qui ont répondu « disponible » à ses demandes. Pour relier un passage du carnet à un magasin."""
    since = datetime.now(timezone.utc) - timedelta(days=180)
    last: dict[int, datetime] = {}
    rows = list(db.execute(select(ContactEvent.shop_id, ContactEvent.created_at)
                           .where(ContactEvent.client_hash == client_hash(request), ContactEvent.created_at >= since)))
    rows += [r for r in db.execute(select(RequestResponse.shop_id, RequestResponse.responded_at)
                                   .join(PartRequest, PartRequest.id == RequestResponse.request_id)
                                   .where(PartRequest.user_id == user.id, RequestResponse.available.is_(True)))
             if r[1] is not None]
    for sid, at in rows:
        last[sid] = max(last.get(sid, _naive(at)), _naive(at))
    shops = list(db.scalars(select(Shop).where(Shop.id.in_(last), Shop.status.in_(RECOMMENDABLE_STATUSES))))
    shops.sort(key=lambda s: last[s.id], reverse=True)
    return [{"id": s.id, "name": s.name, "commune": s.commune.nom_fr if s.commune else None, "is_demo": s.is_demo}
            for s in shops[:20]]


# --- Papiers : contrôle technique et assurance -------------------------------

class PaperIn(BaseModel):
    kind: str = Field(..., pattern="^(controle|assurance)$")
    done_on: date | None = None
    valid_until: date
    provider: str | None = Field(None, max_length=120)
    price: float | None = Field(None, ge=0, le=10_000_000)
    note: str | None = Field(None, max_length=300)


def _fill_paper(doc: VehicleDocument, body: PaperIn) -> None:
    today = date.today()
    if body.done_on and body.done_on > today:
        raise HTTPException(422, "La date où il a été fait ne peut pas être dans le futur")
    if body.done_on and body.valid_until <= body.done_on:
        raise HTTPException(422, "La date de fin doit venir après la date où il a été fait")
    if body.valid_until > maintenance.add_months(today, 120):
        raise HTTPException(422, "Date de fin trop lointaine : vérifiez-la sur le document")
    doc.kind, doc.done_on, doc.valid_until = body.kind, body.done_on, body.valid_until
    doc.provider, doc.price, doc.note = _clean(body.provider), body.price, _clean(body.note)


def _own_paper(db: Session, car: UserVehicle, doc_id: int) -> VehicleDocument:
    d = db.get(VehicleDocument, doc_id)
    if not d or d.user_vehicle_id != car.id:
        raise HTTPException(404, "Document inconnu")
    return d


@router.get("/vehicles/{vehicle_id}/papers")
def papers(vehicle_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Contrôle technique et assurance en cours (état, jours restants) et historique des renouvellements."""
    car = _own(db, user, vehicle_id)
    return {"current": vehicle_papers.current(db, car),
            "history": [vehicle_papers.doc_out(d) for d in vehicle_papers.history(db, car)]}


@router.post("/vehicles/{vehicle_id}/papers", status_code=201)
def paper_add(vehicle_id: int, body: PaperIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    car = _own(db, user, vehicle_id)
    doc = VehicleDocument(user_vehicle_id=car.id)
    _fill_paper(doc, body)
    db.add(doc)
    db.commit()
    return vehicle_papers.doc_out(doc)


@router.put("/vehicles/{vehicle_id}/papers/{doc_id}")
def paper_update(vehicle_id: int, doc_id: int, body: PaperIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    car = _own(db, user, vehicle_id)
    doc = _own_paper(db, car, doc_id)
    _fill_paper(doc, body)
    db.commit()
    return vehicle_papers.doc_out(doc)


@router.delete("/vehicles/{vehicle_id}/papers/{doc_id}", status_code=204)
def paper_delete(vehicle_id: int, doc_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    car = _own(db, user, vehicle_id)
    db.delete(_own_paper(db, car, doc_id))
    db.commit()


@router.get("/alerts")
def alerts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Repère de l'onglet Compte : papiers qui finissent dans 30 jours au plus ou expirés, entretiens à faire."""
    cars = list(db.scalars(select(UserVehicle).where(UserVehicle.user_id == user.id)))
    return {"papers": sum(len(vehicle_papers.alerts(db, c)) for c in cars),
            "maintenance": sum(maintenance.due_count(db, c) for c in cars),
            "prices": price_watch.alert_count(db, user)}


# --- Prix suivis -------------------------------------------------------------

class PriceWatchIn(BaseModel):
    category_id: int
    variant_id: int | None = None


@router.get("/price-watches")
def price_watches(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Pièces suivies : prix de référence, prix le plus bas du moment et son magasin, alerte (baisse ou disponible)."""
    return price_watch.watches(db, user)


@router.post("/price-watches", status_code=201)
def price_watch_add(body: PriceWatchIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Suivre le prix d'une pièce ; référence = prix le plus bas du jour. Suivre deux fois la même pièce ne crée rien."""
    if not db.get(PartCategory, body.category_id):
        raise HTTPException(404, "Pièce inconnue")
    if body.variant_id is not None and not db.get(VehicleVariant, body.variant_id):
        raise HTTPException(422, "Véhicule inconnu")
    w = db.scalar(select(PriceWatch).where(PriceWatch.user_id == user.id, PriceWatch.category_id == body.category_id))
    if w is None:
        if len(list(db.scalars(select(PriceWatch.id).where(PriceWatch.user_id == user.id)))) >= price_watch.MAX_WATCHES:
            raise HTTPException(409, f"{price_watch.MAX_WATCHES} pièces suivies au plus : retirez-en une")
        low = price_history.lowest(db, body.category_id)
        w = PriceWatch(user_id=user.id, category_id=body.category_id, variant_id=body.variant_id,
                       reference_price=low["price"] if low else None)
        db.add(w)
        try:
            db.commit()
        except IntegrityError:   # deux touchers rapides
            db.rollback()
            w = db.scalar(select(PriceWatch).where(PriceWatch.user_id == user.id, PriceWatch.category_id == body.category_id))
    return price_watch.watch_out(db, w)


def _own_watch(db: Session, user: User, watch_id: int) -> PriceWatch:
    w = db.get(PriceWatch, watch_id)
    if not w or w.user_id != user.id:
        raise HTTPException(404, "Suivi inconnu")
    return w


@router.post("/price-watches/{watch_id}/seen")
def price_watch_seen(watch_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """« Vu » : le prix le plus bas du moment devient la référence ; l'alerte disparaît jusqu'à la prochaine baisse."""
    w = _own_watch(db, user, watch_id)
    low = price_history.lowest(db, w.category_id)
    w.reference_price = low["price"] if low else w.reference_price
    db.commit()
    return price_watch.watch_out(db, w)


@router.delete("/price-watches/{watch_id}", status_code=204)
def price_watch_delete(watch_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(_own_watch(db, user, watch_id))
    db.commit()
