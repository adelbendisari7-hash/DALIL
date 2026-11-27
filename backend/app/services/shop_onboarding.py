"""Inscription guidée des magasins (plan côté magasin, phase 1) : horaires et « ouvert maintenant », recherche
d'adresse dans la wilaya d'Oran, fiches proches à revendiquer, doublons probables.

Fonctions pures autant que possible : testées sans réseau (la recherche d'adresse prend un client HTTP en paramètre).
"""
from __future__ import annotations

import re
import threading
import time
import unicodedata
from collections import OrderedDict
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Commune, Shop
from .recommendation import haversine_km

ALGIERS = timezone(timedelta(hours=1))   # l'Algérie ne change pas d'heure (UTC+1 toute l'année)
DAY_SHORT = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
# Wilaya d'Oran, large : la recherche d'adresse ne propose rien en dehors
ORAN_VIEWBOX = (-1.10, 35.98, -0.10, 35.40)   # ouest, nord, est, sud
NEARBY_CLAIM_M = 150
DUPLICATE_M = 30


# --- Horaires -------------------------------------------------------------------------------------------------

def check_opening(o: dict | None) -> dict | None:
    """Valide et normalise des horaires structurés ; ValueError avec un message en français sinon."""
    if o is None:
        return None
    days = sorted({int(d) for d in o.get("days", [])})
    if not days or any(d < 0 or d > 6 for d in days):
        raise ValueError("Horaires : choisissez au moins un jour d'ouverture")
    start, end = o.get("from", ""), o.get("to", "")
    if not (TIME_RE.match(start) and TIME_RE.match(end)) or start >= end:
        raise ValueError("Horaires : heure d'ouverture et de fermeture invalides (exemple 08:00 et 18:00)")
    out = {"days": days, "from": start, "to": end}
    brk = o.get("break")
    if brk:
        if len(brk) != 2 or not all(TIME_RE.match(x or "") for x in brk) or not (start < brk[0] < brk[1] < end):
            raise ValueError("Horaires : la pause doit être comprise dans la journée")
        out["break"] = list(brk)
    return out


def _hh(t: str) -> str:
    h, m = t.split(":")
    return f"{int(h)}h" if m == "00" else f"{int(h)}h{m}"


def hours_text(o: dict | None) -> str | None:
    """« Sam-Jeu 8h-18h (pause 12h-13h30) » : le texte affiché partout, tiré des horaires structurés."""
    if not o:
        return None
    days = o["days"]
    # Semaine algérienne : samedi d'abord. Suite continue (Sam-Jeu) ou liste (Sam, Lun, Mer).
    order = [5, 6, 0, 1, 2, 3, 4]
    ordered = [d for d in order if d in days]
    idx = [order.index(d) for d in ordered]
    if len(ordered) > 2 and idx == list(range(idx[0], idx[0] + len(idx))):
        label = f"{DAY_SHORT[ordered[0]]}-{DAY_SHORT[ordered[-1]]}"
    else:
        label = ", ".join(DAY_SHORT[d] for d in ordered)
    text = f"{label} {_hh(o['from'])}-{_hh(o['to'])}"
    if o.get("break"):
        text += f" (pause {_hh(o['break'][0])}-{_hh(o['break'][1])})"
    return text


def open_status(shop: Shop, now: datetime | None = None) -> dict | None:
    """{"open": bool, "label": ...} d'après les horaires et la fermeture exceptionnelle ; None si on ne sait pas."""
    now = (now or datetime.now(timezone.utc)).astimezone(ALGIERS)
    if shop.closed_until and now.date() <= shop.closed_until:
        note = f" : {shop.closed_note}" if shop.closed_note else ""
        return {"open": False, "label": f"Fermé exceptionnellement jusqu'au {shop.closed_until:%d/%m}{note}"}
    o = shop.opening
    if not o:
        return None
    hm = now.strftime("%H:%M")
    in_day = now.weekday() in o["days"] and o["from"] <= hm < o["to"]
    if in_day and o.get("break") and o["break"][0] <= hm < o["break"][1]:
        return {"open": False, "label": f"En pause, rouvre à {_hh(o['break'][1])}"}
    if in_day:
        return {"open": True, "label": f"Ouvert, ferme à {_hh(o['to'])}"}
    return {"open": False, "label": "Fermé"}


# --- Recherche d'adresse (Nominatim, OpenStreetMap) ----------------------------------------------------------

class Geocoder:
    """Nominatim, dans les règles d'usage : une requête par seconde au plus (toute l'application), identifiant
    d'application générique, résultats gardés en mémoire. Seule l'adresse tapée par le magasin est envoyée."""

    def __init__(self, client: httpx.Client | None = None):
        self.client = client
        self.lock = threading.Lock()
        self.last = 0.0
        self.cache: OrderedDict[str, list[dict]] = OrderedDict()

    def search(self, query: str) -> list[dict]:
        q = " ".join(query.split())[:200]
        if len(q) < 3:
            return []
        key = q.lower()
        if key in self.cache:
            return self.cache[key]
        s = get_settings()
        if not s.geocoder_url:
            return []
        params = {"q": q if "oran" in key else f"{q}, Oran", "format": "jsonv2", "limit": 5, "countrycodes": "dz",
                  "viewbox": ",".join(map(str, ORAN_VIEWBOX)), "bounded": 1, "accept-language": "fr", "addressdetails": 0}
        with self.lock:   # une requête par seconde au plus
            wait = 1.0 - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.monotonic()
            client = self.client or httpx.Client(timeout=8.0)
            try:
                r = client.get(s.geocoder_url, params=params, headers={"User-Agent": "DALIL-prototype/0.1"})
                r.raise_for_status()
                rows = r.json()
            finally:
                if self.client is None:
                    client.close()
        out = [{"label": row.get("display_name", ""), "lat": float(row["lat"]), "lng": float(row["lon"])}
               for row in rows if "lat" in row and "lon" in row]
        self.cache[key] = out
        while len(self.cache) > 500:
            self.cache.popitem(last=False)
        return out


geocoder = Geocoder()


# --- Fiches proches, doublons, commune ----------------------------------------------------------------------

def _norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", name.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\[d[ée]mo\]|pi[eè]ces?|auto(s|mobiles?)?|magasin|sarl|eurl|ets|[^a-z0-9 ]", " ", s)
    return " ".join(s.split())


def similar_names(a: str, b: str) -> bool:
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return False
    return na in nb or nb in na or SequenceMatcher(None, na, nb).ratio() >= 0.7


def nearby_claimable(db: Session, lat: float | None, lng: float | None, phone: str | None) -> list[tuple[Shop, float | None]]:
    """Fiches sans gérant au même numéro ou à moins de 150 m : « C'est mon magasin » plutôt qu'un doublon."""
    out: dict[int, tuple[Shop, float | None]] = {}
    if phone:
        for s in db.scalars(select(Shop).where(Shop.phone == phone, Shop.owner_user_id.is_(None))):
            out[s.id] = (s, haversine_km(lat, lng, s.lat, s.lng) if None not in (lat, lng, s.lat, s.lng) else None)
    if lat is not None and lng is not None:
        for s in db.scalars(select(Shop).where(Shop.owner_user_id.is_(None), Shop.lat.is_not(None),
                                              Shop.status != "rejected", Shop.is_demo.is_(False))):
            d = haversine_km(lat, lng, s.lat, s.lng)
            if d * 1000 <= NEARBY_CLAIM_M:
                out[s.id] = (s, d)
    return sorted(out.values(), key=lambda x: (x[1] is None, x[1] or 0))


def possible_duplicates(db: Session, shop: Shop) -> list[Shop]:
    """Autres fiches à moins de 30 m au nom proche : signalées à l'administrateur pour une fusion."""
    if shop.lat is None or shop.lng is None:
        return []
    found = []
    for s in db.scalars(select(Shop).where(Shop.id != shop.id, Shop.lat.is_not(None), Shop.status != "rejected")):
        if haversine_km(shop.lat, shop.lng, s.lat, s.lng) * 1000 <= DUPLICATE_M and similar_names(shop.name, s.name):
            found.append(s)
    return found


def nearest_commune(db: Session, lat: float | None, lng: float | None) -> Commune | None:
    from ..import_osm import nearest_commune as _nearest

    return _nearest(lat, lng, list(db.scalars(select(Commune))))[0]


def today_algiers() -> date:
    return datetime.now(timezone.utc).astimezone(ALGIERS).date()
