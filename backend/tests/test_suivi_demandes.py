"""« Mes demandes » : le client voit les réponses des magasins à sa demande (disponible, prix), avec ou sans compte."""
from datetime import datetime, timezone

from sqlalchemy import select

from app.models import PartCategory, Shop, ShopCategory

from .conftest import login

API = "/api/v1"


def _shops(client, db, n_shops, tag):
    """Magasins validés, gérés, qui vendent la famille « freinage » : ils reçoivent la demande."""
    fam = db.scalar(select(PartCategory).where(PartCategory.slug == "freinage")).id
    out = []
    for i in range(n_shops):
        h = login(client, f"0694{tag}{i:05d}")
        client.patch(f"{API}/auth/me", headers=h, json={"role": "shop_owner"})
        sid = client.post(f"{API}/shops", headers=h, json={"name": f"Demandes {tag}{i}", "lat": 35.7, "lng": -0.63,
                                                           "category_ids": [fam]}).json()["id"]
        shop = db.get(Shop, sid)
        shop.status, shop.verified_at = "claimed", datetime.now(timezone.utc)
        db.commit()
        out.append((h, sid))
    return out


def _plaquettes(db):
    return db.scalar(select(PartCategory).where(PartCategory.slug == "plaquettes-avant")).id


def test_client_connecte_voit_les_reponses_triees(client, db):
    shops = _shops(client, db, 3, "1")
    me = login(client, "0694099001")
    req = client.post(f"{API}/part-requests", headers=me, json={"category_id": _plaquettes(db)}).json()
    assert req["token"] and req["notified_shops"] >= 3
    (h1, s1), (h2, s2), (h3, s3) = shops
    client.post(f"{API}/part-requests/{req['id']}/responses?shop_id={s1}", headers=h1, json={"available": True, "price": 5200})
    client.post(f"{API}/part-requests/{req['id']}/responses?shop_id={s2}", headers=h2, json={"available": False})
    client.post(f"{API}/part-requests/{req['id']}/responses?shop_id={s3}", headers=h3, json={"available": True, "price": 4300})
    mine = client.get(f"{API}/me/part-requests", headers=me).json()[0]
    assert mine["part"] == "Plaquettes de frein avant" and mine["answered"] == 3 and mine["unseen"] == 3
    # Disponibles d'abord, du moins cher au plus cher ; puis « pas en stock »
    assert [(r["shop"]["id"], r["available"]) for r in mine["responses"]] == [(s3, True), (s1, True), (s2, False)]
    assert mine["responses"][0]["shop"]["phone"]   # de quoi appeler le magasin
    assert client.get(f"{API}/me/part-requests/unseen", headers=me).json()["unseen"] == 3
    assert client.post(f"{API}/part-requests/{req['id']}/seen", headers=me).status_code == 204
    assert client.get(f"{API}/me/part-requests/unseen", headers=me).json()["unseen"] == 0


def test_sans_compte_avec_le_jeton_seulement(client, db):
    (h, sid), = _shops(client, db, 1, "2")
    req = client.post(f"{API}/part-requests", json={"category_id": _plaquettes(db)}).json()
    client.post(f"{API}/part-requests/{req['id']}/responses?shop_id={sid}", headers=h, json={"available": True, "price": 3900})
    ok = client.get(f"{API}/part-requests/{req['id']}", params={"token": req["token"]})
    assert ok.status_code == 200 and ok.json()["responses"][0]["price"] == 3900
    # Sans jeton, avec un faux jeton, ou par un autre compte : introuvable (les identifiants se suivent)
    assert client.get(f"{API}/part-requests/{req['id']}").status_code == 404
    assert client.get(f"{API}/part-requests/{req['id']}", params={"token": "faux"}).status_code == 404
    other = login(client, "0694099002")
    assert client.get(f"{API}/part-requests/{req['id']}", headers=other).status_code == 404
    assert client.post(f"{API}/part-requests/{req['id']}/seen", params={"token": req["token"]}).status_code == 204
    assert client.get(f"{API}/me/part-requests", headers=other).json() == []
