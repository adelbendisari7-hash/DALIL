"""Avis vérifiés « pièce trouvée » sur la fiche d'un magasin (28/11/2026).

Un retour « pièce trouvée » ou « pas trouvée » n'est montré comme avis vérifié que si le même client (empreinte HMAC
de l'adresse IP, jamais l'adresse) a d'abord appelé le magasin ou lui a écrit sur WhatsApp depuis DALIL, dans les 30
jours qui précèdent ; pour les contacts plus anciens, sans empreinte, le même diagnostic suffit. Un avis par client et
par jour, comme pour le score. Rien de personnel n'est affiché : la pièce, le modèle de la voiture et la date.
Les commentaires libres ne sont jamais publiés (ils servent à l'entraînement, après relecture).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ContactEvent, DiagnosisSession, Feedback, PartCategory, VehicleVariant

WINDOW = timedelta(days=30)
RECENT = 5


def _aware(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def verified_feedback(db: Session, shop_id: int) -> list[Feedback]:
    """Retours vérifiés du magasin, du plus récent au plus ancien, un par client et par jour."""
    fbs = list(db.scalars(select(Feedback).where(Feedback.shop_id == shop_id, Feedback.part_found.is_not(None))
                          .order_by(Feedback.created_at.desc(), Feedback.id.desc())))
    if not fbs:
        return []
    contacts = list(db.scalars(select(ContactEvent).where(ContactEvent.shop_id == shop_id)))
    by_hash: dict[str, list[datetime]] = {}
    by_session: dict[int, list[datetime]] = {}
    for c in contacts:
        if c.client_hash:
            by_hash.setdefault(c.client_hash, []).append(_aware(c.created_at))
        if c.session_id:
            by_session.setdefault(c.session_id, []).append(_aware(c.created_at))

    def contacted_before(times: list[datetime], at: datetime) -> bool:
        return any(at - WINDOW <= t <= at for t in times)

    out, seen = [], set()
    for f in fbs:
        at = _aware(f.created_at)
        ok = (f.client_hash and contacted_before(by_hash.get(f.client_hash, []), at)) or \
             (f.session_id and contacted_before(by_session.get(f.session_id, []), at))
        if not ok:
            continue
        voter = (f.client_hash or f"session:{f.session_id}", at.date())
        if voter in seen:
            continue
        seen.add(voter)
        out.append(f)
    return out


def reviews(db: Session, shop_id: int) -> dict:
    fbs = verified_feedback(db, shop_id)
    found = [f for f in fbs if f.part_found]
    recent = []
    for f in found[:RECENT]:
        cat = db.get(PartCategory, f.category_id) if f.category_id else None
        vehicle = None
        if f.session_id:
            sess = db.get(DiagnosisSession, f.session_id)
            v = db.get(VehicleVariant, sess.variant_id) if sess and sess.variant_id else None
            vehicle = f"{v.model.brand.name} {v.model.name}" if v else None
        recent.append({"part": cat.name_fr if cat else None, "vehicle": vehicle, "date": _aware(f.created_at).date().isoformat()})
    return {"found": len(found), "not_found": len(fbs) - len(found), "recent": recent,
            "since": _aware(fbs[-1].created_at).date().isoformat() if fbs else None}
