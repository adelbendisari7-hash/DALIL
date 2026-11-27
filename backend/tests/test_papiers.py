"""Papiers des voitures (contrôle technique, assurance) avec rappels, et magasins DALIL dans le carnet d'entretien."""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.models import Commune, Shop, VehicleVariant
from app.services.vehicle_papers import status

from .conftest import login

API = "/api/v1"


def _car(client, db, phone, plate):
    h = login(client, phone)
    vid = db.scalar(select(VehicleVariant).order_by(VehicleVariant.id)).id
    cid = client.post(f"{API}/me/vehicles", headers=h, json={"plate": plate, "variant_id": vid, "mileage_km": 50000}).json()["id"]
    return h, cid


def _d(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def test_etats_et_seuils():
    t = date(2026, 6, 1)
    assert status(date(2026, 7, 15), t) == ("ok", 44)
    assert status(date(2026, 7, 1), t) == ("soon", 30)
    assert status(date(2026, 6, 8), t) == ("urgent", 7)
    assert status(date(2026, 6, 1), t) == ("urgent", 0)      # dernier jour : encore valable
    assert status(date(2026, 5, 31), t) == ("expired", -1)


def test_controle_et_assurance_rappels_et_renouvellement(client, db):
    h, cid = _car(client, db, "0697000001", "40001-115-31")
    r = client.post(f"{API}/me/vehicles/{cid}/papers", headers=h, json={
        "kind": "controle", "done_on": _d(-700), "valid_until": _d(20), "provider": "Centre de contrôle Es Senia", "price": 2500})
    assert r.status_code == 201 and r.json()["status"] == "soon" and r.json()["days_left"] == 20
    client.post(f"{API}/me/vehicles/{cid}/papers", headers=h, json={
        "kind": "assurance", "done_on": _d(-360), "valid_until": _d(5), "provider": "Assureur X", "note": "Tous risques"})
    car = next(c for c in client.get(f"{API}/me/vehicles", headers=h).json() if c["id"] == cid)
    assert car["papers"]["controle"]["status"] == "soon" and car["papers"]["assurance"]["status"] == "urgent"
    assert {a["kind"] for a in car["papers_alerts"]} == {"controle", "assurance"}
    assert client.get(f"{API}/me/alerts", headers=h).json()["papers"] == 2
    # Assurance renouvelée pour un an : le papier en cours est le nouveau, l'ancien reste dans l'historique
    client.post(f"{API}/me/vehicles/{cid}/papers", headers=h, json={"kind": "assurance", "done_on": _d(0), "valid_until": _d(365)})
    p = client.get(f"{API}/me/vehicles/{cid}/papers", headers=h).json()
    assert p["current"]["assurance"]["status"] == "ok" and p["current"]["assurance"]["days_left"] == 365
    assert len([x for x in p["history"] if x["kind"] == "assurance"]) == 2
    assert client.get(f"{API}/me/alerts", headers=h).json()["papers"] == 1


def test_papier_expire_corrige_puis_supprime(client, db):
    h, cid = _car(client, db, "0697000002", "40002-115-31")
    doc = client.post(f"{API}/me/vehicles/{cid}/papers", headers=h, json={"kind": "controle", "valid_until": _d(-3)}).json()
    assert doc["status"] == "expired" and doc["days_left"] == -3
    r = client.put(f"{API}/me/vehicles/{cid}/papers/{doc['id']}", headers=h, json={"kind": "controle", "valid_until": _d(300)})
    assert r.status_code == 200 and r.json()["status"] == "ok"
    assert client.delete(f"{API}/me/vehicles/{cid}/papers/{doc['id']}", headers=h).status_code == 204
    assert client.get(f"{API}/me/vehicles/{cid}/papers", headers=h).json()["current"]["controle"] is None


def test_papiers_refus_et_voiture_d_un_autre(client, db):
    h, cid = _car(client, db, "0697000003", "40003-115-31")
    post = lambda body: client.post(f"{API}/me/vehicles/{cid}/papers", headers=h, json=body)   # noqa: E731
    assert post({"kind": "vignette", "valid_until": _d(10)}).status_code == 422
    assert post({"kind": "controle"}).status_code == 422                                  # date de fin obligatoire
    assert post({"kind": "controle", "done_on": _d(1), "valid_until": _d(400)}).status_code == 422   # fait dans le futur
    assert post({"kind": "controle", "done_on": _d(-10), "valid_until": _d(-20)}).status_code == 422  # fin avant le début
    assert post({"kind": "assurance", "valid_until": _d(5000)}).status_code == 422          # trop lointaine
    doc = post({"kind": "assurance", "valid_until": _d(30)}).json()
    h2, cid2 = _car(client, db, "0697000004", "40004-115-31")
    assert client.get(f"{API}/me/vehicles/{cid}/papers", headers=h2).status_code == 404
    assert client.put(f"{API}/me/vehicles/{cid2}/papers/{doc['id']}", headers=h2,
                      json={"kind": "assurance", "valid_until": _d(30)}).status_code == 404
    assert client.delete(f"{API}/me/vehicles/{cid2}/papers/{doc['id']}", headers=h2).status_code == 404


def test_magasins_contactes_et_passage_relie_au_magasin(client, db):
    h, cid = _car(client, db, "0697000005", "40005-115-31")
    commune = db.scalar(select(Commune).order_by(Commune.id))
    shop = Shop(name="Pièces Carnet", status="verified", source="terrain", verified_at=datetime.now(timezone.utc),
                commune_id=commune.id)
    draft = Shop(name="Brouillon Carnet", status="draft", source="osm")
    db.add_all([shop, draft])
    db.commit()
    client.post(f"{API}/contact-events", json={"shop_id": shop.id, "channel": "call"})
    client.post(f"{API}/contact-events", json={"shop_id": draft.id, "channel": "call"})
    ids = [s["id"] for s in client.get(f"{API}/me/contacted-shops", headers=h).json()]
    assert shop.id in ids and draft.id not in ids and ids[0] == shop.id     # le plus récent d'abord, brouillon exclu
    assert client.get(f"{API}/me/contacted-shops", headers=h).json()[0]["commune"] == commune.nom_fr
    r = client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"items": ["vidange"], "shop_id": shop.id, "price": 4000})
    assert r.status_code == 201
    v = client.get(f"{API}/me/vehicles/{cid}/maintenance/history", headers=h).json()["visits"][0]
    assert v["shop"] == {"id": shop.id, "name": "Pièces Carnet"} and v["place"] == "Pièces Carnet"
    assert client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h,
                       json={"items": ["vidange"], "shop_id": draft.id}).status_code == 422
