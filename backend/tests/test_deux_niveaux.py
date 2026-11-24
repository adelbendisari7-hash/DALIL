"""Classifieur à deux niveaux (FamilyRerankedClassifier) : les familles de pièces reclassent les pannes proposées."""
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.services.diagnosis.classifier import FamilyRerankedClassifier, FaultClassifier, load_classifier


def _pipe(texts, labels):
    return Pipeline([("v", TfidfVectorizer()), ("c", LogisticRegression(C=10))]).fit(texts, labels)


BASE = _pipe(["bruit au freinage", "grincement frein", "batterie à plat", "ne démarre pas le matin"],
             ["plaquettes-usees", "plaquettes-usees", "batterie-faible", "batterie-faible"])
FAMILIES = _pipe(["pédale de frein molle", "bruit en freinant", "voyant batterie", "démarreur muet"],
                 ["freinage", "freinage", "electricite", "electricite"])
LF = {"plaquettes-usees": "freinage", "batterie-faible": "electricite"}


def test_alpha_nul_rend_le_classifieur_de_base():
    base = FaultClassifier(BASE, "fault", "v1")
    two = FamilyRerankedClassifier(base, FAMILIES, 0.0, LF)
    assert two.predict_proba("bruit en freinant") == base.predict_proba("bruit en freinant")


def test_la_famille_fait_remonter_la_bonne_panne_et_somme_un():
    base = FaultClassifier(BASE, "fault", "v1")
    text = "pédale de frein molle"                       # mot absent du classifieur de base
    p0 = base.predict_proba(text)
    p1 = FamilyRerankedClassifier(base, FAMILIES, 1.0, LF).predict_proba(text)
    assert p1["plaquettes-usees"] > p0["plaquettes-usees"]
    assert abs(sum(p1.values()) - 1) < 1e-9


def test_chargement_du_fichier(tmp_path):
    path = tmp_path / "famille_rerank_a0.5.joblib"
    joblib.dump({"kind": "family_rerank", "base": {"pipeline": BASE, "target": "fault", "version": "v1"},
                 "family_pipeline": FAMILIES, "alpha": 0.5, "label_family": LF, "version": "v1+familles-a0.5"}, path)
    clf = load_classifier(path)
    assert isinstance(clf, FamilyRerankedClassifier) and clf.target == "fault" and clf.version == "v1+familles-a0.5"
    assert set(clf.predict_proba("frein")) == {"plaquettes-usees", "batterie-faible"}
