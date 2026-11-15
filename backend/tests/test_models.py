"""Étape 7 : classifieurs (cible panne ou pièce), banc d'évaluation, jeu d'affinage, carnets Kaggle."""
import json
import sys
from pathlib import Path

import joblib
import pytest
from sqlalchemy import select

from app.config import get_settings
from app.models import Fault, PartCategory
from app.services.diagnosis import pipeline as P
from app.services.diagnosis.classifier import FaultClassifier, build_pipeline, load_classifier
from app.services.diagnosis.llm import SYSTEM_PROMPT

ROOT = Path(get_settings().data_dir).parent
sys.path.insert(0, str(ROOT / "ml"))


def _maps(db):
    faults = {f.slug: f for f in db.scalars(select(Fault))}
    cats = {c.id: c for c in db.scalars(select(PartCategory))}
    return faults, cats


def test_pieces_vers_pannes(db):
    faults, cats = _maps(db)
    out = P.parts_to_faults({"plaquettes-avant": 0.9, "batterie": 0.1}, faults, cats)
    assert max(out, key=out.get) == "plaquettes-usees"
    assert out["batterie-faible"] > 0
    # étiquette de niveau 1 (famille) : répartie sur les pannes de la famille
    fam = P.parts_to_faults({"refroidissement": 1.0}, faults, cats)
    assert {"thermostat-bloque", "pompe-eau-hs", "fuite-refroidissement"} <= set(fam)
    assert "plaquettes-usees" not in fam


def test_chargement_avec_cible(tmp_path):
    pipe = build_pipeline().fit(["ça grince au freinage", "la batterie est à plat", "frein qui siffle", "batterie morte"],
                                ["plaquettes-avant", "batterie", "plaquettes-avant", "batterie"])
    joblib.dump({"pipeline": pipe, "target": "part", "version": "test-v1"}, tmp_path / "m.joblib")
    m = load_classifier(tmp_path / "m.joblib")
    assert isinstance(m, FaultClassifier) and m.target == "part" and m.version == "test-v1"
    joblib.dump(pipe, tmp_path / "ancien.joblib")  # ancien format : pipeline seul = cible panne
    assert load_classifier(tmp_path / "ancien.joblib").target == "fault"


def test_chaine_avec_classifieur_de_pieces(db, tmp_path, monkeypatch):
    texts, labels = [], []
    for line in (ROOT / "data" / "seed" / "diagnosis_examples_fr.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        texts.append(r["text"])
        labels.append(r["fault"])
    f2p = {f["slug"]: max(f["parts"].items(), key=lambda x: x[1])[0]
           for f in json.loads((ROOT / "data" / "seed" / "faults.json").read_text(encoding="utf-8"))["faults"]}
    model = FaultClassifier(build_pipeline().fit(texts, [f2p[x] for x in labels]), target="part")
    monkeypatch.setattr(P, "get_classifier", lambda: model)
    r, _ = P.run_diagnosis(db, P.DiagnosisInput(text="ça grince fort quand je freine, bruit de métal"), mode="classifier")
    assert r["causes"] and r["causes"][0]["part"]["slug"] in ("plaquettes-avant", "disques-frein")


def test_banc_evaluation(db):
    from evaluate import load_cases, ranked_parts, run

    cases = load_cases(ROOT / "data" / "test" / "dev_fr_synthetique.jsonl")
    assert len(cases) == 55 and sum(c.get("expect_status") == "unknown" for c in cases) == 5
    assert len(load_cases(ROOT / "data" / "seed" / "demo_cases.json")) == 20
    res = run(db, cases[:6] + cases[-2:], "full")
    assert res["n"] == 6 and res["n_hors_sujet"] == 2
    assert 0 <= res["top1"] <= res["top3"] <= 1
    assert ranked_parts({"causes": [{"part": {"slug": "a"}}, {"part": {"slug": "a"}}, {"part": {"slug": "b"}}]}) == ["a", "b"]


def test_jeu_d_affinage(db, monkeypatch):
    import build_llm_dataset as B

    monkeypatch.setattr(B, "OUT", Path(get_settings().data_dir).parent / "backend" / ".pytest_llm")
    stats = B.build()
    assert stats["train"] > 100 and stats["val"] > 5
    row = json.loads((B.OUT / "val.jsonl").read_text(encoding="utf-8").splitlines()[0])
    system, user, assistant = row["messages"]
    assert system["content"] == SYSTEM_PROMPT
    cands = {c["slug"] for c in json.loads(user["content"])["candidats"]}
    ranking = json.loads(assistant["content"])["ranking"]
    assert len(cands) == B.N_CANDIDATES and ranking[0]["fault"] in cands
    assert all(r["fault"] in cands for r in ranking)
    # aucun cas des jeux de test dans l'affinage
    test_texts = {c["text"] for c in (json.loads(l) for l in (ROOT / "data" / "test" / "dev_fr_synthetique.jsonl").read_text(encoding="utf-8").splitlines())}
    train_texts = {json.loads(json.loads(l)["messages"][1]["content"])["description"]
                   for l in (B.OUT / "train.jsonl").read_text(encoding="utf-8").splitlines()}
    assert not test_texts & train_texts


@pytest.mark.parametrize("name", ["01_traduction", "02_encodeur_fr", "02_encodeur_enfr", "03_lora_llm", "04_fusion_gguf"])
def test_carnets_kaggle_a_jour_et_valides(name):
    import importlib.util

    spec = importlib.util.spec_from_file_location("mk", ROOT / "ml" / "kaggle" / "make_notebooks.py")
    mk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mk)
    cells = mk.NOTEBOOKS[name]
    on_disk = json.loads((ROOT / "ml" / "kaggle" / f"{name}.ipynb").read_text(encoding="utf-8"))
    assert on_disk == mk.notebook(cells), "carnet périmé : relancer python ml/kaggle/make_notebooks.py"
    for c in on_disk["cells"]:
        if c["cell_type"] == "code":
            compile("".join(l for l in c["source"] if not l.lstrip().startswith("!")), name, "exec")
