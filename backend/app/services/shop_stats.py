"""Statistiques du magasin (plan côté magasin, phase 4) et badge « Répond vite » (idée D).

Tout est agrégé : aucun client n'est identifiable. Apparitions et vues comptent une fois par client (empreinte de
l'adresse IP) et par jour, pour qu'une page rechargée ne gonfle pas les chiffres.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import median

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ContactEvent, Feedback, PartCategory, RequestResponse, SearchEvent, Shop, ShopCategory, ShopEvent
from .recommendation import category_lineage, haversine_km

WINDOW_DAYS = 30
NEAR_KM = 10.0
# « Répond vite » : sur 90 jours, au moins 3 réponses, 70 % des demandes répondues, délai médian d'une heure au plus
FAST_DAYS, FAST_MIN_ANSWERS, FAST_RATE, FAST_MINUTES = 90, 3, 0.7, 60


def _aware(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def record(db: Session, shop_ids: list[int], kind: str, client: str | None) -> None:
    for sid in shop_ids:
        db.add(ShopEvent(shop_id=sid, kind=kind, client_hash=client))


def record_search(db: Session, category_id: int, brand_id: int | None, lat: float | None, lng: float | None) -> None:
    db.add(SearchEvent(category_id=category_id, brand_id=brand_id,
                       lat=round(lat, 2) if lat is not None else None, lng=round(lng, 2) if lng is not None else None))


def _unique_daily(events) -> int:
    """Une fois par client et par jour ; un événement sans empreinte compte pour un."""
    seen, n = set(), 0
    for e in events:
        if e.client_hash is None:
            n += 1
            continue
        key = (e.client_hash, _aware(e.created_at).date())
        if key not in seen:
            seen.add(key)
            n += 1
    return n


def _period(db: Session, shop: Shop, start: datetime, end: datetime) -> dict:
    ev = list(db.scalars(select(ShopEvent).where(ShopEvent.shop_id == shop.id, ShopEvent.created_at >= start,
                                                 ShopEvent.created_at < end)))
    contacts = list(db.scalars(select(ContactEvent).where(ContactEvent.shop_id == shop.id, ContactEvent.created_at >= start,
                                                          ContactEvent.created_at < end)))
    reqs = list(db.scalars(select(RequestResponse).where(RequestResponse.shop_id == shop.id,
                                                         RequestResponse.notified_at >= start, RequestResponse.notified_at < end)))
    answered = [r for r in reqs if r.responded_at is not None]
    delays = [(_aware(r.responded_at) - _aware(r.notified_at)).total_seconds() / 60 for r in answered]
    found = list(db.scalars(select(Feedback).where(Feedback.shop_id == shop.id, Feedback.part_found.is_not(None),
                                                   Feedback.created_at >= start, Feedback.created_at < end)))
    return {
        "impressions": _unique_daily(e for e in ev if e.kind == "impression"),
        "views": _unique_daily(e for e in ev if e.kind == "view"),
        "calls": sum(c.channel == "call" for c in contacts),
        "whatsapp": sum(c.channel == "whatsapp" for c in contacts),
        "requests": len(reqs),
        "answered": len(answered),
        "response_minutes": round(median(delays)) if delays else None,
        "found_yes": sum(bool(f.part_found) for f in found),
        "found_no": sum(not f.part_found for f in found),
    }


def demand_near(db: Session, shop: Shop, since: datetime, limit: int = 8) -> list[dict]:
    """Pièces les plus cherchées par les clients à moins de 10 km du magasin (ou sans position donnée), et si le
    magasin les vend (famille déclarée, ou famille parente)."""
    counts: dict[int, int] = {}
    for e in db.scalars(select(SearchEvent).where(SearchEvent.created_at >= since)):
        if e.lat is not None and shop.lat is not None and haversine_km(shop.lat, shop.lng, e.lat, e.lng) > NEAR_KM:
            continue
        counts[e.category_id] = counts.get(e.category_id, 0) + 1
    sold = {c.category_id for c in db.scalars(select(ShopCategory).where(ShopCategory.shop_id == shop.id))}
    out = []
    for cid, n in sorted(counts.items(), key=lambda x: -x[1])[:limit]:
        cat = db.get(PartCategory, cid)
        lineage, _ = category_lineage(db, cid)
        out.append({"category_id": cid, "name": cat.name_fr if cat else "?", "searches": n,
                    "sold": bool(set(lineage) & sold)})
    return out


def stats(db: Session, shop: Shop, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(days=WINDOW_DAYS)
    return {"days": WINDOW_DAYS, "current": _period(db, shop, start, now + timedelta(seconds=1)),
            "previous": _period(db, shop, start - timedelta(days=WINDOW_DAYS), start),
            "demand": demand_near(db, shop, start), "fast_reply": fast_reply(db, shop.id, now)}


def fast_reply(db: Session, shop_id: int, now: datetime | None = None) -> bool:
    """Badge « Répond vite » (idée D)."""
    now = now or datetime.now(timezone.utc)
    reqs = list(db.scalars(select(RequestResponse).where(RequestResponse.shop_id == shop_id,
                                                         RequestResponse.notified_at >= now - timedelta(days=FAST_DAYS))))
    answered = [r for r in reqs if r.responded_at is not None]
    if len(answered) < FAST_MIN_ANSWERS or len(answered) / len(reqs) < FAST_RATE:
        return False
    delays = [(_aware(r.responded_at) - _aware(r.notified_at)).total_seconds() / 60 for r in answered]
    return median(delays) <= FAST_MINUTES
