"""Recherche de pièces (synonymes compris) et résolution de texte libre vers le référentiel."""
from __future__ import annotations

import difflib
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Brand, Model, PartCategory, VehicleVariant
from .diagnosis.normalize import normalize


def search_categories(db: Session, q: str, limit: int = 10) -> list[tuple[PartCategory, float]]:
    nq = normalize(q)
    if not nq:
        return []
    out = []
    for c in db.scalars(select(PartCategory)):
        names = [normalize(c.name_fr), normalize(c.slug.replace("-", " "))] + [normalize(s) for s in (c.synonyms or [])]
        best = 0.0
        for n in names:
            if nq == n:
                best = max(best, 1.0)
            elif re.search(rf"\b{re.escape(nq)}", n) or re.search(rf"\b{re.escape(n)}\b", nq):
                best = max(best, 0.85)
            else:
                best = max(best, difflib.SequenceMatcher(None, nq, n).ratio() * 0.8)
        if c.parent_id:  # préférer la sous-famille, plus précise, à la famille
            best += 0.02
        if best >= 0.55:
            out.append((c, round(min(best, 1.0), 3)))
    out.sort(key=lambda x: (-x[1], x[0].parent_id is None, x[0].id))
    return out[:limit]


def resolve_category(db: Session, label: str) -> PartCategory | None:
    if not label:
        return None
    slug = db.scalar(select(PartCategory).where(PartCategory.slug == label.strip().lower()))
    if slug:
        return slug
    hits = search_categories(db, label, limit=1)
    return hits[0][0] if hits and hits[0][1] >= 0.8 else None


YEAR_RE = re.compile(r"\b(19[89]\d|20[0-4]\d)\b")


def resolve_variants(db: Session, text: str) -> list[VehicleVariant]:
    """« Dacia Logan 1.5 dCi 2015 » -> variantes compatibles. Moteur et année facultatifs."""
    t = normalize(text)
    for brand in sorted(db.scalars(select(Brand)), key=lambda b: -len(b.name)):
        bn = normalize(brand.name)
        if not t.startswith(bn):
            continue
        rest = t[len(bn):].strip()
        for model in sorted(db.scalars(select(Model).where(Model.brand_id == brand.id)), key=lambda m: -len(m.name)):
            mn = normalize(model.name)
            if not re.match(rf"{re.escape(mn)}\b", rest):
                continue
            tail = rest[len(mn):].strip()
            year_m = YEAR_RE.search(tail)
            year = int(year_m.group(1)) if year_m else None
            engine_txt = YEAR_RE.sub("", tail).strip()
            out = []
            for v in model.variants:
                if engine_txt and normalize(v.engine) not in engine_txt and engine_txt not in normalize(v.engine):
                    continue
                if year and not (v.year_from <= year <= (v.year_to or 9999)):
                    continue
                out.append(v)
            return out
    return []
