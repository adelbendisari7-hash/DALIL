"""Critère de fin de l'étape 8 : les 20 cas de démonstration passent ; hors sujet -> « je ne sais pas »."""
import json
from pathlib import Path

import pytest

from app.config import get_settings
from app.seed import _variant
from app.services.diagnosis.pipeline import DiagnosisInput, run_diagnosis

CASES = json.loads((Path(get_settings().data_dir) / "seed" / "demo_cases.json").read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", CASES, ids=[c["text"][:40] or ",".join(c.get("dtc", [])) for c in CASES])
def test_demo_case(db, case):
    vid = _variant(db, *case["variant"]).id if case.get("variant") else None
    r, _ = run_diagnosis(db, DiagnosisInput(text=case["text"], variant_id=vid, dtc_codes=case.get("dtc", [])))
    if "expect_status" in case:
        assert r["status"] == case["expect_status"]
        return
    assert r["status"] in ("ok", "clarify"), r.get("message")
    parts = {p for c in r["causes"] for p in [c["part"]["slug"]] + [o["slug"] for o in c["other_parts"]]}
    assert parts & set(case["expect_parts"]), [c["fault"] for c in r["causes"]]
    assert len(r["causes"]) <= 3


# --- Description trop courte (17/11/2026) : « frein » seul donnait 78 % de confiance sans question --------------

def test_mot_seul_pas_de_resultat_sur(db):
    from app.services.diagnosis.pipeline import informative_words

    assert informative_words("frein") == 1
    assert informative_words("ma voiture a un problème") == 0
    assert informative_words("ça grince quand je freine") == 2
    for text in ["frein", "batterie", "bruit", "fumée"]:
        r, _ = run_diagnosis(db, DiagnosisInput(text=text))
        # soit des questions de précision, soit une demande de description plus précise : jamais un résultat sûr
        assert (r["status"] == "clarify" and r["questions"]) or (r["status"] == "unknown" and not r["causes"]), (text, r["status"])


def test_mot_seul_puis_reponse_donne_un_resultat(db):
    r, _ = run_diagnosis(db, DiagnosisInput(text="batterie"))
    if r["status"] != "clarify":
        pytest.skip("pas de question pour ce mot avec cet index")
    q = r["questions"][0]
    r2, _ = run_diagnosis(db, DiagnosisInput(text="batterie", answers={q["id"]: 0}))
    assert r2["status"] in ("ok", "clarify") and r2["causes"]  # une réponse donnée : plus de blocage


def test_mot_seul_avec_code_obd_reste_un_diagnostic(db):
    r, _ = run_diagnosis(db, DiagnosisInput(text="voyant", dtc_codes=["P0420"]))
    assert r["status"] in ("ok", "clarify") and r["causes"]
