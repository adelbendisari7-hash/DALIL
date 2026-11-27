"""Historique des prix d'une pièce (28/11/2026).

Chaque fois qu'un prix est fixé, changé ou retiré dans un catalogue (inscription d'un produit, modification, prix en
un toucher, import Excel, retrait), une ligne `PricePoint` est écrite au moment où la base enregistre : aucun chemin
d'écriture ne peut l'oublier. Le résumé décrit l'état des catalogues à la fin de chaque mois : prix le plus bas,
médiane, plus haut, nombre de magasins. Prix lus dans les catalogues, jamais estimés ; ceux des magasins fictifs ne
servent que s'il n'existe aucun vrai magasin, et sont alors marqués comme fictifs.
"""
from __future__ import annotations

from datetime import datetime, timezone
from statistics import median

from sqlalchemy import event, inspect, select
from sqlalchemy.orm import Session

from ..models import PricePoint, Product, Shop
from .recommendation import RECOMMENDABLE_STATUSES, category_lineage

MIN_SHOPS = 2   # en dessous, pas de « médiane » : un seul magasin n'est pas un prix du marché


def _point(p: Product, price: float | None) -> PricePoint:
    return PricePoint(product_id=p.id, shop_id=p.shop_id, category_id=p.category_id, condition=p.condition or "neuf",
                      price=price)


@event.listens_for(Session, "after_flush")
def _record_prices(session: Session, _ctx) -> None:
    """Après chaque écriture : un point par produit nouveau avec prix, par prix (ou état) changé, par produit retiré.
    Après l'écriture et non avant, pour que le produit nouveau ait déjà son identifiant."""
    points = []
    for obj in session.new:
        if isinstance(obj, Product) and obj.price is not None:
            points.append(_point(obj, obj.price))
    for obj in session.dirty:
        if not isinstance(obj, Product):
            continue
        st = inspect(obj)
        if any(st.attrs[a].history.has_changes() for a in ("price", "condition", "category_id")):
            points.append(_point(obj, obj.price))
    gone_shops = {o.id for o in session.deleted if isinstance(o, Shop)}
    for obj in session.deleted:
        if isinstance(obj, Product) and obj.price is not None and obj.shop_id not in gone_shops:
            points.append(_point(obj, None))
    if points:
        session.add_all(points)   # écrites au prochain passage, sans redéclencher d'autre point


def _month_ends(now: datetime, months: int) -> list[tuple[str, datetime]]:
    out = []
    y, m = now.year, now.month
    for _ in range(months):
        label = f"{y:04d}-{m:02d}"
        out.append((label, now if not out else datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=timezone.utc)))
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return out[::-1]


def _aware(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def summary(db: Session, category_id: int, condition: str | None = None, months: int = 6,
            now: datetime | None = None) -> dict:
    """État des catalogues à la fin de chacun des `months` derniers mois (le mois en cours : aujourd'hui).

    Pour chaque produit, le dernier prix connu à cette date ; un produit retiré sort du calcul. Par mois : plus bas,
    médiane, plus haut, nombre de magasins et de produits. `trend_pct` compare la médiane d'aujourd'hui à la plus
    ancienne médiane disponible de la période (au moins deux magasins de part et d'autre)."""
    now = _aware(now or datetime.now(timezone.utc))
    _, descendants = category_lineage(db, category_id)
    rows = db.execute(
        select(PricePoint, Shop.is_demo).join(Shop, Shop.id == PricePoint.shop_id)
        .where(PricePoint.category_id.in_(descendants), Shop.status.in_(RECOMMENDABLE_STATUSES))
        .order_by(PricePoint.recorded_at, PricePoint.id)
    ).all()
    real = [p for p, demo in rows if not demo]
    demo = not real and bool(rows)
    points = real or [p for p, _ in rows]

    def state_at(end: datetime) -> dict[int, PricePoint]:
        last: dict[int, PricePoint] = {}
        for p in points:
            if _aware(p.recorded_at) <= end:
                last[p.product_id] = p
        return {pid: p for pid, p in last.items() if p.price is not None and (condition is None or p.condition == condition)}

    series = []
    for label, end in _month_ends(now, months):
        cur = state_at(end)
        prices = sorted(p.price for p in cur.values())
        shops = {p.shop_id for p in cur.values()}
        series.append({
            "month": label, "products": len(prices), "shops": len(shops),
            "min": prices[0] if prices else None, "max": prices[-1] if prices else None,
            "median": median(prices) if len(shops) >= MIN_SHOPS else None,
        })

    current = state_at(now)
    by_condition = {}
    for cond in ("neuf", "adaptable", "occasion"):
        ps = sorted(p.price for p in current.values() if p.condition == cond)
        if ps:
            by_condition[cond] = {"min": ps[0], "median": median(ps), "max": ps[-1], "products": len(ps),
                                  "shops": len({p.shop_id for p in current.values() if p.condition == cond})}

    trend = None
    last = series[-1]
    first = next((s for s in series[:-1] if s["median"] is not None), None)
    if first and last["median"] is not None and first["median"]:
        trend = round((last["median"] - first["median"]) / first["median"] * 100)
    return {"category_id": category_id, "condition": condition, "demo": demo, "months": series,
            "now": last, "by_condition": by_condition, "trend_pct": trend, "since": first["month"] if first else None}
