"""Plan côté magasin, phase 2 : catalogue plus rapide (modification en un toucher, aperçu de l'import, 500 lignes),
photos des produits et de la devanture (JPEG seulement, sans métadonnées ni position GPS)."""
import io
import struct

import pytest
from sqlalchemy import select

from app.models import Product, Shop
from app.services.media import InvalidImage, clean_jpeg

from .conftest import login

API = "/api/v1"


def jpeg(width=16, height=16, gps=True, size_padding=0) -> bytes:
    """JPEG synthétique avec, comme une vraie photo de téléphone, un EXIF qui contient une position GPS."""
    seg = lambda marker, payload: b"\xff" + bytes([marker]) + struct.pack(">H", len(payload) + 2) + payload
    out = b"\xff\xd8"
    out += seg(0xE0, b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
    if gps:
        out += seg(0xE1, b"Exif\x00\x00GPSLatitude=35.6971;GPSLongitude=-0.6308;Model=Phone")
        out += seg(0xFE, b"commentaire du telephone")
    out += seg(0xDB, bytes([0]) + bytes(range(64)))
    out += seg(0xC0, b"\x08" + struct.pack(">HH", height, width) + b"\x01\x01\x11\x00")
    out += seg(0xDA, b"\x01\x01\x00\x00\x3f\x00")
    out += b"\x12\x34\x56" * (10 + size_padding) + b"\xff\xd9"
    return out


def _shop(client, db, phone):
    h = login(client, phone)
    client.patch(f"{API}/auth/me", headers=h, json={"role": "shop_owner"})
    sid = client.post(f"{API}/shops", headers=h, json={"name": f"Magasin {phone}", "lat": 35.70, "lng": -0.63}).json()["id"]
    return h, sid


def _product(client, h, sid, db):
    from app.models import PartCategory
    cat = db.scalar(select(PartCategory).where(PartCategory.slug == "plaquettes-avant")).id
    return client.post(f"{API}/shops/{sid}/products", headers=h, json={"title": "Plaquettes avant", "category_id": cat,
                                                                        "price": 4500}).json()["id"]


# --- Nettoyage des photos -------------------------------------------------------------------------------------

def test_photo_sans_metadonnees_ni_position_gps():
    raw = jpeg()
    assert b"GPSLatitude" in raw
    clean = clean_jpeg(raw)
    assert b"GPS" not in clean and b"Model" not in clean and b"commentaire" not in clean
    assert clean.startswith(b"\xff\xd8\xff\xe0") and clean.endswith(b"\xff\xd9")   # JFIF gardé, image intacte
    assert clean_jpeg(clean) == clean


@pytest.mark.parametrize("bad, why", [
    (b"\x89PNG\r\n\x1a\n" + b"0" * 100, "JPEG"),
    (jpeg(width=9000), "trop grande"),
    (jpeg()[:40], "abîmée"),
    (jpeg(size_padding=400_000), "trop lourde"),
])
def test_photo_refusee(bad, why):
    with pytest.raises(InvalidImage, match=why):
        clean_jpeg(bad)


def test_photo_du_produit_envoyee_servie_remplacee_supprimee(client, db, tmp_path):
    h, sid = _shop(client, db, "0681000001")
    pid = _product(client, h, sid, db)
    r = client.post(f"{API}/shops/{sid}/products/{pid}/photo", headers=h,
                    files={"file": ("photo.jpg", jpeg(), "image/jpeg")})
    assert r.status_code == 200, r.text
    url = r.json()["photo_url"]
    assert url.startswith("/api/v1/media/produits/") and url.endswith(".jpg")
    served = client.get(url)
    assert served.status_code == 200 and served.headers["content-type"] == "image/jpeg"
    assert b"GPS" not in served.content and "immutable" in served.headers["cache-control"]
    # Une autre photo remplace la première, dont le fichier disparaît
    url2 = client.post(f"{API}/shops/{sid}/products/{pid}/photo", headers=h,
                       files={"file": ("autre.jpg", jpeg(), "image/jpeg")}).json()["photo_url"]
    assert url2 != url and client.get(url).status_code == 404 and client.get(url2).status_code == 200
    # Un faux JPEG est refusé ; un autre magasin ne peut pas changer la photo
    fake = client.post(f"{API}/shops/{sid}/products/{pid}/photo", headers=h, files={"file": ("x.jpg", b"<svg/>", "image/jpeg")})
    assert fake.status_code == 422
    other, _ = _shop(client, db, "0681000002")
    assert client.post(f"{API}/shops/{sid}/products/{pid}/photo", headers=other,
                       files={"file": ("p.jpg", jpeg(), "image/jpeg")}).status_code == 403
    # Produit retiré : sa photo aussi
    assert client.delete(f"{API}/shops/{sid}/products/{pid}", headers=h).status_code == 204
    assert client.get(url2).status_code == 404


def test_photo_de_la_devanture(client, db):
    h, sid = _shop(client, db, "0681000003")
    url = client.post(f"{API}/shops/{sid}/photo", headers=h, files={"file": ("d.jpg", jpeg(), "image/jpeg")}).json()["photo_url"]
    assert url.startswith("/api/v1/media/devantures/")
    assert client.get(f"{API}/shops/mine", headers=h).json()[0]["photo_url"] == url
    assert client.delete(f"{API}/shops/{sid}/photo", headers=h).status_code == 204
    assert client.get(url).status_code == 404
    for bad in ["../../secret.jpg", "abc.jpg", "0" * 32 + ".png"]:
        assert client.get(f"{API}/media/produits/{bad}").status_code == 404
    assert client.get(f"{API}/media/autre/{'0' * 32}.jpg").status_code == 404


# --- Catalogue --------------------------------------------------------------------------------------------------

def test_prix_et_stock_en_un_toucher(client, db):
    h, sid = _shop(client, db, "0681000004")
    pid = _product(client, h, sid, db)
    first = client.get(f"{API}/shops/{sid}/products", headers=h).json()[0]["price_confirmed_at"]
    r = client.patch(f"{API}/shops/{sid}/products/{pid}", headers=h, json={"in_stock": False})
    assert r.json()["in_stock"] is False and r.json()["price"] == 4500 and r.json()["price_confirmed_at"] >= first
    r = client.patch(f"{API}/shops/{sid}/products/{pid}", headers=h, json={"price": 4800})
    assert r.json()["price"] == 4800
    assert client.patch(f"{API}/shops/{sid}/products/{pid}", headers=h, json={"confirm": True}).status_code == 200
    assert client.patch(f"{API}/shops/{sid}/products/{pid}", headers=h, json={"price": -1}).status_code == 422
    other, _ = _shop(client, db, "0681000005")
    assert client.patch(f"{API}/shops/{sid}/products/{pid}", headers=other, json={"price": 1}).status_code == 403


def _csv(n: int, bad_line: int | None = None) -> bytes:
    lines = ["titre;famille;reference;etat;prix;compatibilite"]
    for i in range(n):
        fam = "famille inconnue" if i == bad_line else "plaquettes avant"
        lines.append(f"Plaquettes avant {i};{fam};FICTIF-IMP-{i:04d};adaptable;{1000 + i};Dacia Logan 1.5 dCi 2015")
    return "\n".join(lines).encode()


def test_apercu_de_l_import_n_enregistre_rien(client, db):
    h, sid = _shop(client, db, "0681000006")
    r = client.post(f"{API}/shops/{sid}/products/import?dry_run=true", headers=h,
                    files={"file": ("cat.csv", _csv(5, bad_line=2), "text/csv")}).json()
    assert r["dry_run"] is True and r["created"] == 4 and r["errors"][0]["line"] == 4
    assert client.get(f"{API}/shops/{sid}/products", headers=h).json() == []   # rien d'enregistré
    r = client.post(f"{API}/shops/{sid}/products/import", headers=h, files={"file": ("cat.csv", _csv(5, bad_line=2), "text/csv")}).json()
    assert r["created"] == 4 and len(client.get(f"{API}/shops/{sid}/products", headers=h).json()) == 4


def test_import_de_500_lignes_sans_erreur(client, db):
    """Objectif du cahier des charges (F12) : import de 500 lignes sans erreur ; réimport = mises à jour."""
    h, sid = _shop(client, db, "0681000007")
    r = client.post(f"{API}/shops/{sid}/products/import", headers=h, files={"file": ("cat.csv", _csv(500), "text/csv")}).json()
    assert (r["created"], r["updated"], r["errors"]) == (500, 0, [])
    r = client.post(f"{API}/shops/{sid}/products/import", headers=h, files={"file": ("cat.csv", _csv(500), "text/csv")}).json()
    assert (r["created"], r["updated"]) == (0, 500)
    assert len(list(db.scalars(select(Product).where(Product.shop_id == sid)))) == 500
