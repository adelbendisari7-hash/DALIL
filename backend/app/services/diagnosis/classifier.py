"""Étape 3 : classifieur texte -> panne type (variante A : TF-IDF + régression logistique).

Les poids sont produits par `ml/train_baseline.py` (ou les carnets Kaggle pour mmBERT) et
chargés ici. S'ils manquent, le modèle de référence est entraîné à la volée sur les exemples
d'amorçage, ce qui prend moins d'une seconde.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from ...config import get_settings
from .normalize import normalize

log = logging.getLogger("dalil.classifier")


def load_examples(path: Path | None = None) -> tuple[list[str], list[str]]:
    path = path or Path(get_settings().data_dir) / "seed" / "diagnosis_examples_fr.jsonl"
    texts, labels = [], []
    for line in path.read_text(encoding="utf-8").split(chr(10)):
        if line.strip():
            row = json.loads(line)
            texts.append(row["text"])
            labels.append(row["fault"])
    return texts, labels


def fiche_examples() -> tuple[list[str], list[str]]:
    """Exemples tirés des fiches de pannes (nom + propositions de la description).

    Ajoutés à l'entraînement seulement, jamais à l'évaluation : ils font passer le top-1
    de 21 % à 59 % en validation croisée sur le jeu d'amorçage.
    """
    import re

    data = json.loads((Path(get_settings().data_dir) / "seed" / "faults.json").read_text(encoding="utf-8"))
    texts, labels = [], []
    for f in data["faults"]:
        texts.append(f["name_fr"])
        labels.append(f["slug"])
        for clause in re.split(r"[.,;:]", f["description"]):
            if len(clause.split()) >= 3:
                texts.append(clause.strip())
                labels.append(f["slug"])
    return texts, labels


def build_pipeline(large: bool = False) -> Pipeline:
    """large=True pour le corpus de l'étape 6 (~9 000 textes) : vocabulaire plafonné et régularisation
    plus forte, sans quoi l'entraînement dure des heures sur un processeur."""
    if large:
        features = FeatureUnion([
            ("word", TfidfVectorizer(preprocessor=normalize, ngram_range=(1, 2), sublinear_tf=True, min_df=2, max_features=100_000)),
            ("char", TfidfVectorizer(preprocessor=normalize, analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True,
                                     min_df=3, max_features=200_000)),
        ])
        return Pipeline([("features", features), ("clf", LogisticRegression(C=8.0, max_iter=500, tol=1e-3))])
    features = FeatureUnion([
        ("word", TfidfVectorizer(preprocessor=normalize, ngram_range=(1, 2), sublinear_tf=True, min_df=1)),
        ("char", TfidfVectorizer(preprocessor=normalize, analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=1)),
    ])
    return Pipeline([("features", features), ("clf", LogisticRegression(C=20.0, max_iter=3000))])


def train_baseline(texts: list[str], labels: list[str]) -> Pipeline:
    ft, fl = fiche_examples()
    pipe = build_pipeline()
    pipe.fit(list(texts) + ft, list(labels) + fl)
    return pipe


class FaultClassifier:
    """Classifieur scikit-learn. `target` dit ce qu'il prédit :
    - "fault" : une panne type (slug de faults), comme le modèle de référence ;
    - "part"  : une famille de pièce (slug de part_categories), comme le demande la section 6.1.
    La chaîne de diagnostic convertit une prédiction « part » en pannes types (voir pipeline.py).
    """

    def __init__(self, pipeline: Pipeline, target: str = "fault", version: str | None = None):
        self.pipeline = pipeline
        self.target = target
        self.version = version
        self.labels: list[str] = list(pipeline.classes_)

    def predict_proba(self, text: str) -> dict[str, float]:
        probs = self.pipeline.predict_proba([text])[0]
        return {label: float(p) for label, p in zip(self.labels, probs)}


class OnnxEncoderClassifier:
    """Encodeur affiné (mmBERT, XLM-R, DziriBERT) exporté en ONNX par le carnet Kaggle 02.

    Dossier attendu : model.onnx, tokenizer.json, labels.json ({"target": "part", "labels": [...],
    "version": "...", "max_length": 256}). Demande onnxruntime et tokenizers ; sous Windows,
    onnxruntime exige le Microsoft Visual C++ Redistributable.
    """

    def __init__(self, folder: Path):
        import numpy as np
        import onnxruntime as ort
        from tokenizers import Tokenizer

        meta = json.loads((folder / "labels.json").read_text(encoding="utf-8"))
        self.labels, self.target, self.version = meta["labels"], meta.get("target", "part"), meta.get("version")
        self.max_length = int(meta.get("max_length", 256))
        self.tok = Tokenizer.from_file(str(folder / "tokenizer.json"))
        self.tok.enable_truncation(self.max_length)
        self.session = ort.InferenceSession(str(folder / "model.onnx"), providers=["CPUExecutionProvider"])
        self.inputs = {i.name for i in self.session.get_inputs()}
        self._np = np

    def predict_proba(self, text: str) -> dict[str, float]:
        np = self._np
        enc = self.tok.encode(text)
        feed = {"input_ids": np.array([enc.ids], dtype=np.int64),
                "attention_mask": np.array([enc.attention_mask], dtype=np.int64)}
        if "token_type_ids" in self.inputs:
            feed["token_type_ids"] = np.array([enc.type_ids], dtype=np.int64)
        logits = self.session.run(None, {k: v for k, v in feed.items() if k in self.inputs})[0][0]
        e = np.exp(logits - logits.max())
        p = e / e.sum()
        return {label: float(x) for label, x in zip(self.labels, p)}


class FamilyRerankedClassifier:
    """Classifieur à deux niveaux (ml/train_family_reranker.py) : le classifieur de base propose ses pannes ou pièces,
    un classifieur de familles de pièces (entraîné notamment sur L'Argus, dont seule la famille est fiable) les
    reclasse : score = p(étiquette) x p(famille de l'étiquette) ** alpha, puis normalisation.
    alpha = 0 rend exactement le classifieur de base. Une étiquette sans famille connue reçoit un facteur neutre.
    """

    def __init__(self, base, family_pipeline, alpha: float, label_family: dict[str, str],
                 version: str | None = None):
        """`family_pipeline` : pipeline scikit-learn (TF-IDF) ou encodeur ONNX de familles (OnnxEncoderClassifier,
        CamemBERT entraîné par le carnet Kaggle 02_camembert_familles)."""
        self.base, self.family_pipeline, self.alpha = base, family_pipeline, float(alpha)
        self.label_family = label_family
        self.target, self.labels = base.target, base.labels
        self.version = version or f"{base.version}+familles-a{alpha:g}"
        classes = getattr(family_pipeline, "classes_", None)
        self.families: list[str] = list(classes) if classes is not None else list(family_pipeline.labels)

    def family_proba(self, text: str) -> dict[str, float]:
        if not hasattr(self.family_pipeline, "classes_"):   # encodeur ONNX : dictionnaire famille -> probabilité
            return self.family_pipeline.predict_proba(text)
        probs = self.family_pipeline.predict_proba([text])[0]
        return {f: float(p) for f, p in zip(self.families, probs)}

    def predict_proba(self, text: str) -> dict[str, float]:
        p = self.base.predict_proba(text)
        if not self.alpha:
            return p
        q = self.family_proba(text)
        neutral = 1.0 / max(len(q), 1)
        scores = {label: v * (q.get(self.label_family.get(label, ""), neutral) + 1e-6) ** self.alpha for label, v in p.items()}
        total = sum(scores.values()) or 1.0
        return {label: v / total for label, v in scores.items()}


def load_classifier(path: Path):
    """Charge un classifieur : fichier .joblib (pipeline seul, dict avec target/version, ou classifieur à deux
    niveaux « family_rerank ») ou dossier ONNX."""
    if path.is_dir():
        return OnnxEncoderClassifier(path)
    obj = joblib.load(path)
    if isinstance(obj, dict) and obj.get("kind") == "family_rerank":
        if obj.get("base_onnx"):   # premier niveau ONNX (CamemBERT-pièces), dossier relatif au fichier .joblib
            base = OnnxEncoderClassifier((path.parent / obj["base_onnx"]).resolve())
        else:
            base = FaultClassifier(obj["base"]["pipeline"], obj["base"].get("target", "fault"), obj["base"].get("version"))
        family = obj.get("family_pipeline")
        if family is None:   # modèle de familles ONNX, dossier relatif au fichier .joblib
            family = OnnxEncoderClassifier((path.parent / obj["family_onnx"]).resolve())
        return FamilyRerankedClassifier(base, family, obj["alpha"], obj["label_family"], obj.get("version"))
    if isinstance(obj, dict):
        return FaultClassifier(obj["pipeline"], obj.get("target", "fault"), obj.get("version"))
    return FaultClassifier(obj)


@lru_cache
def get_classifier():
    path = Path(get_settings().classifier_path)
    if path.exists():
        return load_classifier(path)
    log.warning("Poids du classifieur absents (%s) : entraînement à la volée du modèle de référence", path)
    return FaultClassifier(train_baseline(*load_examples()))
