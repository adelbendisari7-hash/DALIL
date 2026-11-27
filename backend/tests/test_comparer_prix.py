"""Comparer les prix d'une pièce : chaque magasin du classement porte sa meilleure offre (prix du catalogue,
compatible avec le véhicule d'abord), jamais un prix estimé."""
from datetime import datetime, timezone

from sqlalchemy import select

from app.models import PartCategory, Product, ProductFitment, Shop, VehicleVariant

API = "/api/v1"


def _cat(db, slug):
    return db.scalar(select(PartCategory).where(PartCategory.slug == slug)).id


def _shop(db, name, fam):
    s = Shop(name=name, phone=None, lat=35.70, lng=-0.63, status="verified", source="terrain",
             verified_at=datetime.now(timezone.utc))
    db.add(s)
    db.flush()
    from app.models import ShopCategory
    db.add(ShopCategory(shop_id=s.id, category_id=fam, source="terrain", confirmed_at=datetime.now(timezone.utc)))
    return s


def test_meilleure_offre_compatible_d_abord(client, db):
    fam, plaq = _cat(db, "freinage"), _cat(db, "plaquettes-avant")
    variant = db.scalar(select(VehicleVariant).order_by(VehicleVariant.id))
    a, b, c = _shop(db, "Prix A", fam), _shop(db, "Prix B", fam), _shop(db, "Prix C", fam)
    # A : un produit compatible à 5 000 et un générique moins cher à 3 000 -> l'offre est le compatible
    pa = Product(shop_id=a.id, category_id=plaq, title="Plaquettes A", price=5000, in_stock=True)
    db.add_all([pa, Product(shop_id=a.id, category_id=plaq, title="Générique A", price=3000, in_stock=True)])
    # B : seulement un produit de la famille, sans compatibilité connue ; C : un produit en rupture
    db.add(Product(shop_id=b.id, category_id=plaq, title="Plaquettes B", price=4200, in_stock=True))
    db.add(Product(shop_id=c.id, category_id=plaq, title="Plaquettes C", price=100, in_stock=False))
    db.flush()
    db.add(ProductFitment(product_id=pa.id, variant_id=variant.id))
    db.commit()
    rec = {x["id"]: x for x in client.get(f"{API}/shops/recommend", params={"category_id": plaq, "variant_id": variant.id}).json()}
    assert rec[a.id]["offer"]["price"] == 5000 and rec[a.id]["offer"]["compatible"] is True
    assert rec[b.id]["offer"]["price"] == 4200 and rec[b.id]["offer"]["compatible"] is False
    assert rec[c.id]["offer"] is None          # rupture de stock : pas d'offre (prix jamais inventé)
    # Sans véhicule : le moins cher de la famille, compatibilité non évaluée
    rec = {x["id"]: x for x in client.get(f"{API}/shops/recommend", params={"category_id": plaq}).json()}
    assert rec[a.id]["offer"]["price"] == 3000 and rec[a.id]["offer"]["compatible"] is None
    assert rec[a.id]["offer"]["confirmed_days"] == 0
