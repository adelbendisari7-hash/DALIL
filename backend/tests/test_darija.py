"""Darija en lettres latines ou arabes -> français (section 6.1, étape 1 de la chaîne)."""
import pytest

from app.services.diagnosis.darija import to_french
from app.services.diagnosis.pipeline import DiagnosisInput, run_diagnosis


@pytest.mark.parametrize("text,expected,lang", [
    ("el frein ysoni", "le frein fait du bruit", "dz"),
    ("tomobil ma tdemarich", "voiture ne demarre pas", "dz"),
    ("el ma ta3 radiateur yan9as", "liquide de refroidissement de radiateur baisse", "dz"),
    ("الموتور يسخن بزاف", "moteur chauffe surchauffe beaucoup", "ar"),
    ("الطوموبيل ما تديماريش في الصباح", "voiture ne demarre pas dans matin", "ar"),
])
def test_traduction(text, expected, lang):
    assert to_french(text) == (expected, lang)


@pytest.mark.parametrize("text", [
    "ça grince quand je freine, j'ai fini par m'inquiéter",   # « fini » existe aussi en français
    "la clim souffle chaud",
    "Le moteur chauffe sur autoroute",
])
def test_francais_inchange(text):
    assert to_french(text) == (text, "fr")


def test_negation_ma_jamais_traduite_seule():
    # « ma » est la négation : seul, il ne doit pas devenir « eau ».
    assert "eau" not in to_french("ma tdemarich ghir f sbah")[0]


def test_mots_arabes_inconnus_retires():
    fr, lang = to_french("الموتور يسخن والسلام عليكم")
    assert lang == "ar" and "moteur" in fr and not any("؀" <= c <= "ۿ" for c in fr)


@pytest.mark.parametrize("text,famille", [
    ("el moteur ysakhen bezaf", "refroidissement"),
    ("tomobil ma tdemarich f sbah", "electricite"),
    ("الفرامل تصفر كي نفريني", "freinage"),
])
def test_diagnostic_en_darija(db, text, famille):
    r, _ = run_diagnosis(db, DiagnosisInput(text=text))
    assert r["status"] in ("ok", "clarify"), r.get("message")
    assert r["understood"]  # ce que DALIL a compris, montré à l'utilisateur
    systems = {c["system"] for c in r["causes"]}
    assert famille in systems or famille in {c["part"]["family"] for c in r["causes"] if "family" in c["part"]}, systems


def test_arabe_incompris_message_clair(db):
    r, _ = run_diagnosis(db, DiagnosisInput(text="السلام عليكم"))
    assert r["status"] == "unknown" and "darija en lettres latines" in r["message"]


@pytest.mark.parametrize("text", ["chhal soum el gasoil lyoum", "wach rak khouya labas", "صباح الخير كيراك"])
def test_hors_sujet_en_darija_refuse(db, text):
    r, _ = run_diagnosis(db, DiagnosisInput(text=text))
    assert r["status"] == "unknown" and not r["causes"]
