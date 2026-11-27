"""Inscription et connexion par mot de passe (27/11/2026, SMS payants) ; unicité du téléphone et du matricule."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import User, UserVehicle
from app.security import hash_password, verify_password

API = "/api/v1"


def _register(client, phone, password="motdepasse1", **extra):
    return client.post(f"{API}/auth/register", json={"first_name": "Nadia", "last_name": "Bouzid", "phone": phone,
                                                      "password": password, "consent": True, **extra})


def _h(r):
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_empreinte_du_mot_de_passe():
    h = hash_password("secret123")
    assert "secret123" not in h and h.startswith("scrypt$")
    assert verify_password("secret123", h) and not verify_password("secret124", h)
    assert hash_password("secret123") != h   # sel différent à chaque fois
    assert not verify_password("secret123", None) and not verify_password("x", "abîmé")


def test_inscription_puis_connexion(client, db):
    r = _register(client, "0661 20 30 40", email="Nadia@Exemple.dz")
    assert r.status_code == 201, r.text
    u = r.json()["user"]
    assert u["complete"] and u["has_password"] and u["consent"] and u["phone"] == "+213661203040"
    assert u["email"] == "nadia@exemple.dz"
    stored = db.scalar(select(User).where(User.phone == "+213661203040")).password_hash
    assert "motdepasse1" not in stored
    # Connexion avec le numéro écrit autrement
    ok = client.post(f"{API}/auth/login", json={"phone": "+213661203040", "password": "motdepasse1"})
    assert ok.status_code == 200 and client.get(f"{API}/auth/me", headers=_h(ok)).json()["first_name"] == "Nadia"
    # Mauvais mot de passe et numéro inconnu : même réponse, rien ne dit qui a un compte
    bad = client.post(f"{API}/auth/login", json={"phone": "0661203040", "password": "faux-faux"})
    unknown = client.post(f"{API}/auth/login", json={"phone": "0661999999", "password": "faux-faux"})
    assert bad.status_code == unknown.status_code == 401 and bad.json() == unknown.json()
    assert client.post(f"{API}/auth/login", json={"phone": "n'importe quoi", "password": "x"}).status_code == 401


def test_inscription_refusee(client):
    assert _register(client, "0661200001", password="court").status_code == 422
    assert "8 caractères" in _register(client, "0661200001", password="court").text
    assert client.post(f"{API}/auth/register", json={"first_name": "A", "last_name": "B", "phone": "0661200001",
                                                      "password": "motdepasse1"}).status_code == 422   # sans consentement
    assert _register(client, "0661200001", first_name="").status_code == 422
    assert _register(client, "12345").status_code == 422


def test_numero_unique_quel_que_soit_son_ecriture(client, db):
    assert _register(client, "0770 11 22 33").status_code == 201
    for same in ["0770112233", "+213770112233", "00213 770 11 22 33", "0770-11-22-33"]:
        r = _register(client, same, password="autremotdepasse")
        assert r.status_code == 409 and "déjà un compte" in r.json()["detail"], same
    assert len(list(db.scalars(select(User).where(User.phone == "+213770112233")))) == 1
    # La base elle-même refuse un doublon (index unique), même sans passer par l'API
    db.add(User(phone="+213770112233", role="driver"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_matricule_unique_dans_la_base_et_entre_ses_propres_voitures(client, db):
    h = _h(_register(client, "0662000001"))
    other = _h(_register(client, "0662000002"))
    a = client.post(f"{API}/me/vehicles", headers=h, json={"plate": "11223-115-31", "label": "Peugeot 206"}).json()
    b = client.post(f"{API}/me/vehicles", headers=h, json={"plate": "44556-118-16", "label": "Dacia Logan"}).json()
    # Le même client ne peut pas non plus enregistrer deux fois le même matricule
    assert client.post(f"{API}/me/vehicles", headers=h, json={"plate": "11223 115 31", "label": "x"}).status_code == 409
    # Changer le matricule d'une voiture pour celui d'une autre : refusé (le sien comme celui d'un autre client)
    assert client.patch(f"{API}/me/vehicles/{b['id']}", headers=h, json={"plate": "11223.115.31"}).status_code == 409
    c = client.post(f"{API}/me/vehicles", headers=other, json={"plate": "77889-120-31", "label": "Kia Picanto"}).json()
    assert client.patch(f"{API}/me/vehicles/{c['id']}", headers=other, json={"plate": "11223-115-31"}).status_code == 409
    # Garder son propre matricule dans une modification : accepté
    assert client.patch(f"{API}/me/vehicles/{a['id']}", headers=h, json={"plate": "11223-115-31", "mileage_km": 5}).status_code == 200
    # La base elle-même refuse un doublon (contrainte unique)
    owner = db.scalar(select(UserVehicle).where(UserVehicle.plate == "1122311531")).user_id
    db.add(UserVehicle(user_id=owner, plate="1122311531", label="doublon"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_changer_son_mot_de_passe_et_reinitialisation_par_l_administrateur(client, admin_headers):
    h = _h(_register(client, "0663000001"))
    assert client.post(f"{API}/auth/me/password", headers=h, json={"current": "mauvais", "new": "nouveau-mdp"}).status_code == 400
    assert client.post(f"{API}/auth/me/password", headers=h, json={"current": "motdepasse1", "new": "court"}).status_code == 422
    assert client.post(f"{API}/auth/me/password", headers=h, json={"current": "motdepasse1", "new": "nouveau-mdp"}).status_code == 200
    assert client.post(f"{API}/auth/login", json={"phone": "0663000001", "password": "nouveau-mdp"}).status_code == 200
    # Mot de passe oublié : l'administrateur donne un mot de passe provisoire
    r = client.post(f"{API}/admin/users/reset-password", headers=admin_headers, json={"phone": "0663 00 00 01"})
    temp = r.json()["temporary_password"]
    assert len(temp) == 10
    assert client.post(f"{API}/auth/login", json={"phone": "0663000001", "password": "nouveau-mdp"}).status_code == 401
    assert client.post(f"{API}/auth/login", json={"phone": "0663000001", "password": temp}).status_code == 200
    assert client.post(f"{API}/admin/users/reset-password", headers=h, json={"phone": "0663000001"}).status_code == 403
    assert client.post(f"{API}/admin/users/reset-password", headers=admin_headers, json={"phone": "0663999999"}).status_code == 404


def test_compte_supprime_libere_le_numero(client):
    h = _h(_register(client, "0664000001"))
    assert client.delete(f"{API}/auth/me", headers=h).status_code == 204
    assert client.post(f"{API}/auth/login", json={"phone": "0664000001", "password": "motdepasse1"}).status_code == 401
    assert _register(client, "0664000001", password="un-autre-mdp").status_code == 201
