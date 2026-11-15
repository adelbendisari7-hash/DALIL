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
