"""Retours des utilisateurs -> vrais exemples candidats pour l'entraînement (même format que les forums).

    cd backend
    python -m app.export_retours                    # data/processed/retours_dalil.jsonl
    python -m app.export_retours --out autre.jsonl

Sur la page de résultat, « Oui » confirme la première cause proposée ; « Non » demande la pièce réellement en cause
(et, en option, ce que le mécanicien a trouvé). Chaque retour avec une pièce devient une ligne
{id, text, part, fault, correct, verifie: false}, où `fault` est la panne type dont cette pièce est la pièce principale
(parmi celles proposées au conducteur s'il y en a plusieurs).

- **À vérifier avant tout entraînement**, comme les causes des forums : un « Oui » peut confirmer par politesse,
  un « Non » peut nommer une pièce changée sans succès. Une fois relues, les lignes justes vont dans
  `train_baseline.py --exemples-reels`.
- **Données personnelles** : numéros et adresses e-mail masqués dans le texte et le commentaire ; ni l'utilisateur
  ni l'empreinte du client ne sont exportés. Le fichier reste hors git (data/processed/).
- **Rejouable** : un exemple par diagnostic (le dernier retour l'emporte), même sortie à base égale.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import DiagnosisSession, Fault, FaultPart, Feedback, PartCategory

PHONE = re.compile(r"(?:\+|00)?\d[\d .\-/]{7,}\d")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
MIN_WORDS = 3


def scrub(text: str) -> str:
    return PHONE.sub("[numéro]", EMAIL.sub("[e-mail]", text or "")).strip()


def principal_faults(db: Session) -> dict[str, list[str]]:
    """pièce -> pannes types dont elle est la pièce principale (poids 1,0 dans data/seed/faults.json)."""
    out: dict[str, list[str]] = {}
    rows = db.execute(select(PartCategory.slug, Fault.slug).join(FaultPart, FaultPart.category_id == PartCategory.id)
                      .join(Fault, Fault.id == FaultPart.fault_id).where(FaultPart.weight >= 1.0).order_by(Fault.id))
    for part, fault in rows:
        out.setdefault(part, []).append(fault)
    return out


def export(db: Session) -> tuple[list[dict], dict]:
    principal = principal_faults(db)
    cats = {c.id: c.slug for c in db.scalars(select(PartCategory))}
    latest: dict[int, Feedback] = {}
    for fb in db.scalars(select(Feedback).where(Feedback.session_id.is_not(None), Feedback.diagnosis_correct.is_not(None))
                         .order_by(Feedback.id)):
        latest[fb.session_id] = fb   # le dernier retour sur un diagnostic l'emporte
    rows, stats = [], {"retours": len(latest), "sans_piece": 0, "texte_trop_court": 0, "panne_ambigue": 0, "exportes": 0}
    for sid, fb in sorted(latest.items()):
        sess = db.get(DiagnosisSession, sid)
        text = scrub(sess.input_text if sess else "")
        if len(text.split()) < MIN_WORDS:
            stats["texte_trop_court"] += 1
            continue
        causes = (sess.result_json or {}).get("causes", [])
        part = cats.get(fb.category_id)
        if fb.diagnosis_correct and not part and causes:   # « Oui » d'un ancien site, sans pièce : la première cause
            part = causes[0].get("part", {}).get("slug")
        if not part:
            stats["sans_piece"] += 1
            continue
        candidates = principal.get(part, [])
        shown = [c.get("fault") for c in causes]
        if fb.diagnosis_correct and causes and causes[0].get("part", {}).get("slug") == part:
            fault = causes[0].get("fault")
        elif len(candidates) == 1:
            fault = candidates[0]
        else:
            among = [f for f in candidates if f in shown]
            fault = among[0] if len(among) == 1 else None
        if fault is None:
            stats["panne_ambigue"] += 1   # gardé quand même : la pièce suffit au modèle de familles et à la relecture
        rows.append({"id": f"retour:{sid}", "text": text, "part": part, "fault": fault,
                     "correct": bool(fb.diagnosis_correct), "comment": scrub(fb.comment or "") or None,
                     "model_version": sess.model_version if sess else None, "verifie": False})
        stats["exportes"] += 1
    return rows, stats


def main() -> None:
    from .db import SessionLocal

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(Path(get_settings().data_dir) / "processed" / "retours_dalil.jsonl"))
    args = ap.parse_args()
    with SessionLocal() as db:
        rows, stats = export(db)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"{out} : {stats}")


if __name__ == "__main__":
    main()
