"""Import des codes OBD-II génériques d'OBDex (CC0) dans la table dtc_codes, étape 3.

    python data/scripts/import_obdex.py --json chemin/vers/obdex.json
    python data/scripts/import_obdex.py --json obdex.json --translate   # traduction automatique en français

Source : https://github.com/foerbsnavi/OBDex (télécharger le JSON depuis le dépôt).
- Les codes déjà rédigés en français par l'équipe (source = dalil-seed) ne sont jamais écrasés.
- Sans --translate, le titre anglais est stocké dans title_en et title_fr reçoit le préfixe
  « [à traduire] » : à traduire ensuite sur GPU (Kaggle) avec un modèle ouvert, puis relire.
- --translate utilise Helsinki-NLP/opus-mt-en-fr (transformers requis).
Le script est rejouable : il met à jour les codes existants d'origine OBDex.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.db import SessionLocal  # noqa: E402
from app.models import DtcCode  # noqa: E402

KEYS_CODE = ("code", "dtc", "id")
KEYS_TITLE = ("description", "title", "name", "definition")


def _first(d: dict, keys) -> str | None:
    for k in keys:
        if d.get(k):
            return d[k] if isinstance(d[k], str) else json.dumps(d[k], ensure_ascii=False)
    return None


def _as_list(v) -> list[str]:
    if not v:
        return []
    if isinstance(v, str):
        return [x.strip() for x in v.split(";") if x.strip()]
    return [str(x) for x in v]


def iter_records(data) -> list[dict]:
    if isinstance(data, dict):
        if "codes" in data:
            data = data["codes"]
        else:
            data = [{"code": k, **(v if isinstance(v, dict) else {"description": v})} for k, v in data.items()]
    return [r for r in data if isinstance(r, dict)]


def make_translator():
    from transformers import pipeline  # import paresseux : dépendance optionnelle

    tr = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
    return lambda texts: [o["translation_text"] for o in tr(texts, batch_size=16)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--translate", action="store_true")
    args = ap.parse_args()
    records = iter_records(json.loads(Path(args.json).read_text(encoding="utf-8")))
    translate = make_translator() if args.translate else None
    created = updated = skipped = 0
    with SessionLocal() as db:
        batch = []
        for r in records:
            code = (_first(r, KEYS_CODE) or "").strip().upper()
            title_en = _first(r, KEYS_TITLE)
            if not code or not title_en or code[0] not in "PCBU":
                continue
            row = db.get(DtcCode, code)
            if row and row.source == "dalil-seed":
                skipped += 1
                continue
            if row is None:
                row = DtcCode(code=code, source="obdex")
                db.add(row)
                created += 1
            else:
                updated += 1
            row.title_en = title_en[:255]
            row.causes = _as_list(r.get("causes") or r.get("common_causes"))
            row.symptoms = _as_list(r.get("symptoms"))
            row.description = r.get("repair") if isinstance(r.get("repair"), str) else None
            batch.append(row)
        if translate:
            for i in range(0, len(batch), 64):
                chunk = batch[i:i + 64]
                for row, fr in zip(chunk, translate([b.title_en for b in chunk])):
                    row.title_fr = fr[:255]
        else:
            for row in batch:
                row.title_fr = f"[à traduire] {row.title_en}"[:255]
        db.commit()
    print(f"OBDex : {created} créés, {updated} mis à jour, {skipped} codes rédigés par l'équipe conservés")


if __name__ == "__main__":
    main()
