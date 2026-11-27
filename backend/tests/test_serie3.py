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
