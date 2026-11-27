"""ml/build_training_set.py : jeu commun aux variantes A et B (poids, seuil de confiance, fuite des jeux de test)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ml"))

import build_training_set as B  # noqa: E402


def _write(tmp_path, rows, source="forum_test"):
    d = tmp_path / "train"
    d.mkdir()
    with (d / f"{source}.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({"source": source, "lang": "fr", "text_fr": None, "fault": None,
                                "family": None, "synthetic": False, **r}, ensure_ascii=False) + "\n")
    return d


def test_poids_seuil_doublons_et_fuite(tmp_path):
    dev_text = json.loads((ROOT / "data" / "test" / "dev_fr_synthetique.jsonl").read_text(encoding="utf-8").split(chr(10))[0])["text"]
    rows = [
        {"id": "forum_test:1", "text": "Bruit de grincement au freinage depuis une semaine", "category": "plaquettes-avant",
         "label_quality": "solution+component"},
        {"id": "forum_test:2", "text": "Voyant moteur allumé et perte de puissance en côte", "category": "vanne-egr",
         "label_quality": "question"},                                   # trop faible pour le niveau « moyen »
        {"id": "forum_test:3", "text": "bruit de GRINCEMENT au freinage, depuis une semaine !", "category": "disques",
         "label_quality": "keyword"},                                    # doublon après normalisation
        {"id": "forum_test:4", "text": dev_text.upper(), "category": "batterie", "label_quality": "solution"},  # fuite
        {"id": "forum_test:5", "text": "Embrayage qui patine en montée", "category": "kit-embrayage",
         "label_quality": "reponses+component"},
    ]
    train, val, stats = B.build("moyen", seed_weight=1.0, train_dir=_write(tmp_path, rows))
    corpus = {r["id"]: r for r in train + val if r["source"] == "forum_test"}
    assert set(corpus) == {"forum_test:1", "forum_test:5"}
    assert corpus["forum_test:1"]["weight"] == 1.0 and corpus["forum_test:5"]["weight"] == 0.7
    assert {k: v for k, v in stats["ecartes"].items() if not k.startswith("amorçage")} == {
        "confiance < moyen": 1, "doublon": 1, "présent dans un jeu de test": 1}
    tests = B.test_texts()
    assert not any(B.norm(r["text"]) in tests for r in train + val)
    assert {r["source"] for r in train} >= {"seed", "fiche"}           # amorçage et fiches toujours présents
    assert all(r["source"] not in ("seed", "fiche") for r in val)

    train2, val2, _ = B.build("tout", train_dir=tmp_path / "train")
    assert any(r.get("id") == "forum_test:2" and r["weight"] == 0.2 for r in train2 + val2)


def test_validation_stable():
    assert [B.is_val(f"forum_test:{i}") for i in range(200)] == [B.is_val(f"forum_test:{i}") for i in range(200)]
    assert 5 <= sum(B.is_val(f"forum_test:{i}") for i in range(200)) <= 40


def test_regle_largus_famille_et_poids_mesures(tmp_path):
    """L'Argus : seule la famille est gardée, pour les niveaux validés par la relecture, avec le poids mesuré."""
    rows = [
        {"id": "largus_forum:1", "text": "La pédale de frein s'enfonce jusqu'au plancher", "category": "maitre-cylindre",
         "family": "freinage", "label_quality": "question+component"},
        {"id": "largus_forum:2", "text": "Le moteur chauffe et le ventilateur ne tourne pas", "category": "motoventilateur",
         "family": "refroidissement", "label_quality": "auteur"},          # niveau écarté par la relecture
        {"id": "largus_forum:3", "text": "Ma batterie se vide en une nuit sans raison", "category": "batterie",
         "family": "electricite", "label_quality": "auteur+component"},
    ]
    train, val, stats = B.build("moyen", seed_weight=1.0, train_dir=_write(tmp_path, rows, "largus_forum"))
    got = {r["id"]: r for r in train + val if r["source"] == "largus_forum"}
    assert set(got) == {"largus_forum:1", "largus_forum:3"}
    assert got["largus_forum:1"]["label"] == "freinage" and got["largus_forum:1"]["weight"] == 0.82
    assert got["largus_forum:3"]["label"] == "electricite" and got["largus_forum:3"]["weight"] == 0.75
    assert stats["ecartes"]["niveau écarté par la relecture"] == 1
    fort, _, _ = B.build("fort", seed_weight=1.0, train_dir=tmp_path / "train")   # 0,75 < 0,8 : écarté en « fort »
    assert not any(r.get("id") == "largus_forum:3" for r in fort)


def test_regle_techniconnexion_double_accord(tmp_path):
    """Techniconnexion : seules les familles qui s'accordent avec la section ET avec la question sont gardées."""
    rows = [
        {"id": "techniconnexion:1", "text": "Bruit au freinage, les plaquettes sifflent", "category": "plaquettes-avant",
         "family": "freinage", "label_quality": "auteur+domaine+accord"},
        {"id": "techniconnexion:2", "text": "Le moteur cale au ralenti", "category": "vanne-egr",
         "family": "gestion-moteur", "label_quality": "reponses+domaine"},       # sans accord avec la question
        {"id": "techniconnexion:3", "text": "Fuite d'eau sous la pompe à eau", "category": "pompe-eau",
         "family": "refroidissement", "label_quality": "solution+domaine+accord"},
    ]
    train, val, _ = B.build("moyen", seed_weight=1.0, train_dir=_write(tmp_path, rows, "techniconnexion"))
    got = {r["id"]: r for r in train + val if r["source"] == "techniconnexion"}
    assert set(got) == {"techniconnexion:1", "techniconnexion:3"}
    assert got["techniconnexion:1"]["label"] == "freinage" and got["techniconnexion:1"]["weight"] == 0.82
    fort, _, _ = B.build("fort", seed_weight=1.0, train_dir=tmp_path / "train")   # 0,73 < 0,8 : écarté en « fort »
    assert not any(r.get("id") == "techniconnexion:3" for r in fort)
