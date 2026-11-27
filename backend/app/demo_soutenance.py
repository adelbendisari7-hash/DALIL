"""Scénario de démonstration pour la soutenance (28/11/2026) : un compte client fictif prêt à montrer en 5 minutes
(docs/demo-soutenance.md). Tout est fictif et marqué [DÉMO] ; rejouable (le compte est remis à zéro à chaque
lancement) ; supprimé par `python -m app.seed --purge-demo`.

    cd backend && python -m app.demo_soutenance

Contenu : une Clio 4 avec son carnet (trois passages, dont un dans un garage de démonstration), une vidange dépassée,
une assurance qui finit dans 5 jours et un contrôle technique valable, un prix suivi en baisse (plaquettes avant), une
demande de pièce à laquelle un magasin de démonstration a répondu, un avis vérifié sur ce magasin, et l'historique des
prix de la pièce sur six mois. Les magasins de démonstration doivent exister (`python -m app.seed`).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (Brand, ContactEvent, DiagnosisSession, Feedback, MaintenanceRecord, MaintenanceVisit, Model, PartCategory,
                     PartRequest, PricePoint, PriceWatch, Product, RequestResponse, Shop, User, UserVehicle, VehicleDocument,
                     VehicleTransfer, VehicleVariant)
from .security import hash_password

PHONE = "+213550000101"          # numéro fictif, de la même série que les magasins de démonstration
PASSWORD = "demo-soutenance"
PLATE = "0000113131"              # 00001-131-31 : matricule manifestement fictif
GARAGE = "[DÉMO] Garage Mécanique El Bahia"
CLIENT_HASH = "demo-soutenance"   # empreinte fixe des contacts et avis de démonstration


def _clear_user(db: Session, user: User) -> None:
    for s in db.scalars(select(DiagnosisSession).where(DiagnosisSession.user_id == user.id)):
        s.user_id, s.user_vehicle_id = None, None
    # Les enfants d'abord, puis les parents : la session garde une image exacte de la base (rejouable sans avertissement)
    cars = list(db.scalars(select(UserVehicle).where(UserVehicle.user_id == user.id)))
    reqs = list(db.scalars(select(PartRequest).where(PartRequest.user_id == user.id)))
    for model in (MaintenanceRecord, MaintenanceVisit, VehicleDocument, VehicleTransfer):
        for row in db.scalars(select(model).where(model.user_vehicle_id.in_([c.id for c in cars]))):
            db.delete(row)
    for rr in db.scalars(select(RequestResponse).where(RequestResponse.request_id.in_([r.id for r in reqs]))):
        db.delete(rr)
    db.flush()
    for row in [*cars, *reqs, *db.scalars(select(PriceWatch).where(PriceWatch.user_id == user.id))]:
        db.delete(row)
    db.flush()


def purge(db: Session) -> None:
    """Retire le compte de démonstration (appelé par seed --purge-demo) ; le garage part avec les magasins fictifs."""
    user = db.scalar(select(User).where(User.phone == PHONE))
    if user is not None:
        _clear_user(db, user)
        db.delete(user)
    for model in (Feedback, ContactEvent):
        for row in db.scalars(select(model).where(model.client_hash == CLIENT_HASH)):
            db.delete(row)


def _variant(db: Session) -> VehicleVariant | None:
    return db.scalar(select(VehicleVariant).join(Model).join(Brand)
                     .where(Brand.name == "Renault", Model.name == "Clio 4").order_by(VehicleVariant.id))


def run(db: Session, today: date | None = None) -> dict:
    today = today or date.today()
    now = datetime.now(timezone.utc)
    shops = list(db.scalars(select(Shop).where(Shop.is_demo.is_(True), Shop.shop_type != "garage").order_by(Shop.id)))
    if not shops:
        raise SystemExit("Aucun magasin de démonstration : lancez d'abord python -m app.seed")
    plaq = db.scalar(select(PartCategory).where(PartCategory.slug == "plaquettes-avant"))

    # Compte client fictif, remis à zéro
    user = db.scalar(select(User).where(User.phone == PHONE))
    if user is None:
        user = User(phone=PHONE)
        db.add(user)
    else:
        _clear_user(db, user)
    user.first_name, user.last_name, user.name = "[DÉMO] Amina", "Démo", "[DÉMO] Amina Démo"
    user.role, user.consent_at, user.password_hash = "driver", now, hash_password(PASSWORD)
    for model in (Feedback, ContactEvent):
        for row in db.scalars(select(model).where(model.client_hash == CLIENT_HASH)):
            db.delete(row)
    db.flush()

    # Garage de démonstration (spécialités), vérifié
    garage = db.scalar(select(Shop).where(Shop.name == GARAGE))
    if garage is None:
        garage = Shop(name=GARAGE, phone="+213550009001", whatsapp="+213550009001", lat=35.6971, lng=-0.6337,
                      hours="Sam-Jeu 8h-17h", shop_type="garage", specialties=["freinage-suspension", "mecanique-generale"],
                      status="verified", source="terrain", verified_at=now, visited_at=now, is_demo=True, surveyor="démo")
        db.add(garage)
        db.flush()

    # La voiture : vidange dépassée (98 000 km, dernière à 86 000), papiers, carnet
    v = _variant(db)
    car = UserVehicle(user_id=user.id, plate=PLATE, variant_id=v.id if v else None, label=None if v else "Renault Clio 4",
                      year=2016, nickname="[DÉMO] Clio", mileage_km=98000)
    db.add(car)
    db.flush()
    for days, km, items, price, place, shop in [
        (330, 86000, ["vidange", "filtre-air"], 9500, "[DÉMO] Garage du quartier", None),
        (200, 91000, ["plaquettes"], 7200, None, garage),
        (60, 96500, ["filtre-habitacle"], 2500, "[DÉMO] Station de lavage", None),
    ]:
        done = today - timedelta(days=days)
        visit = MaintenanceVisit(user_vehicle_id=car.id, done_on=done, km=km, price=price,
                                 place=place or (shop.name if shop else None), shop_id=shop.id if shop else None)
        visit.records = [MaintenanceRecord(user_vehicle_id=car.id, item=i, km=km, done_on=done) for i in items]
        db.add(visit)
    db.add(VehicleDocument(user_vehicle_id=car.id, kind="assurance", done_on=today - timedelta(days=360),
                           valid_until=today + timedelta(days=5), provider="[DÉMO] Assurance fictive"))
    db.add(VehicleDocument(user_vehicle_id=car.id, kind="controle", done_on=today - timedelta(days=300),
                           valid_until=today + timedelta(days=430), provider="[DÉMO] Centre de contrôle"))

    # Historique des prix des plaquettes chez les magasins de démonstration (six mois), puis une baisse
    products = list(db.scalars(select(Product).where(Product.shop_id.in_([s.id for s in shops]), Product.category_id == plaq.id,
                                                     Product.price.is_not(None))))
    if products and not db.scalar(select(PricePoint).where(PricePoint.product_id == products[0].id,
                                                           PricePoint.recorded_at < now - timedelta(days=60))):
        for p in products:
            for days, k in ((170, 1.18), (130, 1.12), (95, 1.08), (50, 1.04)):
                db.add(PricePoint(product_id=p.id, shop_id=p.shop_id, category_id=p.category_id, condition=p.condition,
                                  price=round(p.price * k, -1), recorded_at=now - timedelta(days=days)))
    low = min((p.price for p in products), default=None)
    db.add(PriceWatch(user_id=user.id, category_id=plaq.id, variant_id=car.variant_id,
                      reference_price=round(low * 1.2, -1) if low else None))   # suivi quand c'était 20 % plus cher

    # Demande de pièce à laquelle un magasin a répondu ; avis vérifié sur ce magasin
    shop = next((s for s in shops if any(p.shop_id == s.id for p in products)), shops[0])
    req = PartRequest(user_id=user.id, category_id=plaq.id, variant_id=car.variant_id, status="answered",
                      token="demo-soutenance-demande", created_at=now - timedelta(hours=3))
    db.add(req)
    db.flush()
    db.add(RequestResponse(request_id=req.id, shop_id=shop.id, available=True, price=low,
                           notified_at=now - timedelta(hours=3), responded_at=now - timedelta(hours=2)))
    db.add(ContactEvent(shop_id=shop.id, channel="call", category_id=plaq.id, client_hash=CLIENT_HASH,
                        created_at=now - timedelta(days=2, hours=1)))
    db.add(Feedback(shop_id=shop.id, category_id=plaq.id, part_found=True, client_hash=CLIENT_HASH,
                    created_at=now - timedelta(days=2)))
    db.commit()
    return {"phone": "0550000101", "password": PASSWORD, "car_id": car.id, "garage_id": garage.id, "shop_id": shop.id}


def main() -> None:
    from .db import SessionLocal
    with SessionLocal() as db:
        out = run(db)
    print("Compte de démonstration prêt (fictif) : numéro 0550 00 01 01, mot de passe « demo-soutenance ».")
    print(f"Voiture [DÉMO] Clio (matricule 00001-131-31), garage {GARAGE}, magasin n° {out['shop_id']}.")
    print("Déroulé : docs/demo-soutenance.md ; suppression : python -m app.seed --purge-demo")


if __name__ == "__main__":
    main()
