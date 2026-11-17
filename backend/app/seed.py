"""Chargement rejouable des référentiels (étape 3) et des données de démonstration.

    python -m app.seed               # référentiels + démo
    python -m app.seed --no-demo     # référentiels seulement
    python -m app.seed --purge-demo  # supprime les magasins fictifs
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import (
    Brand,
    Commune,
    DtcCode,
    DtcPart,
    Fault,
    FaultPart,
    KnowledgeChunk,
    Model,
    PartCategory,
    PartReference,
    Product,
    ProductFitment,
    Shop,
    ShopBrand,
    ShopCategory,
    VehicleVariant,
    Wilaya,
)

SEED = Path(get_settings().data_dir) / "seed"


def _load(name: str) -> dict:
    return json.loads((SEED / name).read_text(encoding="utf-8"))


def seed_geo(db: Session) -> None:
    data = _load("geo_oran.json")
    for w in data["wilayas"]:
        obj = db.get(Wilaya, w["code"]) or Wilaya(code=w["code"])
        obj.nom_fr, obj.nom_ar, obj.active = w["nom_fr"], w["nom_ar"], w.get("active", False)
        db.add(obj)
    db.flush()
    for c in data["communes"]:
        obj = db.scalar(select(Commune).where(Commune.code == c["code"])) or Commune(code=c["code"])
        obj.wilaya_code = c["code"][:2]
        obj.nom_fr, obj.nom_ar, obj.lat, obj.lng = c["nom_fr"], c["nom_ar"], c["lat"], c["lng"]
        db.add(obj)


def seed_vehicles(db: Session) -> None:
    for b in _load("vehicles.json")["brands"]:
        brand = db.scalar(select(Brand).where(Brand.name == b["name"])) or Brand(name=b["name"])
        brand.country, brand.priority = b.get("country"), b.get("priority", 0)
        db.add(brand)
        db.flush()
        for m in b["models"]:
            model = db.scalar(select(Model).where(Model.brand_id == brand.id, Model.name == m["name"]))
            if model is None:
                model = Model(brand_id=brand.id, name=m["name"])
            model.pilot = m.get("pilot", False)
            db.add(model)
            db.flush()
            for v in m["variants"]:
                exists = db.scalar(select(VehicleVariant).where(
                    VehicleVariant.model_id == model.id,
                    VehicleVariant.engine == v["engine"],
                    VehicleVariant.year_from == v["year_from"],
                ))
                if exists is None:
                    db.add(VehicleVariant(model_id=model.id, **v))
                else:
                    exists.year_to, exists.fuel = v["year_to"], v["fuel"]


def seed_categories(db: Session) -> dict[str, int]:
    for fam in _load("part_categories.json")["families"]:
        parent = db.scalar(select(PartCategory).where(PartCategory.slug == fam["slug"])) or PartCategory(slug=fam["slug"])
        parent.name_fr, parent.name_ar, parent.synonyms, parent.parent_id = fam["name_fr"], fam.get("name_ar"), fam.get("synonyms", []), None
        db.add(parent)
        db.flush()
        for ch in fam["children"]:
            c = db.scalar(select(PartCategory).where(PartCategory.slug == ch["slug"])) or PartCategory(slug=ch["slug"])
            c.name_fr, c.name_ar, c.synonyms = ch["name_fr"], ch.get("name_ar"), ch.get("synonyms", [])
            c.parent_id, c.pilot = parent.id, ch.get("pilot", False)
            db.add(c)
    db.flush()
    return {c.slug: c.id for c in db.scalars(select(PartCategory))}


def seed_faults(db: Session, cats: dict[str, int]) -> None:
    for f in _load("faults.json")["faults"]:
        fault = db.scalar(select(Fault).where(Fault.slug == f["slug"])) or Fault(slug=f["slug"])
        fault.name_fr, fault.system, fault.severity, fault.description = f["name_fr"], f["system"], f["severity"], f["description"]
        fault.do_not_drive, fault.fuel = f.get("do_not_drive", False), f.get("fuel")
        db.add(fault)
        db.flush()
        db.execute(delete(FaultPart).where(FaultPart.fault_id == fault.id))
        for slug, w in f["parts"].items():
            db.add(FaultPart(fault_id=fault.id, category_id=cats[slug], weight=w))


def seed_dtc(db: Session, cats: dict[str, int]) -> None:
    for d in _load("dtc_fr.json")["codes"]:
        obj = db.get(DtcCode, d["code"]) or DtcCode(code=d["code"])
        obj.title_fr, obj.title_en = d["title_fr"], d.get("title_en")
        obj.causes, obj.symptoms = d.get("causes", []), d.get("symptoms", [])
        obj.description = d.get("description")
        if obj.source != "obdex":
            obj.source = "dalil-seed"
        db.add(obj)
        db.flush()
        db.execute(delete(DtcPart).where(DtcPart.code == obj.code))
        for slug, w in d.get("parts", {}).items():
            db.add(DtcPart(code=obj.code, category_id=cats[slug], weight=w))


def seed_knowledge(db: Session) -> None:
    """Base de connaissances amorcée avec les fiches DALIL (pannes, codes).

    Mise à jour en place (clé : source + panne ou code) : les identifiants des passages ne changent pas d'un
    chargement à l'autre, et les vecteurs de la recherche hybride, rangés par identifiant, restent valables."""
    wanted: dict[tuple[str, str], tuple[str, dict]] = {}
    for f in _load("faults.json")["faults"]:
        wanted[("dalil-fiches", f["slug"])] = (f"{f['name_fr']}. {f['description']}", {"fault": f["slug"]})
    for d in _load("dtc_fr.json")["codes"]:
        text = f"Code {d['code']} : {d['title_fr']}. Causes : {'; '.join(d['causes'])}. Symptômes : {'; '.join(d['symptoms'])}."
        wanted[("dalil-dtc", d["code"])] = (text, {"dtc": d["code"]})
    for row in db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.source.in_(["dalil-fiches", "dalil-dtc"]))):
        key = (row.source, (row.meta or {}).get("fault") or (row.meta or {}).get("dtc"))
        if key in wanted:
            text, meta = wanted.pop(key)
            if row.text != text:
                row.text, row.embedding = text, None
            row.meta = meta
        else:
            db.delete(row)  # fiche retirée du référentiel (ou doublon)
    for (source, _), (text, meta) in wanted.items():
        db.add(KnowledgeChunk(source=source, lang="fr", license="propriétaire DALIL", text=text, meta=meta))


def _variant(db: Session, brand: str, model: str, engine: str, year: int) -> VehicleVariant | None:
    return db.scalar(
        select(VehicleVariant).join(Model).join(Brand)
        .where(Brand.name == brand, Model.name == model, VehicleVariant.engine == engine, VehicleVariant.year_from <= year)
        .where((VehicleVariant.year_to.is_(None)) | (VehicleVariant.year_to >= year))
    )


def seed_demo(db: Session, cats: dict[str, int]) -> None:
    now = datetime.now(timezone.utc)
    brands = {b.name: b.id for b in db.scalars(select(Brand))}
    communes = {c.code: c.id for c in db.scalars(select(Commune))}
    for i, s in enumerate(_load("demo_shops.json")["shops"], start=1):
        if db.scalar(select(Shop).where(Shop.name == s["name"])):
            continue
        fake = f"+21355000{i:04d}"
        shop = Shop(
            name=s["name"], phone=fake, whatsapp=fake, commune_id=communes.get(s["commune"]),
            lat=s["lat"], lng=s["lng"], hours=s.get("hours"), shop_type=s.get("shop_type", "pieces"),
            parts_origin=s.get("parts_origin", []), sale_mode=s.get("sale_mode"),
            status="verified", source="terrain", verified_at=now, visited_at=now, is_demo=True,
            surveyor="démo",
        )
        db.add(shop)
        db.flush()
        for b in s["brands"]:
            db.add(ShopBrand(shop_id=shop.id, brand_id=brands[b], source="terrain", confirmed_at=now))
        for c in s["categories"]:
            db.add(ShopCategory(shop_id=shop.id, category_id=cats[c], source="terrain", confirmed_at=now))
        for p in s.get("products", []):
            prod = Product(shop_id=shop.id, category_id=cats[p["category"]], title=p["title"], oem_ref=p.get("oem_ref"),
                           part_brand=p.get("part_brand"), condition=p.get("condition", "neuf"), price=p.get("price"))
            db.add(prod)
            db.flush()
            seen = set()
            for fit in p.get("fits", []):
                v = _variant(db, *fit)
                if v and v.id not in seen:
                    seen.add(v.id)
                    db.add(ProductFitment(product_id=prod.id, variant_id=v.id))
                    if p.get("oem_ref"):
                        db.add(PartReference(category_id=prod.category_id, variant_id=v.id, oem_ref=p["oem_ref"],
                                             part_brand=p.get("part_brand"), source="demo"))


def purge_demo(db: Session) -> int:
    ids = [s.id for s in db.scalars(select(Shop).where(Shop.is_demo.is_(True)))]
    db.execute(delete(PartReference).where(PartReference.source == "demo"))
    for sid in ids:
        db.delete(db.get(Shop, sid))
    return len(ids)


def run(db: Session, demo: bool = True) -> None:
    seed_geo(db)
    seed_vehicles(db)
    cats = seed_categories(db)
    seed_faults(db, cats)
    seed_dtc(db, cats)
    seed_knowledge(db)
    if demo:
        seed_demo(db, cats)
    db.commit()


def main() -> None:
    from .db import SessionLocal

    ap = argparse.ArgumentParser()
    ap.add_argument("--no-demo", action="store_true")
    ap.add_argument("--purge-demo", action="store_true")
    args = ap.parse_args()
    with SessionLocal() as db:
        if args.purge_demo:
            n = purge_demo(db)
            db.commit()
            print(f"{n} magasins de démonstration supprimés")
            return
        run(db, demo=not args.no_demo)
        print("Référentiels chargés" + ("" if args.no_demo else " (+ magasins de démonstration fictifs)"))


if __name__ == "__main__":
    main()
