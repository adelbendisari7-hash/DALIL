"""Entretien des voitures du compte client : échéances d'après le kilométrage, la date et l'historique noté."""
from datetime import date, timedelta

from sqlalchemy import select

from app.models import UserVehicle, VehicleVariant
from app.services.maintenance import add_months, items

from .conftest import login

API = "/api/v1"


def _car(client, db, phone, mileage, fuel=None, plate="11111-115-31"):
    h = login(client, phone)
    q = select(VehicleVariant)
    if fuel:
        q = q.where(VehicleVariant.fuel == fuel)
    vid = db.scalar(q.order_by(VehicleVariant.id)).id
    car = client.post(f"{API}/me/vehicles", headers=h, json={"plate": plate, "variant_id": vid, "mileage_km": mileage}).json()
    return h, car["id"]


def _plan(client, h, cid):
    return {x["item"]: x for x in client.get(f"{API}/me/vehicles/{cid}/maintenance", headers=h).json()["items"]}


def test_referentiel_coherent(db):
    from app.models import PartCategory
    slugs = {c.slug for c in db.scalars(select(PartCategory))}
    for it in items():
        assert it["part"] in slugs and it["km"] > 0 and it["months"] > 0 and it["why"]
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_carburant_et_sans_historique(client, db):
    h, cid = _car(client, db, "0695000001", 95000, fuel="diesel", plate="20001-115-31")
    plan = _plan(client, h, cid)
    assert "filtre-carburant" in plan and "bougies" not in plan          # diesel : pas de bougies d'allumage
    assert plan["distribution"]["status"] == "check"                      # 95 000 km, rien de noté : à vérifier
    h2, cid2 = _car(client, db, "0695000002", 4000, fuel="essence", plate="20002-115-31")
    plan2 = _plan(client, h2, cid2)
    assert "bougies" in plan2 and "filtre-carburant" not in plan2
    assert plan2["vidange"]["status"] == "ok" and plan2["vidange"]["km_left"] == 6000


def test_entretien_note_puis_echeances(client, db):
    h, cid = _car(client, db, "0695000003", 50000, plate="20003-115-31")
    r = client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"item": "vidange", "km": 49500})
    assert r.status_code == 201
    v = _plan(client, h, cid)["vidange"]
    assert v["status"] == "ok" and v["next_km"] == 59500 and v["km_left"] == 9500
    # Kilométrage qui approche : bientôt ; dépassé : à faire
    client.patch(f"{API}/me/vehicles/{cid}", headers=h, json={"mileage_km": 58500})
    assert _plan(client, h, cid)["vidange"]["status"] == "soon"
    client.patch(f"{API}/me/vehicles/{cid}", headers=h, json={"mileage_km": 60000})
    assert _plan(client, h, cid)["vidange"]["status"] == "due"
    assert client.get(f"{API}/me/vehicles", headers=h).json()[0]["maintenance_due"] >= 1
    # Échéance par la date aussi : vidange notée il y a 13 mois
    old = (date.today() - timedelta(days=400)).isoformat()
    client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"item": "filtre-air", "km": 59000, "done_on": old})
    assert _plan(client, h, cid)["filtre-air"]["status"] == "ok"        # 24 mois : pas encore
    client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"item": "filtre-habitacle", "done_on": old})
    assert _plan(client, h, cid)["filtre-habitacle"]["status"] == "due"  # 12 mois : dépassé


def test_kilometrage_mis_a_jour_et_annulation(client, db):
    h, cid = _car(client, db, "0695000004", 30000, plate="20004-115-31")
    rid = client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"item": "plaquettes", "km": 31000}).json()["id"]
    assert client.get(f"{API}/me/vehicles", headers=h).json()[0]["mileage_km"] == 31000
    assert client.delete(f"{API}/me/vehicles/{cid}/maintenance/{rid}", headers=h).status_code == 204
    assert _plan(client, h, cid)["plaquettes"]["last"] is None


def test_refus(client, db):
    h, cid = _car(client, db, "0695000005", 1000, plate="20005-115-31")
    other = login(client, "0695000006")
    assert client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"item": "inconnu"}).status_code == 422
    future = (date.today() + timedelta(days=3)).isoformat()
    assert client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"item": "vidange", "done_on": future}).status_code == 422
    assert client.get(f"{API}/me/vehicles/{cid}/maintenance", headers=other).status_code == 404
    assert client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=other, json={"item": "vidange"}).status_code == 404


def _history(client, h, cid):
    return client.get(f"{API}/me/vehicles/{cid}/maintenance/history", headers=h).json()


def test_carnet_un_passage_plusieurs_operations_prix_et_garage(client, db):
    h, cid = _car(client, db, "0695000010", 60000, plate="20010-115-31")
    r = client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={
        "items": ["vidange", "filtre-air"], "other": "  Pneus avant Michelin ", "km": 61200,
        "done_on": (date.today() - timedelta(days=10)).isoformat(), "price": 18500, "place": "Garage Benali, Hai Sabah",
        "note": "Huile 5W40"})
    assert r.status_code == 201, r.text
    hist = _history(client, h, cid)
    v = hist["visits"][0]
    assert (v["km"], v["price"], v["place"], v["note"]) == (61200, 18500, "Garage Benali, Hai Sabah", "Huile 5W40")
    assert [o["name"] for o in v["operations"]] == ["Vidange et filtre à huile", "Filtre à air", "Pneus avant Michelin"]
    assert hist["total"] == 18500 and hist["total_12_months"] == 18500 and hist["priced"] == 1
    # Les échéances partent de ce passage ; le kilométrage de la voiture suit
    plan = _plan(client, h, cid)
    assert plan["vidange"]["last"]["km"] == 61200 and plan["filtre-air"]["next_km"] == 81200
    assert client.get(f"{API}/me/vehicles", headers=h).json()[0]["mileage_km"] == 61200


def test_carnet_corriger_puis_supprimer_un_passage(client, db):
    h, cid = _car(client, db, "0695000011", 40000, plate="20011-115-31")
    vid = client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h,
                      json={"items": ["vidange"], "km": 40000, "price": 6000}).json()["visit_id"]
    old = (date.today() - timedelta(days=400)).isoformat()
    client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"other": "Batterie", "done_on": old, "price": 12000})
    hist = _history(client, h, cid)
    assert hist["total"] == 18000 and hist["total_12_months"] == 6000          # la batterie a plus d'un an
    assert [v["operations"][0]["name"] for v in hist["visits"]] == ["Vidange et filtre à huile", "Batterie"]   # récent d'abord
    # Correction : prix, garage, et une opération de plus
    r = client.put(f"{API}/me/vehicles/{cid}/maintenance/visits/{vid}", headers=h,
                   json={"items": ["vidange", "filtre-habitacle"], "km": 40100, "price": 7500, "place": "Mécanicien du quartier"})
    assert r.status_code == 200 and r.json()["price"] == 7500 and len(r.json()["operations"]) == 2
    assert _plan(client, h, cid)["filtre-habitacle"]["status"] == "ok"
    assert client.delete(f"{API}/me/vehicles/{cid}/maintenance/visits/{vid}", headers=h).status_code == 204
    assert _plan(client, h, cid)["vidange"]["last"] is None
    assert len(_history(client, h, cid)["visits"]) == 1


def test_carnet_refus_et_carnet_d_un_autre(client, db):
    h, cid = _car(client, db, "0695000012", 40000, plate="20012-115-31")
    post = lambda body: client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json=body)   # noqa: E731
    assert post({"km": 40000}).status_code == 422                       # aucune opération
    assert post({"other": "   "}).status_code == 422
    assert post({"items": ["inconnu"]}).status_code == 422
    assert post({"items": ["vidange"], "price": -5}).status_code == 422
    assert post({"items": ["vidange"], "done_on": (date.today() + timedelta(days=1)).isoformat()}).status_code == 422
    vid = post({"items": ["vidange"], "price": 5000}).json()["visit_id"]
    h2, cid2 = _car(client, db, "0695000013", 1000, plate="20013-115-31")
    assert client.get(f"{API}/me/vehicles/{cid}/maintenance/history", headers=h2).status_code == 404
    assert client.put(f"{API}/me/vehicles/{cid2}/maintenance/visits/{vid}", headers=h2, json={"items": ["vidange"]}).status_code == 404
    assert client.delete(f"{API}/me/vehicles/{cid2}/maintenance/visits/{vid}", headers=h2).status_code == 404


def test_annuler_la_derniere_operation_retire_le_passage(client, db):
    h, cid = _car(client, db, "0695000014", 40000, plate="20014-115-31")
    rid = client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"item": "vidange", "price": 5000}).json()["id"]
    assert client.delete(f"{API}/me/vehicles/{cid}/maintenance/{rid}", headers=h).status_code == 204
    assert _history(client, h, cid)["visits"] == []
