"""Avis vérifiés « pièce trouvée » sur la fiche d'un magasin, historique des prix d'une pièce, rappel d'entretien
(deuxième série d'améliorations, 28/11/2026)."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.models import (ContactEvent, DiagnosisSession, Feedback, PartCategory, PricePoint, Product, Shop,
                        VehicleVariant)
from app.services import price_history

from .conftest import login

API = "/api/v1"


def _shop(db, name, demo=False):
    s = Shop(name=name, phone=None, lat=35.70, lng=-0.63, status="verified", source="terrain", is_demo=demo,
             verified_at=datetime.now(timezone.utc))
    db.add(s)
    db.commit()
    return s


def _free_category(db):
    """Une pièce sans aucun prix enregistré par les autres tests (la base est partagée)."""
    used = set(db.scalars(select(PricePoint.category_id)))
    leaves = [c for c in db.scalars(select(PartCategory).where(PartCategory.parent_id.is_not(None)).order_by(PartCategory.id))]
    return next(c for c in leaves if c.id not in used and not any(x.parent_id == c.id for x in leaves))


# --- Avis vérifiés ---------------------------------------------------------

def test_avis_verifie_seulement_apres_un_contact(client, db):
    shop = _shop(db, "Avis A")
    cat = db.scalar(select(PartCategory).where(PartCategory.slug == "plaquettes-avant"))
    # « Pièce trouvée » sans avoir contacté le magasin : compté nulle part sur la fiche
    client.post(f"{API}/feedback", json={"shop_id": shop.id, "category_id": cat.id, "part_found": True})
    rev = client.get(f"{API}/shops/{shop.id}").json()["reviews"]
    assert rev["found"] == 0 and rev["recent"] == []
    # Appel depuis DALIL (même client), puis « pièce trouvée » : avis vérifié
    assert client.post(f"{API}/contact-events", json={"shop_id": shop.id, "channel": "call", "category_id": cat.id}).status_code == 201
    assert db.scalar(select(ContactEvent).where(ContactEvent.shop_id == shop.id)).client_hash
    client.post(f"{API}/feedback", json={"shop_id": shop.id, "category_id": cat.id, "part_found": True})
    client.post(f"{API}/feedback", json={"shop_id": shop.id, "category_id": cat.id, "part_found": True})   # répété
    rev = client.get(f"{API}/shops/{shop.id}").json()["reviews"]
    assert rev["found"] == 1 and rev["not_found"] == 0            # un avis par client et par jour
    assert rev["recent"][0]["part"] == cat.name_fr and rev["recent"][0]["date"]
    assert set(rev["recent"][0]) == {"part", "vehicle", "date"}   # rien de personnel, jamais le commentaire


def test_avis_contact_trop_ancien_ou_autre_client(db):
    from app.services.shop_reviews import reviews
    shop = _shop(db, "Avis B")
    now = datetime.now(timezone.utc)
    db.add(ContactEvent(shop_id=shop.id, channel="call", client_hash="aaaa", created_at=now - timedelta(days=45)))
    db.add(ContactEvent(shop_id=shop.id, channel="call", client_hash="bbbb", created_at=now - timedelta(days=2)))
    db.add(Feedback(shop_id=shop.id, part_found=True, client_hash="aaaa", created_at=now))   # contact de 45 jours
    db.add(Feedback(shop_id=shop.id, part_found=True, client_hash="cccc", created_at=now))   # n'a jamais appelé
    db.add(Feedback(shop_id=shop.id, part_found=False, client_hash="bbbb", created_at=now))  # vérifié, pas trouvée
    db.commit()
    rev = reviews(db, shop.id)
    assert rev["found"] == 0 and rev["not_found"] == 1


def test_avis_ancien_contact_sans_empreinte_par_le_diagnostic(db):
    """Contacts d'avant la migration 0012 (sans empreinte) : le même diagnostic vaut preuve ; la voiture est montrée."""
    from app.services.shop_reviews import reviews
    shop = _shop(db, "Avis C")
    v = db.scalar(select(VehicleVariant).order_by(VehicleVariant.id))
    sess = DiagnosisSession(input_text="ça grince", variant_id=v.id, model_version="test")
    db.add(sess)
    db.flush()
    now = datetime.now(timezone.utc)
    db.add(ContactEvent(shop_id=shop.id, channel="whatsapp", session_id=sess.id, created_at=now - timedelta(hours=1)))
    db.add(Feedback(shop_id=shop.id, session_id=sess.id, part_found=True, client_hash="dddd", created_at=now))
    db.commit()
    rev = reviews(db, shop.id)
    assert rev["found"] == 1 and rev["recent"][0]["vehicle"] == f"{v.model.brand.name} {v.model.name}"


# --- Historique des prix ---------------------------------------------------

def test_points_ecrits_a_chaque_changement(client, db):
    shop = _shop(db, "Prix H1")
    cat = _free_category(db)
    p = Product(shop_id=shop.id, category_id=cat.id, title="Pièce H1", price=4000)
    db.add(p)
    db.commit()
    p.price = 4500
    db.commit()
    p.in_stock = False          # le stock seul ne fait pas de point
    db.commit()
    db.delete(p)
    db.commit()
    pts = list(db.scalars(select(PricePoint).where(PricePoint.product_id == p.id).order_by(PricePoint.id)))
    assert [x.price for x in pts] == [4000, 4500, None]
    assert all(x.shop_id == shop.id and x.category_id == cat.id for x in pts)


def test_point_ecrit_par_le_prix_en_un_toucher(client, db):
    h = login(client, "0696000001")
    from app.models import User
    user = db.scalar(select(User).where(User.phone == "+213696000001"))
    user.role = "shop_owner"
    shop = _shop(db, "Prix H2")
    shop.owner_user_id = user.id
    cat = _free_category(db)
    p = Product(shop_id=shop.id, category_id=cat.id, title="Pièce H2", price=1000)
    db.add(p)
    db.commit()
    r = client.patch(f"{API}/shops/{shop.id}/products/{p.id}", headers=h, json={"price": 1200})
    assert r.status_code == 200, r.text
    # (SQLite peut redonner le numéro d'un produit supprimé : on filtre aussi par magasin)
    prices = list(db.scalars(select(PricePoint.price).where(PricePoint.product_id == p.id, PricePoint.shop_id == shop.id)
                             .order_by(PricePoint.id)))
    assert prices == [1000, 1200]


def test_resume_mois_par_mois(client, db):
    cat = _free_category(db)
    a, b, c = _shop(db, "Prix R1"), _shop(db, "Prix R2"), _shop(db, "Prix R3")
    now = datetime(2026, 11, 20, tzinfo=timezone.utc)
    ago = lambda days: now - timedelta(days=days)   # noqa: E731
    db.add_all([
        # il y a 4 mois : A à 3 000, B à 5 000 (médiane 4 000)
        PricePoint(product_id=90001, shop_id=a.id, category_id=cat.id, condition="neuf", price=3000, recorded_at=ago(125)),
        PricePoint(product_id=90002, shop_id=b.id, category_id=cat.id, condition="neuf", price=5000, recorded_at=ago(125)),
        # A augmente à 4 000, C arrive en occasion à 2 000, B retire son produit
        PricePoint(product_id=90001, shop_id=a.id, category_id=cat.id, condition="neuf", price=4000, recorded_at=ago(20)),
        PricePoint(product_id=90003, shop_id=c.id, category_id=cat.id, condition="occasion", price=2000, recorded_at=ago(15)),
        PricePoint(product_id=90002, shop_id=b.id, category_id=cat.id, condition="neuf", price=None, recorded_at=ago(10)),
    ])
    db.commit()
    s = price_history.summary(db, cat.id, now=now)
    assert [m["month"] for m in s["months"]] == ["2026-06", "2026-07", "2026-08", "2026-09", "2026-10", "2026-11"]
    jul = s["months"][1]
    assert jul["min"] == 3000 and jul["max"] == 5000 and jul["median"] == 4000 and jul["shops"] == 2
    nov = s["now"]
    assert (nov["min"], nov["max"], nov["shops"]) == (2000, 4000, 2) and nov["median"] == 3000
    assert s["trend_pct"] == -25 and s["since"] == "2026-07" and s["demo"] is False
    assert s["by_condition"]["neuf"]["min"] == 4000 and s["by_condition"]["occasion"]["min"] == 2000
    # Filtre par état : neuf seulement -> un seul magasin, pas de médiane
    neuf = price_history.summary(db, cat.id, condition="neuf", now=now)["now"]
    assert neuf["min"] == 4000 and neuf["median"] is None


def test_prix_fictifs_seulement_sans_vrai_magasin(client, db):
    cat = _free_category(db)
    d1, d2 = _shop(db, "[DÉMO] Prix D1", demo=True), _shop(db, "[DÉMO] Prix D2", demo=True)
    db.add_all([Product(shop_id=d1.id, category_id=cat.id, title="[DÉMO] x", price=100),
                Product(shop_id=d2.id, category_id=cat.id, title="[DÉMO] y", price=300)])
    db.commit()
    r = client.get(f"{API}/prices/{cat.id}").json()
    assert r["demo"] is True and r["now"]["median"] == 200
    real = _shop(db, "Prix vrai")
    db.add(Product(shop_id=real.id, category_id=cat.id, title="vrai", price=5000))
    db.commit()
    r = client.get(f"{API}/prices/{cat.id}").json()
    assert r["demo"] is False and r["now"]["min"] == 5000 and r["now"]["median"] is None   # les fictifs écartés
    assert client.get(f"{API}/prices/999999").status_code == 404
    assert client.get(f"{API}/prices/{cat.id}", params={"condition": "cassé"}).status_code == 422


def test_magasin_non_valide_ne_compte_pas(client, db):
    cat = _free_category(db)
    draft = Shop(name="Brouillon prix", status="draft", source="osm")
    db.add(draft)
    db.commit()
    db.add(Product(shop_id=draft.id, category_id=cat.id, title="z", price=999))
    db.commit()
    assert client.get(f"{API}/prices/{cat.id}").json()["now"]["products"] == 0


# --- Rappel d'entretien ----------------------------------------------------

def test_entretiens_a_faire_dans_la_liste_des_voitures(client, db):
    h = login(client, "0696000002")
    vid = db.scalar(select(VehicleVariant).order_by(VehicleVariant.id)).id
    cid = client.post(f"{API}/me/vehicles", headers=h, json={"plate": "30001-115-31", "variant_id": vid, "mileage_km": 30000}).json()["id"]
    client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=h, json={"item": "vidange", "km": 19000})
    car = next(c for c in client.get(f"{API}/me/vehicles", headers=h).json() if c["id"] == cid)
    vid_item = next(x for x in car["maintenance_items"] if x["item"] == "vidange")
    assert vid_item["status"] == "due" and vid_item["km_left"] == -1000 and vid_item["name"]
    assert car["maintenance_due"] == len(car["maintenance_items"])
