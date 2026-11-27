"""Troisième série d'améliorations (28/11/2026) : photo jointe à une demande, alerte de baisse de prix, rappels des
constructeurs, récapitulatif de la semaine des magasins, mécaniciens, carnet transmis à la revente."""
from datetime import datetime, timezone

from sqlalchemy import select

from app.models import PartCategory, PartRequest, Shop, ShopCategory, User

from .conftest import login
from .test_catalogue_rapide import jpeg

API = "/api/v1"


def _cat(db, slug="plaquettes-avant"):
    return db.scalar(select(PartCategory).where(PartCategory.slug == slug))


def _owned_shop(db, phone_user: User, name: str, category_id: int) -> Shop:
    s = Shop(name=name, status="verified", source="declared", owner_user_id=phone_user.id,
             verified_at=datetime.now(timezone.utc))
    db.add(s)
    db.flush()
    db.add(ShopCategory(shop_id=s.id, category_id=category_id, source="declared"))
    db.commit()
    return s


def _user(db, phone: str) -> User:
    return db.scalar(select(User).where(User.phone == "+213" + phone[1:]))


# --- 1. Photo jointe à une demande -----------------------------------------------------------------------------------

def test_photo_de_demande_envoyee_par_jeton_vue_par_le_magasin(client, db):
    hm = login(client, "0698000001")
    owner = _user(db, "0698000001")
    owner.role = "shop_owner"
    fam = db.scalar(select(PartCategory).where(PartCategory.slug == "freinage"))
    shop = _owned_shop(db, owner, "Magasin photo", fam.id)
    req = client.post(f"{API}/part-requests", json={"category_id": _cat(db).id}).json()   # sans compte
    files = {"file": ("piece.jpg", jpeg(), "image/jpeg")}
    assert client.post(f"{API}/part-requests/{req['id']}/photo", files=files).status_code == 404            # sans jeton
    assert client.post(f"{API}/part-requests/{req['id']}/photo", params={"token": "faux"}, files=files).status_code == 404
    r = client.post(f"{API}/part-requests/{req['id']}/photo", params={"token": req["token"]}, files=files)
    assert r.status_code == 200 and r.json()["photo_url"].startswith("/api/v1/media/demandes/")
    url = r.json()["photo_url"]
    photo = client.get(url)
    assert photo.status_code == 200 and b"GPS" not in photo.content and b"Exif" not in photo.content   # métadonnées retirées
    inbox = [x for x in client.get(f"{API}/part-requests/inbox", headers=hm).json() if x["request_id"] == req["id"]]
    assert inbox and inbox[0]["shop_id"] == shop.id and inbox[0]["photo_url"] == url
    assert client.get(f"{API}/part-requests/{req['id']}", params={"token": req["token"]}).json()["photo_url"] == url
    # Pas une image : refusée ; retrait par le client
    bad = {"file": ("x.jpg", b"pas une image", "image/jpeg")}
    assert client.post(f"{API}/part-requests/{req['id']}/photo", params={"token": req["token"]}, files=bad).status_code == 422
    assert client.delete(f"{API}/part-requests/{req['id']}/photo", params={"token": req["token"]}).status_code == 204
    assert client.get(url).status_code == 404


def test_photo_effacee_avec_le_compte(client, db):
    h = login(client, "0698000002")
    req = client.post(f"{API}/part-requests", headers=h, json={"category_id": _cat(db).id}).json()
    url = client.post(f"{API}/part-requests/{req['id']}/photo", headers=h,
                      files={"file": ("p.jpg", jpeg(), "image/jpeg")}).json()["photo_url"]
    assert client.delete(f"{API}/auth/me", headers=h).status_code == 204
    assert client.get(url).status_code == 404
    db.expire_all()
    assert db.get(PartRequest, req["id"]).photo_url is None


# --- 2. Alerte de baisse de prix ---------------------------------------------------------------------------------------

def test_prix_suivi_baisse_puis_vu(client, db):
    from app.models import Product
    from .test_avis_prix import _free_category, _shop
    h = login(client, "0698000010")
    cat = _free_category(db)
    shop = _shop(db, "Prix suivi A")
    p = Product(shop_id=shop.id, category_id=cat.id, title="Pièce suivie", price=5000)
    db.add(p)
    db.commit()
    w = client.post(f"{API}/me/price-watches", headers=h, json={"category_id": cat.id}).json()
    assert w["reference_price"] == 5000 and w["alert"] is None and w["lowest"]["shop"]["name"] == "Prix suivi A"
    assert client.post(f"{API}/me/price-watches", headers=h, json={"category_id": cat.id}).json()["id"] == w["id"]   # pas de doublon
    p.price = 4000
    db.commit()
    w2 = client.get(f"{API}/me/price-watches", headers=h).json()[0]
    assert w2["alert"] == "drop" and w2["drop_pct"] == 20 and w2["lowest"]["price"] == 4000
    assert client.get(f"{API}/me/alerts", headers=h).json()["prices"] == 1
    seen = client.post(f"{API}/me/price-watches/{w['id']}/seen", headers=h).json()
    assert seen["reference_price"] == 4000 and seen["alert"] is None
    assert client.get(f"{API}/me/alerts", headers=h).json()["prices"] == 0
    p.price = 4500          # une hausse ne déclenche rien
    db.commit()
    assert client.get(f"{API}/me/price-watches", headers=h).json()[0]["alert"] is None
    assert client.delete(f"{API}/me/price-watches/{w['id']}", headers=h).status_code == 204
    assert client.get(f"{API}/me/price-watches", headers=h).json() == []


def test_prix_suivi_piece_sans_prix_puis_disponible(client, db):
    from app.models import Product
    from .test_avis_prix import _free_category, _shop
    h = login(client, "0698000011")
    cat = _free_category(db)
    w = client.post(f"{API}/me/price-watches", headers=h, json={"category_id": cat.id}).json()
    assert w["reference_price"] is None and w["lowest"] is None and w["alert"] is None
    shop = _shop(db, "Prix suivi B")
    db.add(Product(shop_id=shop.id, category_id=cat.id, title="Enfin là", price=3000))
    db.commit()
    assert client.get(f"{API}/me/price-watches", headers=h).json()[0]["alert"] == "available"


def test_prix_suivi_refus_et_suivi_d_un_autre(client, db):
    h = login(client, "0698000012")
    assert client.post(f"{API}/me/price-watches", headers=h, json={"category_id": 999999}).status_code == 404
    w = client.post(f"{API}/me/price-watches", headers=h, json={"category_id": _cat(db).id}).json()
    h2 = login(client, "0698000013")
    assert client.delete(f"{API}/me/price-watches/{w['id']}", headers=h2).status_code == 404
    assert client.post(f"{API}/me/price-watches/{w['id']}/seen", headers=h2).status_code == 404
    assert client.get(f"{API}/me/price-watches").status_code == 401
