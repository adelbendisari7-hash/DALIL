"""Plan côté magasin, phase 1 : inscription guidée, adresse sur la carte, revendication, vérification par appel,
horaires et « ouvert maintenant », fermeture exceptionnelle, téléphone du magasin unique."""
from datetime import date, datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy import select

from app.models import Shop
from app.services import shop_onboarding as ob

API = "/api/v1"
OPEN = {"days": [5, 6, 0, 1, 2, 3], "from": "08:00", "to": "18:00", "break": ["12:00", "13:30"]}
ORAN = (35.6971, -0.6308)


def _owner(client, phone):
    r = client.post(f"{API}/auth/register", json={"first_name": "Rachid", "last_name": "Kaci", "phone": phone,
                                                  "password": "magasin-123", "consent": True})
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    client.patch(f"{API}/auth/me", headers=h, json={"role": "shop_owner"})
    return h


# --- Horaires ---------------------------------------------------------------------------------------------------

def test_horaires_texte_et_ouvert_maintenant():
    assert ob.hours_text(OPEN) == "Sam-Jeu 8h-18h (pause 12h-13h30)"
    assert ob.hours_text({"days": [5, 0, 2], "from": "09:00", "to": "17:30"}) == "Sam, Lun, Mer 9h-17h30"
    shop = Shop(name="x", opening=OPEN)
    at = lambda d, h, m=0: datetime(2026, 11, d, h - 1, m, tzinfo=timezone.utc)   # heure d'Alger = UTC + 1
    assert ob.open_status(shop, at(28, 10))["open"] is True           # samedi 28/11, 10 h
    assert ob.open_status(shop, at(28, 12, 30))["label"].startswith("En pause")
    assert ob.open_status(shop, at(28, 19))["open"] is False          # après 18 h
    assert ob.open_status(shop, at(27, 10))["open"] is False          # vendredi
    shop.closed_until, shop.closed_note = date(2026, 11, 29), "Aïd"
    s = ob.open_status(shop, at(28, 10))
    assert s["open"] is False and "Aïd" in s["label"] and "29/11" in s["label"]
    assert ob.open_status(Shop(name="y"), at(28, 10)) is None          # horaires inconnus : on ne dit rien


@pytest.mark.parametrize("bad", [{"days": [], "from": "08:00", "to": "18:00"}, {"days": [1], "from": "18:00", "to": "08:00"},
                                 {"days": [1], "from": "8h", "to": "18:00"}, {"days": [9], "from": "08:00", "to": "18:00"},
                                 {"days": [1], "from": "08:00", "to": "18:00", "break": ["19:00", "20:00"]}])
def test_horaires_invalides(bad):
    with pytest.raises(ValueError):
        ob.check_opening(bad)


# --- Recherche d'adresse ----------------------------------------------------------------------------------------

def test_recherche_adresse_dans_la_wilaya_d_oran(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json=[{"display_name": "Rue Larbi Ben M'hidi, Oran", "lat": "35.6990", "lon": "-0.6350"}])

    monkeypatch.setenv("DALIL_GEOCODER_URL", "https://nominatim.example/search")
    from app.config import get_settings
    get_settings.cache_clear()
    try:
        g = ob.Geocoder(client=httpx.Client(transport=httpx.MockTransport(handler)))
        out = g.search("12 rue Larbi Ben M'hidi")
        assert out == [{"label": "Rue Larbi Ben M'hidi, Oran", "lat": 35.699, "lng": -0.635}]
        p = seen[0].url.params
        assert p["bounded"] == "1" and p["countrycodes"] == "dz" and p["q"].endswith(", Oran")
        assert seen[0].headers["User-Agent"] == "DALIL-prototype/0.1"   # identifiant générique, rien sur l'utilisateur
        g.search("12 rue  Larbi Ben M'hidi")   # même adresse : servie par le cache, aucune nouvelle requête
        assert len(seen) == 1
        assert g.search("ab") == []
    finally:
        get_settings.cache_clear()


def test_recherche_adresse_reservee_aux_comptes(client):
    assert client.get(f"{API}/geo/geocode?q=rue%20larbi").status_code == 401
    h = _owner(client, "0671000001")
    assert client.get(f"{API}/geo/geocode?q=rue%20larbi", headers=h).json() == []   # désactivée dans les tests


# --- Inscription, unicité, revendication ---------------------------------------------------------------------

def test_inscription_guidee_par_adresse(client, db):
    h = _owner(client, "0671000002")
    r = client.post(f"{API}/shops", headers=h, json={
        "name": "Pièces Auto El Bahia", "phone": "0671 10 20 30", "lat": ORAN[0], "lng": ORAN[1],
        "address": "12 rue Larbi Ben M'hidi", "landmark": "en face de la poste", "opening": OPEN,
        "brand_ids": [], "category_ids": [], "parts_origin": ["adaptable"], "sale_mode": "detail"})
    assert r.status_code == 201, r.text
    s = r.json()
    assert s["status"] == "draft" and s["hours"] == "Sam-Jeu 8h-18h (pause 12h-13h30)"
    assert s["commune"] == "Oran" and s["landmark"] == "en face de la poste" and s["verified"] is False
    assert s["phone"] == "+213671102030"
    # Même numéro de magasin, écrit autrement : refusé
    h2 = _owner(client, "0671000003")
    r2 = client.post(f"{API}/shops", headers=h2, json={"name": "Autre", "phone": "+213 671 10 20 30"})
    assert r2.status_code == 409 and r2.json()["detail"]["code"] == "shop_phone_taken"
    bad = client.post(f"{API}/shops", headers=h2, json={"name": "Autre", "opening": {"days": []}})
    assert bad.status_code == 422 and "jour d'ouverture" in bad.text


def test_fiche_de_l_equipe_proposee_puis_revendiquee_apres_appel(client, db, admin_headers):
    team = Shop(name="Pièces Saïd Es Senia", phone="+213672000001", lat=35.6500, lng=-0.6200, status="verified",
                source="terrain", verified_at=datetime.now(timezone.utc))
    db.add(team)
    db.commit()
    h = _owner(client, "0672000099")   # le gérant n'a pas le numéro de la fiche
    near = client.get(f"{API}/shops/nearby-claimable?lat=35.6505&lng=-0.6200", headers=h).json()
    assert [x["id"] for x in near] == [team.id] and near[0]["distance_m"] < 150
    by_phone = client.get(f"{API}/shops/nearby-claimable?phone=0672000001", headers=h).json()
    assert [x["id"] for x in by_phone] == [team.id]
    # Créer un doublon au même numéro : refusé, la fiche à revendiquer est indiquée
    r = client.post(f"{API}/shops", headers=h, json={"name": "Saïd", "phone": "0672000001"})
    assert r.status_code == 409 and r.json()["detail"] == {**r.json()["detail"], "code": "shop_phone_claimable", "shop_id": team.id}
    # Revendication : en attente (numéro différent), la fiche reste publique et sans gérant
    assert client.post(f"{API}/shops/{team.id}/claim", headers=h).json()["claim"] == "pending"
    assert client.get(f"{API}/shops/claims/mine", headers=h).json()[0]["status"] == "pending"
    queue = client.get(f"{API}/admin/verification", headers=admin_headers).json()
    claim = next(c for c in queue["claims"] if c["shop"]["id"] == team.id)
    assert claim["user"]["phone"] == "+213672000099"
    assert client.post(f"{API}/admin/claims/{claim['id']}/accept", headers=admin_headers).json()["status"] == "accepted"
    db.expire_all()
    assert db.get(Shop, team.id).status == "claimed" and client.get(f"{API}/shops/mine", headers=h).json()[0]["id"] == team.id
    assert client.post(f"{API}/admin/claims/{claim['id']}/accept", headers=admin_headers).status_code == 404


def test_verification_par_appel_refus_avec_motif_puis_correction(client, admin_headers):
    h = _owner(client, "0673000001")
    sid = client.post(f"{API}/shops", headers=h, json={"name": "Garage Pièces Hai Sabah", "lat": 35.70, "lng": -0.58}).json()["id"]
    assert any(x["id"] == sid for x in client.get(f"{API}/admin/verification", headers=admin_headers).json()["shops"])
    # Liste de contrôle incomplète : refusée
    r = client.post(f"{API}/admin/shops/{sid}/verify", headers=admin_headers, json={"phone_ok": True, "address_ok": True})
    assert r.status_code == 422
    r = client.post(f"{API}/admin/shops/{sid}/reject", headers=admin_headers, json={"reason": "Numéro injoignable"})
    assert r.json()["status"] == "rejected"
    mine = client.get(f"{API}/shops/mine", headers=h).json()[0]
    assert mine["reject_reason"] == "Numéro injoignable"
    # Le magasin corrige : retour dans la file
    fixed = client.patch(f"{API}/shops/{sid}", headers=h, json={"phone": "0673 22 33 44"}).json()
    assert fixed["status"] == "draft" and fixed["reject_reason"] is None
    ok = client.post(f"{API}/admin/shops/{sid}/verify", headers=admin_headers,
                     json={"phone_ok": True, "address_ok": True, "activity_ok": True}).json()
    assert ok["status"] == "claimed" and ok["verified"] is True and ok["verified_at"]
    assert client.get(f"{API}/shops/{sid}").json()["verified"] is True   # badge visible du public


def test_doublon_probable_signale_a_l_administrateur(client, db, admin_headers):
    db.add(Shop(name="Auto Pièces Benali", phone="+213674000001", lat=35.7100, lng=-0.6100, status="verified", source="terrain"))
    db.commit()
    h = _owner(client, "0674000002")
    sid = client.post(f"{API}/shops", headers=h, json={"name": "Benali Auto", "lat": 35.71005, "lng": -0.61003}).json()["id"]
    entry = next(x for x in client.get(f"{API}/admin/verification", headers=admin_headers).json()["shops"] if x["id"] == sid)
    assert [d["name"] for d in entry["duplicates"]] == ["Auto Pièces Benali"]


def test_fermeture_exceptionnelle_et_reconfirmation(client):
    h = _owner(client, "0675000001")
    sid = client.post(f"{API}/shops", headers=h, json={"name": "Pièces Gambetta", "opening": OPEN}).json()["id"]
    until = (date.today() + timedelta(days=3)).isoformat()
    s = client.patch(f"{API}/shops/{sid}", headers=h, json={"closed_until": until, "closed_note": "Aïd"}).json()
    assert s["closed_until"] == until and s["open_status"]["open"] is False and "Aïd" in s["open_status"]["label"]
    s = client.patch(f"{API}/shops/{sid}", headers=h, json={"closed_until": None}).json()
    assert s["closed_until"] is None and s["closed_note"] is None
    far = (date.today() + timedelta(days=200)).isoformat()
    assert client.patch(f"{API}/shops/{sid}", headers=h, json={"closed_until": far}).status_code == 422
    assert client.post(f"{API}/shops/{sid}/reconfirm", headers=h).status_code == 200
    other = _owner(client, "0675000002")
    assert client.post(f"{API}/shops/{sid}/reconfirm", headers=other).status_code == 403
