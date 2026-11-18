"""ml/build_training_set.py : jeu commun aux variantes A et B (poids, seuil de confiance, fuite des jeux de test)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ml"))

import build_training_set as B  # noqa: E402


def _write(tmp_path, rows):
    d = tmp_path / "train"
    d.mkdir()
    with (d / "largus_forum.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({"source": "largus_forum", "lang": "fr", "text_fr": None, "fault": None,
                                "family": None, "synthetic": False, **r}, ensure_ascii=False) + "\n")
    return d


def test_poids_seuil_doublons_et_fuite(tmp_path):
    dev_text = json.loads((ROOT / "data" / "test" / "dev_fr_synthetique.jsonl").read_text(encoding="utf-8").splitlines()[0])["text"]
    rows = [
        {"id": "largus_forum:1", "text": "Bruit de grincement au freinage depuis une semaine", "category": "plaquettes-avant",
         "label_quality": "solution+component"},
        {"id": "largus_forum:2", "text": "Voyant moteur allumé et perte de puissance en côte", "category": "vanne-egr",
         "label_quality": "question"},                                   # trop faible pour le niveau « moyen »
        {"id": "largus_forum:3", "text": "bruit de GRINCEMENT au freinage, depuis une semaine !", "category": "disques",
         "label_quality": "keyword"},                                    # doublon après normalisation
        {"id": "largus_forum:4", "text": dev_text.upper(), "category": "batterie", "label_quality": "solution"},  # fuite
        {"id": "largus_forum:5", "text": "Embrayage qui patine en montée", "category": "kit-embrayage",
         "label_quality": "reponses+component"},
    ]
    train, val, stats = B.build("moyen", seed_weight=1.0, train_dir=_write(tmp_path, rows))
    corpus = {r["id"]: r for r in train + val if r["source"] == "largus_forum"}
    assert set(corpus) == {"largus_forum:1", "largus_forum:5"}
    assert corpus["largus_forum:1"]["weight"] == 1.0 and corpus["largus_forum:5"]["weight"] == 0.7
    assert {k: v for k, v in stats["ecartes"].items() if not k.startswith("amorçage")} == {
        "confiance < moyen": 1, "doublon": 1, "présent dans un jeu de test": 1}
    tests = B.test_texts()
    assert not any(B.norm(r["text"]) in tests for r in train + val)
    assert {r["source"] for r in train} >= {"seed", "fiche"}           # amorçage et fiches toujours présents
    assert all(r["source"] not in ("seed", "fiche") for r in val)

    train2, val2, _ = B.build("tout", train_dir=tmp_path / "train")
    assert any(r.get("id") == "largus_forum:2" and r["weight"] == 0.2 for r in train2 + val2)


def test_validation_stable():
    assert [B.is_val(f"largus_forum:{i}") for i in range(200)] == [B.is_val(f"largus_forum:{i}") for i in range(200)]
    assert 5 <= sum(B.is_val(f"largus_forum:{i}") for i in range(200)) <= 40
