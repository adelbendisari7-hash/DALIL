"""Import CSV des magasins (back-office, F10) et import Excel/CSV du catalogue (F12)."""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from fastapi import HTTPException
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Brand, Commune, PartCategory, Product, ProductFitment, Shop, ShopBrand, ShopCategory
from ..security import normalize_phone
from .catalog import resolve_category, resolve_variants
from .diagnosis.normalize import normalize

SHOP_COLUMNS = ["name", "phone", "whatsapp", "commune", "lat", "lng", "address", "hours", "brands", "categories",
                "parts_origin", "sale_mode", "shop_type", "specialties", "surveyor", "source", "osm_id"]
# En-têtes français acceptés (liste de visite remplie sur le terrain, data/terrain/) -> colonne d'import.
SHOP_ALIASES = {"nom": "name", "telephone": "phone", "id_osm": "osm_id", "type": "shop_type", "adresse": "address",
                "horaires": "hours", "marques": "brands", "familles": "categories", "origine_des_pieces": "parts_origin",
                "mode_de_vente": "sale_mode", "enqueteur": "surveyor", "specialites": "specialties"}
PRODUCT_COLUMNS = ["titre", "famille", "reference", "marque_piece", "etat", "prix", "en_stock", "compatibilite"]


@dataclass
class ImportReport:
    created: int = 0
    updated: int = 0
    errors: list[dict] = field(default_factory=list)
    notes: list[dict] = field(default_factory=list)  # fusions et numéros écartés, à vérifier sur place


def _first_phone(raw: str) -> str:
    """Un champ peut contenir plusieurs numéros (« 041 00 00 00 / 0661 00 00 00 ») : le premier mobile valide."""
    parts = [x for x in re.split(r"[/;,|]| ou ", str(raw)) if x.strip()]
    if len(parts) > 1:
        for x in parts:
            try:
                return normalize_phone(x)
            except HTTPException:
                continue
    return normalize_phone(str(raw))


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
        r = {**{SHOP_ALIASES[k]: v for k, v in r.items() if k in SHOP_ALIASES and v not in (None, "")}, **{
            k: v for k, v in r.items() if v not in (None, "")}}
        try:
            name = str(r.get("name") or r.get("nom") or "").strip()
            if not name:
                raise ValueError("nom manquant")
            phone = _first_phone(r["phone"]) if r.get("phone") else None
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
            from .garages import parse_specialties
            specialties = parse_specialties(str(r.get("specialties") or ""))
        except (ValueError, KeyError, HTTPException) as e:
            rep.errors.append({"line": line, "error": getattr(e, "detail", None) or str(e)})
            continue

        # Même identifiant OSM d'abord, puis même téléphone.
        shop = db.scalar(select(Shop).where(Shop.osm_id == osm_id)) if osm_id else None
        if shop is None and phone:
            shop = db.scalar(select(Shop).where(Shop.phone == phone))
        is_new = shop is None
        # Deux lieux OSM distincts au même téléphone : on fusionne (même commerce probable) sans écraser
        # l'identifiant ni la position du premier, et on le signale pour vérification sur place.
        other_place = not is_new and osm_id and shop.osm_id and shop.osm_id != osm_id
        if other_place:
            rep.notes.append({"line": line, "note": f"même téléphone que la fiche {shop.id} ({shop.name}) : "
                                                   f"{osm_id} fusionné avec {shop.osm_id}, à vérifier sur place"})
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
        if other_place:
            for k in ("osm_id", "lat", "lng", "address", "commune_id"):
                fields.pop(k)
        for k, v in fields.items():
            if v not in (None, ""):
                setattr(shop, k, v)
        if r.get("parts_origin"):
            shop.parts_origin = sorted(set(shop.parts_origin or []) | set(_split(r["parts_origin"])))
        if specialties:
            shop.specialties = sorted(set(shop.specialties or []) | set(specialties))
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
        prod.price_confirmed_at = datetime.now(timezone.utc)
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


TEMPLATE_HEADERS = ["Titre", "Famille", "Reference", "Marque_piece", "Etat", "Prix", "En_stock", "Compatibilite"]
TEMPLATE_EXAMPLES = [
    ["Plaquettes de frein avant Logan", "plaquettes avant", "", "Bosch", "adaptable", 4500, "oui", "Dacia Logan 1.5 dCi 2015"],
    ["Filtre à huile", "filtre à huile", "", "Mann", "neuf", 900, "oui", "Renault Symbol 2016; Dacia Logan 1.5 dCi 2015"],
]


def product_template(db: Session) -> bytes:
    """Modèle Excel du catalogue (F12). L'import lit la première feuille seulement : les exemples et la liste des
    familles sont sur des feuilles à part, pour ne jamais être importés par erreur."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Catalogue"
    ws.append(TEMPLATE_HEADERS)
    for c in ws[1]:
        c.font = Font(bold=True)
    ex = wb.create_sheet("Exemples")
    ex.append(TEMPLATE_HEADERS)
    for row in TEMPLATE_EXAMPLES:
        ex.append(row)
    ex.append([])
    ex.append(["Etat : neuf, origine, adaptable ou occasion. En_stock : oui ou non. Prix en dinars, sans espace."])
    ex.append(["Compatibilite : « Marque Modèle Motorisation Année », plusieurs véhicules séparés par ; (facultatif)."])
    fam = wb.create_sheet("Familles")
    fam.append(["Famille (à recopier dans la colonne Famille)", "Groupe"])
    parents = {c.id: c.name_fr for c in db.scalars(select(PartCategory).where(PartCategory.parent_id.is_(None)))}
    for c in db.scalars(select(PartCategory).where(PartCategory.parent_id.is_not(None)).order_by(PartCategory.parent_id, PartCategory.name_fr)):
        fam.append([c.name_fr, parents.get(c.parent_id, "")])
    for sheet in (ws, ex, fam):
        for col in sheet.columns:
            sheet.column_dimensions[col[0].column_letter].width = max(12, min(45, max(len(str(c.value or "")) for c in col) + 2))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
