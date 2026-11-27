"""Jeux d'entraînement de CamemBERT, sur le modèle du classifieur à deux niveaux en service (27/11/2026).

    python ml/kaggle/build_camembert_sets.py        # -> data/processed/camembert/{pieces,familles}/{train,val}.jsonl
    ml/kaggle/.venv/Scripts/python ml/kaggle/kaggle_run.py dataset-camembert   # jeu Kaggle privé réduit

Pourquoi deux jeux : mélanger dans un seul classifieur des étiquettes de pièce (amorçage) et de famille (forums)
a fait reculer le modèle de référence (démo 94 -> 77 %, 18/11/2026). On garde donc le découpage qui marche :
- `pieces`  : amorçage + fiches + vrais exemples vérifiés des forums (cause confirmée) -> pièce principale ;
- `familles`: amorçage et fiches (famille de leur pièce, poids 5) + familles « fortes » de L'Argus et de
  Techniconnexion (règles SOURCE_RULES de build_training_set.py), sans les questions de procédure ou d'achat,
  + vrais exemples -> famille de pièce.
CamemBERT-familles remplace le second niveau (TF-IDF) ; CamemBERT-pièces se mesure seul et comme premier niveau.

Garde-fous : aucun texte des jeux de test (publics ou privés) ; validation = 1 exemple sur 10, choisi par le texte.
Ce dossier est le seul envoyé sur Kaggle avec data/seed et data/test : pas les messages complets des forums.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml"))
sys.path.insert(0, str(ROOT / "backend"))

import build_training_set as B  # noqa: E402
from train_family_reranker import fault_to_part, part_to_family  # noqa: E402

OUT = ROOT / "data" / "processed" / "camembert"
REELS = [ROOT / "data" / "processed" / "largus_causes_verifiees.jsonl",
         ROOT / "data" / "processed" / "techniconnexion_causes_verifiees.jsonl"]


def is_val(text: str) -> bool:
    return int(hashlib.sha1(B.norm(text).encode()).hexdigest(), 16) % 10 == 0


def reels() -> list[dict]:
    f2p = fault_to_part()
    out = []
    for p in REELS:
        for line in p.read_text(encoding="utf-8").split(chr(10)):
            if line.strip():
                r = json.loads(line)
                src = r["id"].split(":")[0]
                out.append({"text": r["text"][:B.MAX_CHARS], "label": f2p.get(r["fault"], r["part"]), "weight": 1.0,
                            "source": f"{src}_reel", "quality": "verifie"})
    return out


def write(name: str, rows: list[dict], banned: set[str]) -> dict:
    seen, kept = set(), []
    for r in rows:
        key = B.norm(r["text"])
        if not key or key in banned or key in seen:
            continue
        seen.add(key)
        kept.append(r)
    train = [r for r in kept if not is_val(r["text"])]
    val = [r for r in kept if is_val(r["text"])]
    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    for split, part in (("train", train), ("val", val)):
        with (d / f"{split}.jsonl").open("w", encoding="utf-8") as f:
            for r in part:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    stats = {"train": len(train), "val": len(val), "labels": len({r["label"] for r in kept}),
             "par_source": dict(Counter(r["source"] for r in kept))}
    (d / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


def main() -> None:
    banned = B.test_texts()
    real = reels()
    # pièces : amorçage et fiches (pièce principale de leur panne) + vrais exemples
    pieces = [{**r, "weight": 1.0} for r in B.seed_rows(1.0)] + real
    print("pièces :", write("pieces", pieces, banned))
    # familles : même contenu que le second niveau en service, étendu à Techniconnexion
    p2f = part_to_family()
    # sans bruit (demande de l'utilisateur, 27/11/2026) : étiquettes fortes seulement, et sans les questions de
    # procédure ou d'achat (« comment changer les plaquettes ») : ce n'est pas ce qu'écrit un automobiliste en panne
    train, val, _ = B.build("fort", sources={"largus_forum", "techniconnexion"}, seed_weight=5.0, diagnostic_only=True)
    fam = [{**r, "label": p2f.get(r["label"])} for r in train + val if p2f.get(r["label"])]
    fam += [{**r, "label": p2f[r["label"]]} for r in real if r["label"] in p2f]
    print("familles :", write("familles", fam, banned))


if __name__ == "__main__":
    main()
