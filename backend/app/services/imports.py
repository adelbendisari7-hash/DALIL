"""Import CSV des magasins (back-office, F10) et import Excel/CSV du catalogue (F12)."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime, timezone

from fastapi import HTTPException
from openpyxl import load_workbook
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..models import Brand, Commune, Product, ProductFitment, Shop, ShopBrand, ShopCategory
from ..security import normalize_phone
from .catalog import resolve_category, resolve_variants
from .diagnosis.normalize import normalize

SHOP_COLUMNS = ["name", "phone", "whatsapp", "commune", "lat", "lng", "address", "hours", "brands", "categories",
                "parts_origin", "sale_mode", "shop_type", "surveyor", "source", "osm_id"]
PRODUCT_COLUMNS = ["titre", "famille", "reference", "marque_piece", "etat", "prix", "en_stock", "compatibilite"]


@dataclass
class ImportReport:
    created: int = 0
    updated: int = 0
    errors: list[dict] = field(default_factory=list)


def _split(v: str | None) -> list[str]:
    if not v:
        return []
    return [x.strip() for x in str(v).replace("|", ";").replace(",", ";").split(";") if x.strip()]


def _float(v) -> float | None:
    if v in (None, ""):
        return None
    return float(str(v).replace(",", ".").replace(" ", ""))


def read_table(content: bytes, filename: str) -> list[dict]:
    """Lit un fichier .xlsx ou .csv (séparateur , ou ;) en liste de dictionnaires aux clés normalisées."""
    rows: list[dict] = []
    if filename.lower().endswith((".xlsx", ".xlsm")):
        wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        it = ws.iter_rows(values_only=True)
        header = [normalize(str(h or "")).replace(" ", "_") for h in next(it, [])]
        for r in it:
            if any(c not in (None, "") for c in r):
                rows.append({header[i]: r[i] for i in range(min(len(header), len(r)))})
        return rows
    text = content.decode("utf-8-sig", errors="replace")
    dialect = csv.Sniffer().sniff(text.splitlines()[0] if text else ",", delimiters=",;\t")
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    for r in reader:
        rows.append({normalize(k or "").replace(" ", "_"): v for k, v in r.items()})
    return rows


def import_shops(db: Session, rows: list[dict], default_source: str = "terrain") -> ImportReport:
    """Crée ou fusionne (même téléphone ou même identifiant OSM) les fiches magasins.

    Chaque ligne est entièrement validée avant toute écriture : une ligne fautive est
    signalée et ignorée, sans laisser de fiche à moitié créée.
    """
    rep = ImportReport()
    now = datetime.now(timezone.utc)
    brands = {normalize(b.name): b.id for b in db.scalars(select(Brand))}
    communes = {}
    for c in db.scalars(select(Commune)):
        communes[c.code] = c.id
        communes[normalize(c.nom_fr)] = c.id
    for line, r in enumerate(rows, start=2):
        try:
            name = str(r.get("name") or r.get("nom") or "").strip()
            if not name:
                raise ValueError("nom manquant")
            phone = normalize_phone(str(r["phone"])) if r.get("phone") else None
            wa = normalize_phone(str(r["whatsapp"])) if r.get("whatsapp") else phone
            osm_id = str(r.get("osm_id") or "").strip() or None
            commune_id = None
            if r.get("commune"):
                raw = str(r["commune"]).strip()
                commune_id = communes.get(raw) or communes.get(normalize(raw))
                if commune_id is None:
                    raise ValueError(f"commune inconnue : {raw}")
            brand_ids = []
            for b in _split(r.get("brands") or r.get("marques")):
                if normalize(b) not in brands:
                    raise ValueError(f"marque inconnue : {b}")
                brand_ids.append(brands[normalize(b)])
            cat_ids = []
            for c in _split(r.get("categories") or r.get("familles")):
                cat = resolve_category(db, c)
                if cat is None:
                    raise ValueError(f"famille de pièces inconnue : {c}")
                cat_ids.append(cat.id)
            lat, lng = _float(r.get("lat")), _float(r.get("lng"))
        except (ValueError, KeyError, HTTPException) as e:
            rep.errors.append({"line": line, "error": getattr(e, "detail", None) or str(e)})
            continue

        conds = [Shop.phone == phone] if phone else []
        if osm_id:
            conds.append(Shop.osm_id == osm_id)
        shop = db.scalar(select(Shop).where(or_(*conds))) if conds else None
        is_new = shop is None
        if is_new:
            shop = Shop(name=name, source=str(r.get("source") or default_source), status="draft")
            db.add(shop)
        # Fusion : une valeur existante n'est jamais remplacée par du vide.
        fields = {
            "phone": phone, "whatsapp": wa, "osm_id": osm_id, "commune_id": commune_id,
            "address": r.get("address") or r.get("adresse"), "hours": r.get("hours") or r.get("horaires"),
            "lat": lat, "lng": lng, "sale_mode": r.get("sale_mode"), "shop_type": r.get("shop_type"),
            "surveyor": r.get("surveyor"),
        }
        for k, v in fields.items():
            if v not in (None, ""):
                setattr(shop, k, v)
        if r.get("parts_origin"):
            shop.parts_origin = sorted(set(shop.parts_origin or []) | set(_split(r["parts_origin"])))
        if shop.source == "terrain":
            shop.visited_at = now
        db.flush()
        src = "declared" if shop.source == "osm" else shop.source
        have_b = {sb.brand_id for sb in shop.brands}
        for bid in brand_ids:
            if bid not in have_b:
                shop.brands.append(ShopBrand(brand_id=bid, source=src, confirmed_at=now))
                have_b.add(bid)
        have_c = {sc.category_id for sc in shop.categories}
        for cid in cat_ids:
            if cid not in have_c:
                shop.categories.append(ShopCategory(category_id=cid, source=src, confirmed_at=now))
                have_c.add(cid)
        db.flush()
        rep.created += is_new
        rep.updated += not is_new
    return rep


def import_products(db: Session, shop: Shop, rows: list[dict]) -> ImportReport:
    rep = ImportReport()
    for line, r in enumerate(rows, start=2):
        try:
            title = str(r.get("titre") or r.get("title") or "").strip()
            if not title:
                raise ValueError("titre manquant")
            cat = resolve_category(db, str(r.get("famille") or r.get("category") or title))
            if cat is None:
                raise ValueError(f"famille introuvable : {r.get('famille')}")
            variant_ids: list[int] = []
            for spec in _split(str(r.get("compatibilite") or "")):
                variants = resolve_variants(db, spec)
                if not variants:
                    raise ValueError(f"véhicule non reconnu : {spec}")
                variant_ids += [v.id for v in variants]
            price = _float(r.get("prix"))
        except ValueError as e:
            rep.errors.append({"line": line, "error": str(e)})
            continue
        ref = str(r.get("reference") or r.get("oem_ref") or "").strip() or None
        existing = db.scalar(select(Product).where(Product.shop_id == shop.id, Product.title == title, Product.oem_ref == ref)) if ref else None
        prod = existing or Product(shop_id=shop.id, title=title)
        prod.category_id, prod.oem_ref, prod.price = cat.id, ref, price
        prod.part_brand = str(r.get("marque_piece") or "").strip() or None
        prod.condition = str(r.get("etat") or "neuf").strip().lower() or "neuf"
        prod.in_stock = str(r.get("en_stock") or "oui").strip().lower() not in ("non", "0", "false", "faux", "no")
        db.add(prod)
        db.flush()
        have = {f.variant_id for f in prod.fitments}
        for vid in variant_ids:
            if vid not in have:
                prod.fitments.append(ProductFitment(variant_id=vid))
                have.add(vid)
        rep.created += existing is None
        rep.updated += existing is not None
    db.flush()
    return rep
