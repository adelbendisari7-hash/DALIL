"""Modèle de langage dans la chaîne (étape 8) : repli, cache, réponses rejetées, mode différé.

Un faux fournisseur remplace l'appel réseau : aucune dépendance à llama.cpp ni à un service payant."""
import json
from pathlib import Path

import pytest

from app.config import get_settings
from app.seed import _variant
from app.services.diagnosis import llm as llm_mod
from app.services.diagnosis.pipeline import DiagnosisInput, run_diagnosis

API = "/api/v1"
CASES = json.loads((Path(get_settings().data_dir) / "seed" / "demo_cases.json").read_text(encoding="utf-8"))["cases"]
TEXT = "quand je freine j'entends un frottement métallique à l'avant"


class Fake:
    """Remplace OpenAICompatProvider.complete_json ; compte les appels."""

    def __init__(self, behaviour="keep"):
        self.behaviour, self.calls = behaviour, 0

    def __call__(self, system, user):
        self.calls += 1
        if self.behaviour == "timeout":
            raise TimeoutError("le serveur n'a pas répondu")
        cands = [c["slug"] for c in json.loads(user)["candidats"]]
        if self.behaviour == "hors_liste":
            return {"ranking": [{"fault": "panne-inventee", "confidence": 0.9, "explanation": "x",
                                 "reference": "FICTIF-123"}]}
        if self.behaviour == "inverse":
            cands = cands[::-1]
        return {"ranking": [{"fault": s, "confidence": 0.8 - 0.2 * i, "explanation": f"explication {s}"}
                            for i, s in enumerate(cands[:3])]}


@pytest.fixture()
def fake(monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "llm_provider", "openai_compat")
    monkeypatch.setattr(s, "llm_base_url", "http://faux")
    monkeypatch.setattr(llm_mod.budget, "count", 0)
    llm_mod.cache.data.clear()
    holder = {}

    def install(behaviour="keep"):
        holder["fake"] = Fake(behaviour)
        fk = holder["fake"]
        monkeypatch.setattr(llm_mod.OpenAICompatProvider, "complete_json", lambda self, system, user: fk(system, user))
        return holder["fake"]

    yield install
    llm_mod.cache.data.clear()


def _run(db, text=TEXT, **kw):
    return run_diagnosis(db, DiagnosisInput(text=text), **kw)[0]


def test_sans_modele_de_langage_l_etat_est_off(db):
    assert _run(db)["llm"] == "off"


def test_modele_utilise_et_explication_recopiee(db, fake):
    f = fake("keep")
    r = _run(db)
    assert r["llm"] == "used" and f.calls == 1
    assert r["causes"][0]["explanation"].startswith("explication ")


def test_repli_quand_le_modele_ne_repond_pas(db, fake):
    base = _run(db)  # sans modèle (off) : classement du classifieur
    fake("timeout")
    r = _run(db)
    assert r["llm"] == "fallback"
    assert r["status"] in ("ok", "clarify") and r["causes"]
    assert [c["fault"] for c in r["causes"]] == [c["fault"] for c in base["causes"]]
    assert all(c["explanation"] is None for c in r["causes"])


def test_reponse_hors_liste_rejetee_et_aucune_reference_generee(db, fake):
    fake("hors_liste")
    r = _run(db)
    assert r["llm"] == "fallback"
    assert "panne-inventee" not in {c["fault"] for c in r["causes"]}
    assert "FICTIF-123" not in json.dumps(r)


def test_cache_une_question_identique_ne_coute_qu_un_appel(db, fake):
    f = fake("keep")
    assert _run(db)["llm"] == "used"
    assert _run(db)["llm"] == "cached"
    assert f.calls == 1
    assert _run(db, text=TEXT + " et une odeur de brûlé")["llm"] == "used"  # autre question : nouvel appel
    assert f.calls == 2


def test_cache_expire(db, fake, monkeypatch):
    f = fake("keep")
    _run(db)
    monkeypatch.setattr(get_settings(), "llm_cache_ttl", -1)
    assert _run(db)["llm"] == "used"
    assert f.calls == 2


def test_plafond_mensuel_d_appels(db, fake, monkeypatch):
    f = fake("keep")
    monkeypatch.setattr(get_settings(), "llm_monthly_call_cap", 0)
    assert _run(db)["llm"] == "fallback" and f.calls == 0


def test_le_classifieur_seul_n_appelle_pas_le_modele(db, fake):
    f = fake("keep")
    assert _run(db, mode="classifier")["llm"] == "off" and f.calls == 0


def test_mode_differe_reponse_immediate_puis_affinage(client, fake):
    f = fake("inverse")
    r = client.post(f"{API}/diagnosis", json={"text": TEXT, "defer_llm": True}).json()
    assert r["llm"] == "pending" and r["causes"], "le résultat du classifieur est rendu tout de suite"
    # Le client de test exécute la tâche d'arrière-plan avant de rendre la main : le résultat est déjà affiné.
    again = client.get(f"{API}/diagnosis/{r['session_id']}").json()
    assert again["llm"] == "used" and f.calls == 1
    assert again["causes"][0]["fault"] != r["causes"][0]["fault"]  # l'ordre inverse du faux modèle a été appliqué


def test_mode_differe_sans_modele_repond_normalement(client):
    r = client.post(f"{API}/diagnosis", json={"text": TEXT, "defer_llm": True}).json()
    assert r["llm"] == "off" and r["causes"]


def test_mode_differe_le_modele_en_panne_ne_laisse_pas_pending(client, fake):
    fake("timeout")
    r = client.post(f"{API}/diagnosis", json={"text": TEXT, "defer_llm": True}).json()
    assert client.get(f"{API}/diagnosis/{r['session_id']}").json()["llm"] == "fallback"


@pytest.mark.parametrize("case", CASES, ids=[c["text"][:40] or ",".join(c.get("dtc", [])) for c in CASES])
def test_cas_de_demonstration_en_mode_complet_avec_modele(db, fake, case):
    """Le critère de fin de l'étape 8 tient aussi quand le modèle de langage est dans la chaîne."""
    fake("keep")
    vid = _variant(db, *case["variant"]).id if case.get("variant") else None
    r, _ = run_diagnosis(db, DiagnosisInput(text=case["text"], variant_id=vid, dtc_codes=case.get("dtc", [])))
    if "expect_status" in case:
        assert r["status"] == case["expect_status"]
        return
    assert r["status"] in ("ok", "clarify"), r.get("message")
    parts = {p for c in r["causes"] for p in [c["part"]["slug"]] + [o["slug"] for o in c["other_parts"]]}
    assert parts & set(case["expect_parts"])
    assert len(r["causes"]) <= 3
