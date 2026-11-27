"""Compte client (27/11/2026) : profil, voitures au matricule unique, signalement, historique, suppression."""
from datetime import date

from sqlalchemy import select

from app.models import UserVehicle, VehicleVariant
from app.schemas import format_plate, normalize_plate

from .conftest import login

API = "/api/v1"


def _variant(db):
    return db.scalar(select(VehicleVariant).order_by(VehicleVariant.id)).id


def test_matricule_normalise():
    assert normalize_plate("12345 115 31") == normalize_plate("12345-115-31") == "1234511531"
    assert format_plate("1234511531") == "12345-115-31"
    for bad in ["ABC-115-31", "123", "12345-115-00", "123456789012"]:
        try:
            normalize_plate(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepté : {bad}")


def test_profil_obligatoire_et_facultatif(client):
    h = login(client, "0550100001")
    me = client.get(f"{API}/auth/me", headers=h).json()
    assert me["complete"] is False   # nouveau compte : prénom et nom à saisir
    r = client.patch(f"{API}/auth/me", headers=h, json={"first_name": " Amina ", "last_name": "Benali"})
    assert r.status_code == 200 and r.json()["user"]["complete"] is True
    assert r.json()["user"]["name"] == "Amina Benali"
    communes = client.get(f"{API}/geo/communes").json()
    r = client.patch(f"{API}/auth/me", headers=h, json={"email": "Amina@Exemple.dz", "commune_id": communes[0]["id"],
                                                         "birth_date": "1990-05-04", "lang": "ar"})
    u = r.json()["user"]
    assert (u["email"], u["commune_id"], u["birth_date"], u["lang"]) == ("amina@exemple.dz", communes[0]["id"], "1990-05-04", "ar")
    u = client.patch(f"{API}/auth/me", headers=h, json={"clear": ["email", "birth_date"]}).json()["user"]
    assert u["email"] is None and u["birth_date"] is None and u["commune_id"] == communes[0]["id"]
    for bad in [{"first_name": "   "}, {"last_name": "B3nali"}, {"email": "pas-une-adresse"},
                {"birth_date": date.today().isoformat()}, {"commune_id": 999999}, {"clear": ["phone"]}]:
        assert client.patch(f"{API}/auth/me", headers=h, json=bad).status_code == 422, bad


def test_voitures_et_matricule_unique(client, db):
    h1, h2 = login(client, "0550100002"), login(client, "0550100003")
    vid = _variant(db)
    r = client.post(f"{API}/me/vehicles", headers=h1, json={
        "plate": "01234 120 31", "variant_id": vid, "year": 2020, "nickname": "la familiale", "mileage_km": 85000,
        "vin": "vf1bb1b0f12345678"})
    assert r.status_code == 201, r.text
    car = r.json()
    assert car["plate"] == "01234-120-31" and car["vin"] == "VF1BB1B0F12345678" and car["display"]
    # Deuxième voiture, absente du référentiel
    r = client.post(f"{API}/me/vehicles", headers=h1, json={"plate": "55555-199-16", "label": "Zastava Yugo", "year": 1999})
    assert r.status_code == 201 and r.json()["display"] == "Zastava Yugo 1999"
    assert len(client.get(f"{API}/me/vehicles", headers=h1).json()) == 2
    # Même matricule, écrit autrement, sur un autre compte : refusé, sans rien dévoiler du propriétaire
    r = client.post(f"{API}/me/vehicles", headers=h2, json={"plate": "01234-120-31", "variant_id": vid})
    assert r.status_code == 409 and r.json()["detail"]["code"] == "plate_taken"
    assert "0550100002" not in r.text and "familiale" not in r.text
    # Ni modèle ni nom saisi : refusé ; modèle inconnu : refusé
    assert client.post(f"{API}/me/vehicles", headers=h2, json={"plate": "77777-115-31"}).status_code == 422
    assert client.post(f"{API}/me/vehicles", headers=h2, json={"plate": "77777-115-31", "variant_id": 999999}).status_code == 422
    # Un autre client ne voit ni ne modifie ni ne supprime la voiture
    assert client.patch(f"{API}/me/vehicles/{car['id']}", headers=h2, json={"mileage_km": 1}).status_code == 404
    assert client.delete(f"{API}/me/vehicles/{car['id']}", headers=h2).status_code == 404
    assert client.get(f"{API}/me/vehicles", headers=h2).json() == []
    # Modification par le propriétaire
    r = client.patch(f"{API}/me/vehicles/{car['id']}", headers=h1, json={"mileage_km": 90000, "nickname": "la grise"})
    assert r.json()["mileage_km"] == 90000 and r.json()["plate"] == "01234-120-31"
    assert client.get(f"{API}/me/vehicles").status_code == 401


def test_signalement_puis_liberation_du_matricule(client, db, admin_headers):
    owner, claimant = login(client, "0550100004"), login(client, "0550100005")
    vid = _variant(db)
    client.post(f"{API}/me/vehicles", headers=owner, json={"plate": "98765-114-31", "variant_id": vid})
    assert client.post(f"{API}/me/vehicles", headers=claimant, json={"plate": "98765-114-31", "variant_id": vid}).status_code == 409
    r = client.post(f"{API}/me/plate-reports", headers=claimant, json={"plate": "98765 114 31", "message": "Achetée en octobre"})
    assert r.status_code == 201
    again = client.post(f"{API}/me/plate-reports", headers=claimant, json={"plate": "98765-114-31"})
    assert again.json()["id"] == r.json()["id"]   # pas de doublon
    assert client.post(f"{API}/me/plate-reports", headers=claimant, json={"plate": "11111-111-11"}).status_code == 422
    reports = client.get(f"{API}/admin/plate-reports", headers=admin_headers).json()
    rep = next(x for x in reports if x["plate"] == "98765-114-31")
    assert rep["holder"]["phone"] and rep["reporter"]["phone"]
    assert client.get(f"{API}/admin/plate-reports", headers=claimant).status_code == 403
    assert client.post(f"{API}/admin/plate-reports/{rep['id']}/release", headers=admin_headers).json()["status"] == "released"
    assert client.post(f"{API}/admin/plate-reports/{rep['id']}/reject", headers=admin_headers).status_code == 409
    assert client.get(f"{API}/me/vehicles", headers=owner).json() == []
    assert client.post(f"{API}/me/vehicles", headers=claimant, json={"plate": "98765-114-31", "variant_id": vid}).status_code == 201


def test_diagnostic_rattache_a_la_voiture_et_historique(client, db):
    h, other = login(client, "0550100006"), login(client, "0550100007")
    car = client.post(f"{API}/me/vehicles", headers=h, json={"plate": "24680-117-31", "label": "Lada Niva"}).json()
    r = client.post(f"{API}/diagnosis", headers=h, json={"text": "ça grince quand je freine", "user_vehicle_id": car["id"]})
    assert r.status_code == 200 and r.json()["vehicle"] == "Lada Niva"
    sid = r.json()["session_id"]
    hist = client.get(f"{API}/me/diagnoses", headers=h).json()
    assert hist[0]["session_id"] == sid and hist[0]["user_vehicle_id"] == car["id"] and hist[0]["top"]
    assert [x["session_id"] for x in client.get(f"{API}/me/diagnoses?vehicle_id={car['id']}", headers=h).json()] == [sid]
    # La voiture d'un autre ne peut pas servir, ni son historique être lu
    assert client.post(f"{API}/diagnosis", headers=other, json={"text": "bruit", "user_vehicle_id": car["id"]}).status_code == 404
    assert client.post(f"{API}/diagnosis", json={"text": "bruit au freinage", "user_vehicle_id": car["id"]}).status_code == 404
    assert client.get(f"{API}/me/diagnoses?vehicle_id={car['id']}", headers=other).status_code == 404
    assert client.get(f"{API}/me/diagnoses", headers=other).json() == []
    # Voiture retirée : l'historique reste, sans voiture
    assert client.delete(f"{API}/me/vehicles/{car['id']}", headers=h).status_code == 204
    assert client.get(f"{API}/me/diagnoses", headers=h).json()[0]["user_vehicle_id"] is None


def test_suppression_du_compte_efface_voitures_et_profil(client, db):
    h = login(client, "0550100008")
    client.patch(f"{API}/auth/me", headers=h, json={"first_name": "Karim", "last_name": "Haddad", "email": "k@exemple.dz"})
    client.post(f"{API}/me/vehicles", headers=h, json={"plate": "13579-118-31", "label": "Fiat Uno"})
    assert client.delete(f"{API}/auth/me", headers=h).status_code == 204
    db.expire_all()
    assert db.scalar(select(UserVehicle).where(UserVehicle.plate == "1357911831")) is None
    h2 = login(client, "0550100009")   # le matricule redevient libre
    assert client.post(f"{API}/me/vehicles", headers=h2, json={"plate": "13579-118-31", "label": "Fiat Uno"}).status_code == 201
