"""Entretien des voitures du compte client (28/11/2026) : prochaines échéances d'après le kilométrage, la date et
l'historique noté par le client. Intervalles indicatifs (`data/seed/maintenance.json`) : le carnet de la voiture fait foi.
"""
from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import MaintenanceRecord, PartCategory, UserVehicle

SOON_KM = 1500
SOON_DAYS = 30


@lru_cache
def items() -> list[dict]:
    path = Path(get_settings().data_dir) / "seed" / "maintenance.json"
    return json.loads(path.read_text(encoding="utf-8"))["items"]


def add_months(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    for day in (d.day, 30, 29, 28):   # 31 janvier + 1 mois -> 28 ou 29 février
        try:
            return date(year, month, day)
        except ValueError:
            continue
    raise ValueError(d)


def schedule(db: Session, car: UserVehicle, today: date | None = None) -> list[dict]:
    """Une ligne par entretien qui concerne la voiture (le carburant écarte bougies ou filtre à gasoil)."""
    today = today or date.today()
    fuel = car.variant.fuel if car.variant else None
    records = list(db.scalars(select(MaintenanceRecord).where(MaintenanceRecord.user_vehicle_id == car.id)
                              .order_by(MaintenanceRecord.done_on.desc(), MaintenanceRecord.id.desc())))
    out = []
    for it in items():
        if it.get("fuel") and fuel and it["fuel"] != fuel:
            continue
        last = next((r for r in records if r.item == it["slug"]), None)
        next_km = next_date = None
        if last:
            next_km = last.km + it["km"] if last.km is not None else None
            next_date = add_months(last.done_on, it["months"])
            km_left = next_km - car.mileage_km if next_km is not None and car.mileage_km is not None else None
            days_left = (next_date - today).days
            if (km_left is not None and km_left <= 0) or days_left <= 0:
                status = "due"
            elif (km_left is not None and km_left <= SOON_KM) or days_left <= SOON_DAYS:
                status = "soon"
            else:
                status = "ok"
        elif car.mileage_km is not None and car.mileage_km >= it["km"]:
            status = "check"     # rien de noté et l'intervalle est dépassé : à vérifier dans le carnet
            km_left = days_left = None
        else:
            status = "unknown" if car.mileage_km is None else "ok"
            next_km = it["km"] if car.mileage_km is not None else None
            km_left = next_km - car.mileage_km if next_km is not None else None
            days_left = None
        cat = db.scalar(select(PartCategory).where(PartCategory.slug == it["part"]))
        out.append({
            "item": it["slug"], "name": it["name"], "why": it["why"], "every_km": it["km"], "every_months": it["months"],
            "status": status, "next_km": next_km, "next_date": next_date.isoformat() if next_date else None,
            "km_left": km_left, "days_left": days_left,
            "last": {"id": last.id, "km": last.km, "done_on": last.done_on.isoformat()} if last else None,
            "part": {"category_id": cat.id, "name": cat.name_fr} if cat else None,
        })
    order = {"due": 0, "check": 1, "soon": 2, "ok": 3, "unknown": 4}
    return sorted(out, key=lambda x: (order[x["status"]], x["km_left"] if x["km_left"] is not None else 1e9))


def due_count(db: Session, car: UserVehicle) -> int:
    return sum(1 for x in schedule(db, car) if x["status"] in ("due", "soon"))
