"""Mécaniciens et garages (28/11/2026) : spécialités déclarées par le garage (ou relevées sur le terrain), et
classement des garages pour la pièce trouvée par le diagnostic.

Un garage n'est proposé que s'il est vérifié par l'équipe ou revendiqué par son gérant, comme un magasin. Le score
explique son classement : spécialité qui couvre la famille de la pièce (1), mécanique générale (0,5), sinon 0 ;
proximité ; ouvert maintenant. Rien n'est estimé : ni prix de main-d'œuvre, ni délai.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import PartCategory, Shop
from .recommendation import RECOMMENDABLE_STATUSES, category_lineage, haversine_km

# Spécialité -> familles de pièces de la taxonomie qu'elle couvre (slugs des familles racines)
SPECIALTIES: dict[str, dict] = {
    "mecanique-generale": {"name": "Mécanique générale", "families": []},
    "freinage-suspension": {"name": "Freinage et suspension", "families": ["freinage", "suspension", "train-roulant", "direction"]},
    "moteur-distribution": {"name": "Moteur et distribution", "families": ["moteur", "distribution", "refroidissement", "filtration"]},
    "diesel-injection": {"name": "Diesel et injection", "families": ["alimentation", "allumage", "gestion-moteur"]},
    "electricite": {"name": "Électricité auto", "families": ["electricite", "allumage"]},
    "diagnostic-electronique": {"name": "Diagnostic électronique (valise)", "families": ["gestion-moteur", "electricite"]},
    "embrayage-boite": {"name": "Embrayage et boîte de vitesses", "families": ["transmission", "train-roulant"]},
    "climatisation": {"name": "Climatisation", "families": ["climatisation"]},
    "echappement": {"name": "Échappement", "families": ["echappement"]},
    "pneus-geometrie": {"name": "Pneus et géométrie", "families": ["train-roulant", "direction", "suspension"]},
}
W_MATCH, W_NEAR, W_OPEN = 0.6, 0.3, 0.1


def specialty_names(slugs: list[str] | None) -> list[str]:
    return [SPECIALTIES[s]["name"] for s in (slugs or []) if s in SPECIALTIES]


def check_specialties(slugs: list[str]) -> list[str]:
    unknown = [s for s in slugs if s not in SPECIALTIES]
    if unknown:
        raise ValueError(f"Spécialité inconnue : {', '.join(unknown)}")
    return sorted(set(slugs))


def parse_specialties(text: str) -> list[str]:
    """Colonne « spécialités » de la liste de visite : slugs ou noms, séparés par ; , ou |."""
    import re
    from .recalls import norm
    by_name = {norm(v["name"]): k for k, v in SPECIALTIES.items()}
    out = []
    for part in re.split(r"[;,|]", text or ""):
        p = norm(part)
        if not p:
            continue
        slug = p if p in SPECIALTIES else by_name.get(p)
        if slug is None:
            raise ValueError(f"spécialité inconnue : {part.strip()}")
        out.append(slug)
    return sorted(set(out))


def family_of(db: Session, category_id: int) -> str | None:
    ancestors, _ = category_lineage(db, category_id)
    for cid in ancestors:
        c = db.get(PartCategory, cid)
        if c is not None and c.parent_id is None:
            return c.slug
    return None


def match(slugs: list[str] | None, family: str | None) -> tuple[float, str | None]:
    slugs = slugs or []
    for s in slugs:
        if family and family in SPECIALTIES.get(s, {}).get("families", []):
            return 1.0, SPECIALTIES[s]["name"]
    if "mecanique-generale" in slugs:
        return 0.5, SPECIALTIES["mecanique-generale"]["name"]
    return 0.0, None


def recommend(db: Session, category_id: int | None, lat: float | None, lng: float | None, limit: int = 10) -> list[dict]:
    from ..schemas import shop_out
    family = family_of(db, category_id) if category_id else None
    garages = list(db.scalars(select(Shop).where(Shop.shop_type == "garage", Shop.status.in_(RECOMMENDABLE_STATUSES))))
    out = []
    for g in garages:
        m, why = match(g.specialties, family) if family else (0.5 if g.specialties else 0.0, None)
        dist = haversine_km(lat, lng, g.lat, g.lng) if None not in (lat, lng, g.lat, g.lng) else None
        near = 1.0 / (1.0 + dist / 3.0) if dist is not None else 0.3
        status = shop_out(g, full=False)["open_status"]
        opened = 1.0 if status and status.get("open") else 0.0
        score = W_MATCH * m + W_NEAR * near + W_OPEN * opened
        reasons = []
        if why:
            reasons.append(f"spécialité : {why.lower()}")
        if dist is not None:
            reasons.append(f"à {dist:.1f} km".replace(".", ","))
        if opened:
            reasons.append("ouvert maintenant")
        out.append({**shop_out(g, full=False), "score": round(score, 3), "reasons": reasons,
                    "distance_km": round(dist, 2) if dist is not None else None,
                    "specialties": specialty_names(g.specialties), "match": m})
    out.sort(key=lambda x: (-x["score"], x["distance_km"] if x["distance_km"] is not None else 1e9, x["id"]))
    return out[:limit]
