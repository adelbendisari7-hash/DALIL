"""Rappels des constructeurs pour une voiture du compte (28/11/2026), tirés de RappelConso (DGCCRF, Licence Ouverte,
déjà dans la base de connaissances).

Ce sont des rappels publiés en France : une voiture d'Algérie du même modèle n'est pas forcément concernée (années,
série, numéro de châssis). DALIL dit donc « rappel possible » et renvoie à la fiche officielle ; jamais « concernée ».

Correspondance : même marque (alias : VW, Mercedes-Benz, Citroën...), et le nom de base du modèle cité comme un mot
dans la liste des modèles du rappel (« clio », « 208 », « golf »), avant toute mention de numéro de châssis. Si la
voiture a une génération (Clio 4) et que le rappel en cite une autre pour ce modèle (« clio v »), le rappel est écarté ;
s'il n'en cite aucune, il est gardé « génération à vérifier ».
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Brand, KnowledgeChunk, Model, UserVehicle

SOURCE = "rappelconso"
BRAND_ALIASES = {"vw": "volkswagen", "mercedes-benz": "mercedes", "mercedes benz": "mercedes", "opel/vauxhall": "opel",
                 "ds automobiles": "ds", "citroen": "citroen"}
EXCLUDED_MAKES = {"renault trucks", "bmw motorrad"}
# Modèles voisins qui commencent par le même nom (« c3 aircross » n'est pas une « c3 »)
SIBLING_SUFFIXES = ("aircross", "picasso", "cactus", "crossback", "allspace", "sportsvan", "plug-in", "e-tech")
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def brand_key(s: str) -> str:
    b = norm(s)
    return BRAND_ALIASES.get(b, b)


def split_model(name: str) -> tuple[str, int | None]:
    """« Clio 4 » -> (« clio », 4) ; « Logan MCV » -> (« logan mcv », None) ; « 208 » -> (« 208 », None)."""
    n = norm(name)
    m = re.fullmatch(r"(.+?)\s+(\d{1,2}|i{1,3}|iv|v|vi{0,3}|ix|x)", n)
    if m and not m.group(1).isdigit():
        g = m.group(2)
        return m.group(1), int(g) if g.isdigit() else ROMAN[g]
    return n, None


def _generation_after(text: str, base: str) -> set[int]:
    """Générations citées juste après le nom du modèle : « clio iv », « clio 5 », « 208 v2 »."""
    gens = set()
    for m in re.finditer(rf"\b{re.escape(base)}\s*(?:v(\d{{1,2}})\b|(\d{{1,2}})\b|\b(i{{1,3}}|iv|v|vi{{0,3}}|ix|x)\b)", text):
        if m.group(1):
            gens.add(int(m.group(1)))
        elif m.group(2) and not base.isdigit():
            gens.add(int(m.group(2)))
        elif m.group(3):
            gens.add(ROMAN[m.group(3)])
    return gens


@lru_cache(maxsize=4)
def _index(_stamp: tuple) -> list[dict]:
    from ..db import SessionLocal
    out = []
    with SessionLocal() as db:
        for c in db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.source == SOURCE)):
            meta = c.meta or {}
            vehicle = meta.get("vehicle") or {}
            make = brand_key(vehicle.get("make") or "")
            models = norm(vehicle.get("model") or "")
            models = re.split(r"\b(?:niv|vin)\b", models)[0]   # pas de correspondance dans un numéro de châssis
            if not make or make in EXCLUDED_MAKES or not models:
                continue
            text = c.text or ""
            # « Rappel <marque> <modèles> : <motif> » ; la liste des modèles peut elle-même contenir « niv : ... »
            raw_models = (vehicle.get("model") or "").lower()
            at = text.lower().find(raw_models) if raw_models else -1
            cut = text.find(" : ", at + len(raw_models) if at >= 0 else 0)
            body = text[cut + 3:] if cut >= 0 else text
            motif, _, risque = body.partition(" Risque : ")
            out.append({"make": make, "models": models, "models_label": (vehicle.get("model") or "").strip(" ."),
                        "motif": motif.strip(), "risque": risque.strip(" ."), "url": meta.get("url"),
                        "date": (meta.get("date") or "")[:10] or None, "id": c.id})
    out.sort(key=lambda r: r["date"] or "", reverse=True)
    return out


def index(db: Session) -> list[dict]:
    n, last = db.execute(select(func.count(), func.max(KnowledgeChunk.id)).where(KnowledgeChunk.source == SOURCE)).one()
    return _index((n, last))


def car_identity(car: UserVehicle) -> tuple[str, str] | None:
    """(marque, modèle) de la voiture : depuis le référentiel, sinon depuis la marque et le modèle saisis."""
    if car.variant:
        return car.variant.model.brand.name, car.variant.model.name
    label = (car.label or "").strip()
    if " " in label:
        brand, model = label.split(" ", 1)
        return brand, model
    return None


def _siblings(db: Session, brand: str, base: str, own: str) -> list[str]:
    names = {norm(n) for n in db.scalars(select(Model.name).join(Brand, Brand.id == Model.brand_id)
                                         .where(func.lower(Brand.name) == brand.lower()))}
    sib = {n for n in names if n.startswith(base + " ") and n != own and split_model(n)[0] != base}
    sib |= {f"{base} {s}" for s in SIBLING_SUFFIXES}
    return sorted(sib, key=len, reverse=True)


def for_car(db: Session, car: UserVehicle, limit: int = 20) -> list[dict]:
    ident = car_identity(car)
    if not ident:
        return []
    make = brand_key(ident[0])
    base, gen = split_model(ident[1])
    if len(base) < 2:
        return []
    word = re.compile(rf"(?<![a-z0-9]){re.escape(base)}(?![a-z0-9])")
    siblings = _siblings(db, ident[0], base, norm(ident[1]))
    out = []
    for r in index(db):
        if r["make"] != make:
            continue
        models = r["models"]
        for sib in siblings:   # « c3 aircross » retiré avant de chercher « c3 »
            models = re.sub(rf"(?<![a-z0-9]){re.escape(sib)}(?![a-z0-9])", " ", models)
        if not word.search(models):
            continue
        gens = _generation_after(models, base)
        if gen is not None and gens and gen not in gens:
            continue   # le rappel cite une autre génération de ce modèle
        out.append({"id": r["id"], "models": r["models_label"], "motif": r["motif"], "risque": r["risque"] or None,
                    "date": r["date"], "url": r["url"],
                    "match": "generation" if gen is not None and gen in gens else "model"})
        if len(out) >= limit:
            break
    return out
