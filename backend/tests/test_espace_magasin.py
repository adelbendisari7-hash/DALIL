"""Étape 10 : espace magasin (modèle Excel, visibilité du catalogue, code de connexion des tests de bout en bout)."""
import io

from openpyxl import Workbook, load_workbook

from app.config import get_settings
from app.security import new_otp
from tests.conftest import login

API = "/api/v1"


def _owner(client, phone: str) -> dict:
    h = login(client, phone)
    token = client.patch(f"{API}/auth/me", json={"role": "shop_owner", "consent": True}, headers=h).json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_modele_excel_du_catalogue(client):
    r = client.get(f"{API}/catalog/template.xlsx")
    assert r.status_code == 200 and "spreadsheetml" in r.headers["content-type"]
    wb = load_workbook(io.BytesIO(r.content))
    assert wb.sheetnames == ["Catalogue", "Exemples", "Familles"]
    assert [c.value for c in wb["Catalogue"][1]] == ["Titre", "Famille", "Reference", "Marque_piece", "Etat", "Prix",
                                                    "En_stock", "Compatibilite"]
    assert wb["Catalogue"].max_row == 1  # feuille à remplir : en-têtes seulement, rien d'importé par erreur
    assert wb["Familles"].max_row > 20


def test_les_exemples_du_modele_s_importent_sans_erreur(client):
    """Les lignes d'exemple doivent être valides : un commerçant qui les recopie ne doit pas avoir d'erreur."""
    h = _owner(client, "0555100200")
    shop = client.post(f"{API}/shops", json={"name": "Magasin modèle"}, headers=h).json()
    src = load_workbook(io.BytesIO(client.get(f"{API}/catalog/template.xlsx").content))["Exemples"]
    wb = Workbook()
    for row in src.iter_rows(min_row=1, max_row=3, values_only=True):
        wb.active.append(list(row))
    buf = io.BytesIO()
    wb.save(buf)
    r = client.post(f"{API}/shops/{shop['id']}/products/import", headers=h,
                    files={"file": ("catalogue.xlsx", buf.getvalue(), "application/octet-stream")}).json()
    assert r == {"created": 2, "updated": 0, "errors": [], "total": 2}


def test_catalogue_d_une_fiche_non_validee_cache_au_public(client, admin_headers):
    h = _owner(client, "0555100300")
    shop = client.post(f"{API}/shops", json={"name": "Magasin en attente"}, headers=h).json()
    client.post(f"{API}/shops/{shop['id']}/products", headers=h,
                json={"title": "Bougie", "category_id": client.get(f"{API}/parts/search", params={"q": "bougies"}).json()[0]["id"]})
    assert client.get(f"{API}/shops/{shop['id']}/products").status_code == 404           # public : caché
    assert len(client.get(f"{API}/shops/{shop['id']}/products", headers=h).json()) == 1   # gérant : visible
    client.post(f"{API}/admin/shops/{shop['id']}/verify", headers=admin_headers)
    assert len(client.get(f"{API}/shops/{shop['id']}/products").json()) == 1             # validé : public


def test_code_fixe_des_tests_seulement_avec_les_sms_de_console(monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "otp_test_code", "123456")
    monkeypatch.setattr(s, "sms_provider", "console")
    assert new_otp() == "123456"
    monkeypatch.setattr(s, "sms_provider", "operateur")  # vrai fournisseur : le code fixe est ignoré
    assert all(new_otp() != "123456" for _ in range(20))


def test_mode_console_annonce_sans_donner_le_code(client, monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "sms_provider", "console")
    r = client.post(f"{API}/auth/otp/request", json={"phone": "0661 55 44 33"}).json()
    assert r["delivery"] == "console" and "code" not in r
    monkeypatch.setattr(s, "sms_provider", "operateur")
    assert client.post(f"{API}/auth/otp/request", json={"phone": "0661 55 44 33"}).json()["delivery"] == "sms"
