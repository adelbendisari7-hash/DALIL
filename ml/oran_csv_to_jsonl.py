"""Convertit les fiches d'annotation des mécaniciens d'Oran (CSV) en jeu de test (JSONL) pour ml/evaluate.py.

    python ml/oran_csv_to_jsonl.py data/test/modele_annotation_oran.csv            # -> data/test/oran_test.jsonl
    python ml/oran_csv_to_jsonl.py fiches.csv --out data/test/oran_test.jsonl --check   # contrôle seulement

Colonnes attendues (séparateur ;) : id ; date ; mecanicien ; marque ; modele ; motorisation ; annee ;
symptome_mots_du_client ; codes_obd ; cause_trouvee ; pieces_changees ; commentaire.

- `pieces_changees` : une ou plusieurs pièces séparées par « , » ou « ; » ou « | », en slug
  (`plaquettes-avant`) ou en toutes lettres (« plaquettes avant ») ; elles deviennent `expect`.
  « hors sujet » ou « aucune » marque une entrée qui doit recevoir « je ne sais pas ».
- Les lignes d'exemple (commentaire contenant « exemple ») sont ignorées.
- Une ligne invalide (pièce inconnue, symptôme vide, identifiant en double) est signalée et n'est pas écrite :
  le jeu de test ne contient que des cas vérifiés.

Le jeu produit est à figer (commit + empreinte SHA-256 notée dans le mémoire) avant tout réglage : il ne sert
jamais à entraîner ni à régler un seuil (data/test/README.md).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

OUT_OF_SCOPE = {"hors sujet", "hors-sujet", "aucune", "aucun", "rien"}


def _slugs() -> dict[str, str]:
    """Sous-familles de la taxonomie : slug -> slug, plus nom et synonymes normalisés -> slug."""
    from app.services.diagnosis.normalize import normalize

    data = json.loads((ROOT / "data" / "seed" / "part_categories.json").read_text(encoding="utf-8"))
    out: dict[str, str] = {}

    def walk(nodes):
        for n in nodes:
            if n.get("children"):
                walk(n["children"])
                continue
            out[n["slug"]] = n["slug"]
            for name in [n.get("name_fr", "")] + list(n.get("synonyms", [])):
                if name:
                    out[normalize(name)] = n["slug"]

    walk(data["families"])
    return out


warnings: list[str] = []


def _variant_known(variant: list) -> bool:
    from app.db import SessionLocal
    from app.seed import _variant

    if not variant[3]:
        return False
    with SessionLocal() as db:
        return _variant(db, *variant) is not None


def _fuzzy(label: str) -> str | None:
    """Sous-famille la plus proche (recherche du catalogue, tolérante aux fautes), ou None."""
    from app.db import SessionLocal
    from app.services.catalog import resolve_category

    with SessionLocal() as db:
        cat = resolve_category(db, label)
        return cat.slug if cat is not None and cat.parent_id is not None else None


def convert(text: str) -> tuple[list[dict], list[str]]:
    """Rend (cas valides, erreurs « ligne N : raison »)."""
    from app.services.diagnosis.normalize import normalize

    slugs = _slugs()
    rows = csv.DictReader(io.StringIO(text.lstrip("﻿")), delimiter=";")
    cases, errors, seen = [], [], set()
    warnings.clear()
    for line, r in enumerate(rows, start=2):
        r = {(k or "").strip(): (v or "").strip() for k, v in r.items()}
        if "exemple" in r.get("commentaire", "").lower():
            continue
        cid, text_ = r.get("id", ""), r.get("symptome_mots_du_client", "")
        if not cid:
            errors.append(f"ligne {line} : identifiant manquant")
            continue
        if cid in seen:
            errors.append(f"ligne {line} : identifiant en double ({cid})")
            continue
        if not text_ and not r.get("codes_obd"):
            errors.append(f"ligne {line} ({cid}) : ni symptôme ni code OBD")
            continue
        case = {"id": cid, "text": text_, "dtc": [c.upper() for c in re.split(r"[\s,;]+", r.get("codes_obd", "")) if c],
                "mechanic": r.get("mecanicien") or None, "date": r.get("date") or None}
        pieces = [p.strip() for p in re.split(r"[,;|]", r.get("pieces_changees", "")) if p.strip()]
        if not pieces or {normalize(p) for p in pieces} <= OUT_OF_SCOPE:
            if pieces:
                case["expect_status"] = "unknown"
            else:
                errors.append(f"ligne {line} ({cid}) : pièce changée manquante (ou « hors sujet »)")
                continue
        else:
            expect, unknown = [], []
            for p in pieces:
                slug = slugs.get(p) or slugs.get(normalize(p))
                if not slug and (guess := _fuzzy(p)):
                    slug = guess  # écriture approchée : acceptée mais signalée, c'est une réponse de référence
                    warnings.append(f"ligne {line} ({cid}) : « {p} » interprété comme {guess}, à vérifier")
                (expect if slug else unknown).append(slug or p)
            if unknown:
                errors.append(f"ligne {line} ({cid}) : pièce inconnue de la taxonomie : {', '.join(unknown)}")
                continue
            case["expect"] = sorted(set(expect))
        if r.get("marque") and r.get("modele"):
            try:
                year = int(r.get("annee") or 0) or None
            except ValueError:
                errors.append(f"ligne {line} ({cid}) : année illisible ({r.get('annee')})")
                continue
            variant = [r["marque"], r["modele"], r.get("motorisation", ""), year]
            if _variant_known(variant):
                case["variant"] = variant
            else:  # véhicule absent du référentiel : le cas reste valable, diagnostiqué sans véhicule
                warnings.append(f"ligne {line} ({cid}) : véhicule inconnu du référentiel, gardé sans véhicule : "
                                f"{' '.join(str(x) for x in variant if x)}")
        seen.add(cid)
        cases.append(case)
    return cases, errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "test" / "oran_test.jsonl")
    ap.add_argument("--check", action="store_true", help="contrôler sans écrire")
    args = ap.parse_args(argv)

    cases, errors = convert(args.csv.read_text(encoding="utf-8-sig"))
    for w in warnings:
        print("ATTENTION", w)
    for e in errors:
        print("ERREUR", e)
    print(f"{len(cases)} cas valides, {len(errors)} lignes refusées")
    if args.check or not cases:
        return 1 if errors else 0
    body = "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases)
    args.out.write_text(body, encoding="utf-8")
    print(f"écrit : {args.out} (SHA-256 {hashlib.sha256(body.encode()).hexdigest()[:16]}…, à noter dans le mémoire)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
