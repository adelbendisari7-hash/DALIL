"""Plan côté magasin, phase 4 : statistiques du magasin, « ce que cherchent les clients près de chez vous », badge
« Répond vite » (idée D), compteur des demandes en attente."""
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models import ContactEvent, PartCategory, PartRequest, RequestResponse, Shop
from app.services import shop_stats

API = "/api/v1"
NOW = datetime.now(timezone.utc)


def _client(ip: str) -> TestClient:
    return TestClient(app, client=(ip, 50000))


def _shop(client, db, n: int, families=("freinage",)):
    r = client.post(f"{API}/auth/register", json={"first_name": "Gérant", "last_name": "Stats", "phone": f"06930{n:05d}",
                                                  "password": "stats-1234", "consent": True})
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    client.patch(f"{API}/auth/me", headers=h, json={"role": "shop_owner"})
    cats = [db.scalar(select(PartCategory).where(PartCategory.slug == f)).id for f in families]
    sid = client.post(f"{API}/shops", headers=h, json={"name": f"Stats {n}", "lat": 35.70, "lng": -0.63,
                                                       "category_ids": cats}).json()["id"]
    shop = db.get(Shop, sid)
    shop.status, shop.verified_at = "claimed", NOW
    db.commit()
    return h, sid


def _cat(db, slug):
    return db.scalar(select(PartCategory).where(PartCategory.slug == slug)).id


def test_apparitions_et_vues_une_fois_par_client_et_par_jour(client, db):
    h, sid = _shop(client, db, 1)
    cat = _cat(db, "plaquettes-avant")
    a, b = _client("10.9.0.1"), _client("10.9.0.2")
    for c in (a, a, a, b):   # le client A recharge deux fois : compté une fois
        assert any(x["id"] == sid for x in c.get(f"{API}/shops/recommend?category_id={cat}&lat=35.70&lng=-0.63").json())
    for c in (a, a, b):
        c.get(f"{API}/shops/{sid}")
    client.get(f"{API}/shops/{sid}", headers=h)   # le gérant qui regarde sa fiche ne compte pas
    cur = client.get(f"{API}/shops/{sid}/stats", headers=h).json()["current"]
    assert (cur["impressions"], cur["views"]) == (2, 2)


def test_contacts_demandes_delai_et_comparaison(client, db):
    h, sid = _shop(client, db, 2)
    cat = _cat(db, "plaquettes-avant")
    for ch in ("call", "call", "whatsapp"):
        db.add(ContactEvent(shop_id=sid, channel=ch, created_at=NOW - timedelta(days=2)))
    db.add(ContactEvent(shop_id=sid, channel="call", created_at=NOW - timedelta(days=40)))   # mois précédent
    for i, minutes in enumerate([10, 30, None]):
        req = PartRequest(category_id=cat)
        db.add(req)
        db.flush()
        sent = NOW - timedelta(days=1, hours=i)
        db.add(RequestResponse(request_id=req.id, shop_id=sid, notified_at=sent, available=None if minutes is None else True,
                               responded_at=None if minutes is None else sent + timedelta(minutes=minutes)))
    db.commit()
    s = client.get(f"{API}/shops/{sid}/stats", headers=h).json()
    assert (s["current"]["calls"], s["current"]["whatsapp"], s["previous"]["calls"]) == (2, 1, 1)
    assert (s["current"]["requests"], s["current"]["answered"], s["current"]["response_minutes"]) == (3, 2, 20)
    assert client.get(f"{API}/part-requests/pending-count", headers=h).json() == {"pending": 1}


def test_ce_que_cherchent_les_clients_pres_de_chez_vous(client, db):
    h, sid = _shop(client, db, 3, families=("freinage",))
    near, far = _client("10.9.1.1"), _client("10.9.1.2")
    plaq, batt = _cat(db, "plaquettes-avant"), _cat(db, "batterie")
    for _ in range(3):
        near.get(f"{API}/shops/recommend?category_id={batt}&lat=35.71&lng=-0.62")   # près, pièce non vendue
    near.get(f"{API}/shops/recommend?category_id={plaq}")                             # sans position : compte
    far.get(f"{API}/shops/recommend?category_id={plaq}&lat=36.50&lng=3.00")          # Alger : ne compte pas
    demand = {d["category_id"]: d for d in client.get(f"{API}/shops/{sid}/stats", headers=h).json()["demand"]}
    assert demand[batt]["searches"] >= 3 and demand[batt]["sold"] is False
    assert demand[plaq]["sold"] is True   # le magasin vend la famille « freinage »
    near_count = demand[plaq]["searches"]
    far.get(f"{API}/shops/recommend?category_id={plaq}&lat=36.50&lng=3.00")
    assert {d["category_id"]: d for d in client.get(f"{API}/shops/{sid}/stats", headers=h).json()["demand"]}[plaq]["searches"] == near_count


def test_badge_repond_vite(client, db):
    h, sid = _shop(client, db, 4)
    cat = _cat(db, "plaquettes-avant")
    assert shop_stats.fast_reply(db, sid) is False   # pas encore d'historique
    for minutes in (5, 15, 40):
        req = PartRequest(category_id=cat)
        db.add(req)
        db.flush()
        db.add(RequestResponse(request_id=req.id, shop_id=sid, notified_at=NOW - timedelta(hours=5), available=True,
                               responded_at=NOW - timedelta(hours=5) + timedelta(minutes=minutes)))
    db.commit()
    assert shop_stats.fast_reply(db, sid) is True
    assert client.get(f"{API}/shops/{sid}").json()["fast_reply"] is True
    rec = client.get(f"{API}/shops/recommend?category_id={cat}").json()
    mine = next(x for x in rec if x["id"] == sid)
    assert mine["fast_reply"] is True and "répond vite aux demandes" in mine["reasons"]
    # Trop de demandes sans réponse : badge perdu
    for _ in range(3):
        req = PartRequest(category_id=cat)
        db.add(req)
        db.flush()
        db.add(RequestResponse(request_id=req.id, shop_id=sid, notified_at=NOW - timedelta(hours=2)))
    db.commit()
    assert shop_stats.fast_reply(db, sid) is False


def test_acces_aux_statistiques(client, db):
    h, sid = _shop(client, db, 5)
    r = client.post(f"{API}/auth/register", json={"first_name": "Vendeur", "last_name": "Stats", "phone": "0693099005",
                                                  "password": "stats-1234", "consent": True})
    vend = {"Authorization": f"Bearer {r.json()['token']}"}
    client.post(f"{API}/shops/{sid}/team", headers=h, json={"phone": "0693099005", "permissions": ["requests"]})
    assert client.get(f"{API}/shops/{sid}/stats", headers=vend).status_code == 403
    uid = client.get(f"{API}/shops/{sid}/team", headers=h).json()["members"][0]["user_id"]
    client.patch(f"{API}/shops/{sid}/team/{uid}", headers=h, json={"permissions": ["requests", "stats"]})
    assert client.get(f"{API}/shops/{sid}/stats", headers=vend).status_code == 200
    assert client.get(f"{API}/shops/{sid}/stats").status_code == 401
