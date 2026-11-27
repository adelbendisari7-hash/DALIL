"""Moteur de recommandation des magasins (section 6.4).

score = 0,35·catalogue + 0,25·marque + 0,20·famille + 0,10·proximité + 0,10·fiabilité

La partie `score_shop` est une fonction pure (testée par des scénarios écrits à la main) ;
`recommend` rassemble les signaux depuis la base.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import String, cast, func, select
from sqlalchemy.orm import Session

from ..models import (
    Feedback,
    PartCategory,
    Product,
    ProductFitment,
    RequestResponse,
    Shop,
    ShopBrand,
    ShopCategory,
    VehicleVariant,
)

WEIGHTS = {"catalog": 0.35, "brand": 0.25, "category": 0.20, "proximity": 0.10, "reliability": 0.10}
PROXIMITY_SCALE_KM = 5.0  # à 5 km, le signal vaut 1/e
STALE_DAYS = 182  # six mois
RECOMMENDABLE_STATUSES = ("verified", "claimed")


@dataclass
class ShopSignals:
    shop_id: int
    name: str
    catalog: float = 0.0  # 1 produit compatible ; 0,5 produit de la famille sans véhicule connu
    sells_brand: bool = False
    brand_source: str | None = None
    sells_category: bool = False
    category_source: str | None = None
    distance_km: float | None = None
    found_yes: int = 0
    found_no: int = 0
    requests_notified: int = 0
    requests_answered: int = 0
    confirmed_at: datetime | None = None
    brand_name: str | None = None
    category_name: str | None = None
    matching_refs: list[str] = field(default_factory=list)


@dataclass
class ScoredShop:
    shop_id: int
    score: float
    breakdown: dict[str, float]
    reasons: list[str]
    stale: bool
    distance_km: float | None


def proximity(distance_km: float | None) -> float:
    if distance_km is None:
        return 0.5  # position inconnue : signal neutre, ne change pas l'ordre
    return math.exp(-max(distance_km, 0.0) / PROXIMITY_SCALE_KM)


def freshness(confirmed_at: datetime | None, now: datetime) -> float:
    """1 jusqu'à six mois, puis décroissance linéaire jusqu'à 0 à douze mois."""
    if confirmed_at is None:
        return 0.0
    if confirmed_at.tzinfo is None:
        confirmed_at = confirmed_at.replace(tzinfo=timezone.utc)
    age = (now - confirmed_at).days
    if age <= STALE_DAYS:
        return 1.0
    return max(0.0, 1.0 - (age - STALE_DAYS) / STALE_DAYS)


def reliability(s: ShopSignals, now: datetime) -> float:
    # Lissage bayésien : un magasin sans historique part de 0,5 et non de 0 ou 1.
    found_rate = (s.found_yes + 1) / (s.found_yes + s.found_no + 2)
    response_rate = (s.requests_answered + 1) / (s.requests_notified + 2)
    return 0.5 * found_rate + 0.3 * freshness(s.confirmed_at, now) + 0.2 * response_rate


def score_shop(s: ShopSignals, now: datetime | None = None) -> ScoredShop:
    now = now or datetime.now(timezone.utc)
    b = {
        "catalog": s.catalog,
        "brand": 1.0 if s.sells_brand else 0.0,
        "category": 1.0 if s.sells_category else 0.0,
        "proximity": proximity(s.distance_km),
        "reliability": reliability(s, now),
    }
    total = sum(WEIGHTS[k] * v for k, v in b.items())
    stale = freshness(s.confirmed_at, now) < 1.0

    reasons: list[str] = []
    if s.catalog >= 1:
        reasons.append("a la pièce au catalogue" + (f" (réf. {', '.join(s.matching_refs[:2])})" if s.matching_refs else ""))
    elif s.catalog > 0:
        reasons.append("a des produits de cette famille au catalogue")
    if s.sells_brand:
        reasons.append(f"vend {s.brand_name}" if s.brand_name else "vend cette marque")
    if s.sells_category:
        reasons.append(f"vend {s.category_name.lower()}" if s.category_name else "vend cette famille de pièces")
    if s.distance_km is not None:
        reasons.append(f"à {s.distance_km:.1f} km".replace(".", ","))
    if s.found_yes:
        reasons.append(f"pièce trouvée par {s.found_yes} client(s)")
    if stale:
        reasons.append("fiche à reconfirmer")
    return ScoredShop(s.shop_id, round(total, 4), {k: round(v, 3) for k, v in b.items()}, reasons, stale, s.distance_km)


def rank(signals: list[ShopSignals], now: datetime | None = None) -> list[ScoredShop]:
    scored = [score_shop(s, now) for s in signals]
    return sorted(scored, key=lambda x: (-x.score, x.distance_km if x.distance_km is not None else 1e9, x.shop_id))


# --- Accès base -----------------------------------------------------------

def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def category_lineage(db: Session, category_id: int) -> tuple[set[int], set[int]]:
    """Renvoie (la catégorie et ses ancêtres, la catégorie et ses descendants)."""
    cats = {c.id: c for c in db.scalars(select(PartCategory))}
    ancestors, cur = set(), cats.get(category_id)
    while cur is not None:
        ancestors.add(cur.id)
        cur = cats.get(cur.parent_id) if cur.parent_id else None
    descendants, frontier = {category_id}, [category_id]
    while frontier:
        pid = frontier.pop()
        for c in cats.values():
            if c.parent_id == pid and c.id not in descendants:
                descendants.add(c.id)
                frontier.append(c.id)
    return ancestors, descendants


def recommend(
    db: Session,
    category_id: int,
    variant_id: int | None = None,
    lat: float | None = None,
    lng: float | None = None,
    limit: int = 20,
    include_demo: bool = True,
) -> list[tuple[Shop, ScoredShop]]:
    category = db.get(PartCategory, category_id)
    if category is None:
        return []
    ancestors, descendants = category_lineage(db, category_id)
    variant = db.get(VehicleVariant, variant_id) if variant_id else None
    brand_id = variant.model.brand_id if variant else None
    brand_name = variant.model.brand.name if variant else None

    q = select(Shop).where(Shop.status.in_(RECOMMENDABLE_STATUSES))
    if not include_demo:
        q = q.where(Shop.is_demo.is_(False))
    shops = list(db.scalars(q))
    if not shops:
        return []
    ids = [s.id for s in shops]

    brand_rows = {}
    if brand_id:
        for sb in db.scalars(select(ShopBrand).where(ShopBrand.brand_id == brand_id, ShopBrand.shop_id.in_(ids))):
            brand_rows[sb.shop_id] = sb
    cat_rows: dict[int, ShopCategory] = {}
    for sc in db.scalars(select(ShopCategory).where(ShopCategory.category_id.in_(ancestors), ShopCategory.shop_id.in_(ids))):
        cat_rows.setdefault(sc.shop_id, sc)

    products = list(db.scalars(
        select(Product).where(Product.shop_id.in_(ids), Product.category_id.in_(descendants), Product.in_stock.is_(True))
    ))
    fit = set()
    if variant_id and products:
        fit = {
            pid for (pid,) in db.execute(
                select(ProductFitment.product_id).where(
                    ProductFitment.variant_id == variant_id,
                    ProductFitment.product_id.in_([p.id for p in products]),
                )
            )
        }

    # « Pièce trouvée » : un retour par client et par jour (empreinte + date), pour qu'on ne puisse pas gonfler le
    # score d'un magasin en répétant le même retour. Retours anciens sans empreinte : comptés un par un.
    voter = func.coalesce(Feedback.client_hash, "id:" + cast(Feedback.id, String)) + "|" + func.date(Feedback.created_at)
    fb = {
        (sid, found): n for sid, found, n in db.execute(
            select(Feedback.shop_id, Feedback.part_found, func.count(func.distinct(voter)))
            .where(Feedback.shop_id.in_(ids), Feedback.part_found.is_not(None))
            .group_by(Feedback.shop_id, Feedback.part_found)
        )
    }
    resp = {
        sid: (n, answered or 0) for sid, n, answered in db.execute(
            select(
                RequestResponse.shop_id,
                func.count(),
                func.count(RequestResponse.responded_at),
            ).where(RequestResponse.shop_id.in_(ids)).group_by(RequestResponse.shop_id)
        )
    }

    signals = []
    for shop in shops:
        sp = [p for p in products if p.shop_id == shop.id]
        catalog, refs = 0.0, []
        if variant_id:
            matched = [p for p in sp if p.id in fit]
            if matched:
                catalog, refs = 1.0, [p.oem_ref for p in matched if p.oem_ref]
        elif sp:
            catalog = 0.5
        dist = haversine_km(lat, lng, shop.lat, shop.lng) if None not in (lat, lng, shop.lat, shop.lng) else None
        sb, sc = brand_rows.get(shop.id), cat_rows.get(shop.id)
        dates = [d for d in (shop.verified_at, shop.visited_at, sb.confirmed_at if sb else None, sc.confirmed_at if sc else None) if d]
        n_notified, n_answered = resp.get(shop.id, (0, 0))
        signals.append(ShopSignals(
            shop_id=shop.id, name=shop.name, catalog=catalog,
            sells_brand=sb is not None, brand_source=sb.source if sb else None,
            sells_category=sc is not None, category_source=sc.source if sc else None,
            distance_km=dist,
            found_yes=fb.get((shop.id, True), 0), found_no=fb.get((shop.id, False), 0),
            requests_notified=n_notified, requests_answered=n_answered,
            confirmed_at=max(dates) if dates else None,
            brand_name=brand_name, category_name=category.name_fr, matching_refs=refs,
        ))
    by_id = {s.id: s for s in shops}
    ranked = [r for r in rank(signals) if r.breakdown["brand"] or r.breakdown["category"] or r.breakdown["catalog"]]
    return [(by_id[r.shop_id], r) for r in ranked[:limit]]


def offers(db: Session, shop_ids: list[int], category_id: int, variant_id: int | None = None) -> dict[int, dict]:
    """Meilleure offre de chaque magasin pour comparer les prix : le produit en stock le moins cher **compatible**
    avec le véhicule ; à défaut, le moins cher de la famille (compatibilité à vérifier avec le vendeur). Prix lus dans
    le catalogue du magasin, jamais estimés."""
    if not shop_ids:
        return {}
    _, descendants = category_lineage(db, category_id)
    products = list(db.scalars(select(Product).where(Product.shop_id.in_(shop_ids), Product.category_id.in_(descendants),
                                                     Product.in_stock.is_(True), Product.price.is_not(None))))
    fit = set()
    if variant_id and products:
        fit = {pid for (pid,) in db.execute(select(ProductFitment.product_id).where(
            ProductFitment.variant_id == variant_id, ProductFitment.product_id.in_([p.id for p in products])))}
    now = datetime.now(timezone.utc)
    out: dict[int, dict] = {}
    for sid in shop_ids:
        mine = [p for p in products if p.shop_id == sid]
        compatible = [p for p in mine if p.id in fit]
        pool, ok = (compatible, True) if compatible else (mine, False if variant_id else None)
        if not pool:
            continue
        best = min(pool, key=lambda p: p.price)
        confirmed = best.price_confirmed_at
        if confirmed is not None and confirmed.tzinfo is None:
            confirmed = confirmed.replace(tzinfo=timezone.utc)
        out[sid] = {"product_id": best.id, "title": best.title, "price": best.price, "condition": best.condition,
                    "oem_ref": best.oem_ref, "photo_url": best.photo_url, "compatible": ok, "count": len(pool),
                    "confirmed_days": (now - confirmed).days if confirmed else None}
    return out
