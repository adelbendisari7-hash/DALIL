"""Étape 11 : un retour « pièce trouvée » modifie le score, mais ne se répète pas pour le gonfler.

Règle : un retour compte une fois par client (empreinte de l'adresse IP) et par jour.
"""
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models import Feedback
from tests.test_api import API, cat_id, variant_id


def _client(ip: str) -> TestClient:
    return TestClient(app, client=(ip, 50000))


def _recommend(client, cid, vid) -> dict[int, dict]:
    return {s["id"]: s for s in client.get(f"{API}/shops/recommend", params={"category_id": cid, "variant_id": vid}).json()}


def test_retour_repete_par_le_meme_client_compte_une_fois(db):
    vid = variant_id(db, "Renault", "Clio", "1.5 dCi", 2016)
    cid = cat_id(db, "kit-embrayage")
    c = _client("10.1.0.1")
    shop = list(_recommend(c, cid, vid).values())[-1]
    assert c.post(f"{API}/feedback", json={"shop_id": shop["id"], "category_id": cid, "part_found": True}).status_code == 201
    once = _recommend(c, cid, vid)[shop["id"]]
    assert once["score"] > shop["score"]  # critère de l'étape 11 : le retour modifie le score
    for _ in range(9):
        c.post(f"{API}/feedback", json={"shop_id": shop["id"], "category_id": cid, "part_found": True})
    again = _recommend(c, cid, vid)[shop["id"]]
    assert again["score"] == once["score"]  # 10 clics du même client = 1 retour
    assert any("pièce trouvée par 1 client" in r for r in again["reasons"])


def test_retours_de_clients_differents_s_additionnent(db):
    vid = variant_id(db, "Renault", "Clio", "1.5 dCi", 2016)
    cid = cat_id(db, "amortisseurs")
    shop = list(_recommend(_client("10.2.0.1"), cid, vid).values())[-1]
    for i in range(3):
        _client(f"10.2.0.{i + 1}").post(f"{API}/feedback", json={"shop_id": shop["id"], "category_id": cid, "part_found": True})
    after = _recommend(_client("10.2.0.9"), cid, vid)[shop["id"]]
    assert any("pièce trouvée par 3 client" in r for r in after["reasons"])


def test_adresse_ip_jamais_conservee(db):
    c = _client("10.3.0.7")
    shop_id = c.get(f"{API}/shops").json()[0]["id"]
    fid = c.post(f"{API}/feedback", json={"shop_id": shop_id, "part_found": False}).json()["id"]
    db.expire_all()
    fb = db.get(Feedback, fid)
    assert fb.client_hash and len(fb.client_hash) == 16 and "10.3.0.7" not in fb.client_hash
    assert db.scalar(select(Feedback.client_hash).where(Feedback.id == fid)) == fb.client_hash


def test_retours_limites_en_debit(monkeypatch):
    from app.security import feedback_limiter

    monkeypatch.setattr(feedback_limiter, "per_minute", 3)
    c = _client("10.4.0.1")
    shop_id = c.get(f"{API}/shops").json()[0]["id"]
    codes = [c.post(f"{API}/feedback", json={"shop_id": shop_id, "part_found": True}).status_code for _ in range(5)]
    assert codes[:3] == [201, 201, 201] and codes[3:] == [429, 429]
