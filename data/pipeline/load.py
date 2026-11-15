"""Chargement dans la base de connaissances (table knowledge_chunks) et export des jeux d'entraînement.

Règles (section 8) :
- aucune ligne sans licence : la licence doit être celle déclarée au registre des sources ;
- rejouable : les lignes d'une source sont remplacées, jamais dupliquées ;
- le texte d'origine est gardé dans text_original quand le texte indexé est une traduction ;
- les fiches synthétiques et les statistiques ne vont jamais dans les jeux d'entraînement étiquetés
  « réels » : le champ synthetic suit chaque exemple.
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import delete, func, select

from .common import PROCESSED, read_jsonl, write_jsonl
from .sources import SOURCES

META_KEYS = ("id", "url", "attribution", "kind", "vehicle", "categories", "family", "fault", "label_quality", "synthetic")
MAX_CHARS = 2000


class LicenseError(ValueError):
    pass


def chunk_rows(records: list[dict]) -> list[dict]:
    rows = []
    for r in records:
        spec = SOURCES.get(r["source"])
        if spec is None:
            raise LicenseError(f"source non déclarée au registre : {r['source']}")
        if not r.get("license") or r["license"] != spec.license:
            raise LicenseError(f"licence absente ou différente du registre pour {r['id']}")
        translated = bool(r.get("text_fr")) and r["lang"] != "fr"
        meta = {k: r.get(k) for k in META_KEYS}
        extra = {k: v for k, v in (r.get("meta") or {}).items() if k in ("answer_url", "rates", "tests", "fault_code", "campaign", "date")}
        rows.append({
            "source": r["source"],
            "lang": "fr" if r.get("text_fr") else r["lang"],
            "text": (r.get("text_fr") or r["text"])[:MAX_CHARS],
            "text_original": r["text"][:MAX_CHARS * 2] if translated else None,
            "meta": {**meta, **extra},
            "license": r["license"],
        })
    return rows


def load_source(db, source_id: str, path: Path) -> dict:
    from app.models import KnowledgeChunk

    records = list(read_jsonl(path))
    rows = chunk_rows(records)  # vérifie toutes les licences avant d'écrire quoi que ce soit
    db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.source == source_id))
    db.bulk_insert_mappings(KnowledgeChunk, rows)
    db.commit()
    n_fr = db.scalar(select(func.count()).select_from(KnowledgeChunk).where(KnowledgeChunk.source == source_id, KnowledgeChunk.lang == "fr"))
    return {"chunks": len(rows), "chunks_fr": n_fr}


def export_training(source_id: str, path: Path) -> int:
    """Exemples (texte -> famille de pièce) pour l'étape 7. Les statistiques et rappels de sécurité
    sans symptôme décrit par un conducteur sont exclus : ils ne ressemblent pas à une demande d'usager."""
    out = []
    for r in read_jsonl(path):
        if r["kind"] not in ("complaint", "qa", "fault_type") or not (r.get("categories") or r.get("family")):
            continue
        if r["kind"] == "qa" and not (r.get("meta") or {}).get("diagnostic", True):
            continue  # question de procédure ou de culture générale : pas un symptôme décrit
        out.append({
            "id": r["id"], "source": r["source"], "lang": r["lang"], "text": r["text"], "text_fr": r.get("text_fr"),
            "category": (r.get("categories") or [None])[0], "family": r.get("family"), "fault": r.get("fault"),
            "label_quality": r.get("label_quality"), "synthetic": r.get("synthetic", False),
            "make": (r.get("vehicle") or {}).get("make"), "license": r["license"],
        })
    return write_jsonl(PROCESSED / "train" / f"{source_id}.jsonl", out)


def summary(path: Path) -> dict:
    n = cat = fam = fault = fr = 0
    kinds: dict[str, int] = {}
    for r in read_jsonl(path):
        n += 1
        cat += bool(r.get("categories"))
        fam += bool(r.get("categories") or r.get("family"))
        fault += bool(r.get("fault"))
        fr += bool(r.get("text_fr"))
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    return {"records": n, "with_category": cat, "with_family": fam, "with_fault": fault, "translated_fr": fr, "kinds": kinds}


def dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)
