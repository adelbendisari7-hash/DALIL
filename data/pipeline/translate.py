"""Traduction en français des textes collectés (section 5, « Traduction »).

- Modèles ouverts Helsinki-NLP (MarianMT) : anglais -> français, et chinois -> anglais -> français.
  Sur le portable, réservé à de petits volumes ; les corpus complets se traduisent sur GPU Kaggle
  avec la même commande (le script détecte la carte graphique).
- Le texte d'origine n'est jamais modifié : la traduction va dans text_fr.
- Le lexique des pièces impose les termes français : corrections après traduction (POSTEDIT) et
  signalement des termes de pièces mal rendus (GLOSSARY) dans l'échantillon de relecture.
- Cache par empreinte du texte : relancer ne retraduit rien.
- Échantillon de relecture : CSV de N traductions tirées au hasard, à relire à la main (200 visées),
  car une erreur sur un nom de pièce fausse l'étiquette d'entraînement.
"""
from __future__ import annotations

import csv
import json
import random
import re
from pathlib import Path

from .common import PROCESSED, read_jsonl, sha1, write_jsonl

CACHE = PROCESSED / "translations" / "cache.jsonl"
MODELS = {"en": "Helsinki-NLP/opus-mt-en-fr", "zh": "Helsinki-NLP/opus-mt-zh-en"}

# Corrections de traductions automatiques fautives -> terme du lexique DALIL.
POSTEDIT = [
    (r"\btampons? de frein\b", "plaquettes de frein"), (r"\bcoussinets? de frein\b", "plaquettes de frein"),
    (r"\brotors?\b", "disques"), (r"\bamortisseurs? de chocs?\b", "amortisseurs"),
    (r"\bcourroie (de )?serpentin(e)?\b", "courroie d'accessoires"), (r"\bconvertisseur catalytique\b", "catalyseur"),
    (r"\bbougies? de lueur\b", "bougies de préchauffage"), (r"\bbougies? lumineuses?\b", "bougies de préchauffage"),
    (r"\bjoints? de tête\b", "joint de culasse"), (r"\bjoint d'en-tête\b", "joint de culasse"),
    (r"\bpompe (à|a) gaz\b", "pompe à carburant"), (r"\bvoyant (du )?moteur de contrôle\b", "voyant moteur"),
    (r"\blumière du moteur de contrôle\b", "voyant moteur"), (r"\blumière de contrôle du moteur\b", "voyant moteur"),
    (r"\bmoteur de démarrage\b", "démarreur"), (r"\bdémarreur moteur\b", "démarreur"),
    (r"\bembouts? de biellette\b", "rotules de direction"), (r"\bextrémités? de tige de liaison\b", "rotules de direction"),
    (r"\barticulations? (à|a) rotule\b", "rotules"), (r"\bjambes? de force\b", "amortisseurs"),
    (r"\bcapteur d'oxygène\b", "sonde lambda"), (r"\bchaîne de synchronisation\b", "chaîne de distribution"),
    (r"\bcourroie de synchronisation\b", "courroie de distribution"), (r"\bboîte de transmission\b", "boîte de vitesses"),
]
# terme anglais -> forme française attendue (sans accents, en minuscules) pour signaler les écarts
GLOSSARY = [
    (r"brake pads?", "plaquette"), (r"rotors?|brake dis[ck]s?", "disque"), (r"spark plugs?", "bougie"),
    (r"timing (belt|chain)", "distribution"), (r"alternator", "alternateur"), (r"starter", "demarreur"),
    (r"water pump", "pompe a eau"), (r"thermostat", "thermostat"), (r"head gasket", "joint de culasse"),
    (r"catalytic converter", "catalyseur"), (r"clutch", "embrayage"), (r"transmission", "boite"),
    (r"wheel bearing", "roulement"), (r"ball joint", "rotule"), (r"shock absorbers?|struts?", "amortisseur"),
    (r"fuel pump", "pompe"), (r"radiator", "radiateur"), (r"battery", "batterie"), (r"o2 sensor|oxygen sensor", "sonde"),
]


def postedit(fr: str) -> str:
    for pat, rep in POSTEDIT:
        fr = re.sub(pat, rep, fr, flags=re.IGNORECASE)
    return fr


def glossary_misses(src: str, fr: str) -> list[str]:
    import unicodedata

    plain = "".join(c for c in unicodedata.normalize("NFD", fr.lower()) if unicodedata.category(c) != "Mn")
    return [want for pat, want in GLOSSARY if re.search(pat, src.lower()) and want not in plain]


def split_sentences(text: str, max_chars: int = 400) -> list[str]:
    parts = re.split(r"(?<=[.!?。；;])\s*", text.strip())
    out = []
    for p in parts:
        while len(p) > max_chars:  # phrases très longues : coupe sur une virgule ou un espace
            cut = max(p.rfind(",", 0, max_chars), p.rfind(" ", 0, max_chars), max_chars // 2)
            out.append(p[:cut].strip())
            p = p[cut:].strip(" ,")
        if p.strip():
            out.append(p.strip())
    return out


# Sigles gardés en majuscules quand un texte écrit tout en capitales est remis en casse normale.
ACRONYMS = ["ABS", "ECU", "EGR", "OBD", "OBD2", "OBDII", "CEL", "TPMS", "ESC", "CVT", "DTC", "VIN", "MPH", "RPM",
            "VW", "GDI", "TSB", "NHTSA", "OEM", "CV", "MAF", "DPF", "AC", "PCM", "TCM", "BCM", "SRS", "EPC", "LED", "USA"]
_ACRO_RE = re.compile(r"\b(" + "|".join(a.lower() for a in sorted(ACRONYMS, key=len, reverse=True)) + r")\b")


def upper_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    return sum(c.isupper() for c in letters) / max(len(letters), 1)


def prepare(text: str) -> str:
    """Remet en casse normale un texte écrit en capitales (72 % des plaintes NHTSA) : les modèles de
    traduction, entraînés sur du texte ordinaire, traduisent très mal les capitales."""
    if upper_ratio(text) <= 0.6:
        return text
    t = text.lower()
    t = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), t)
    t = re.sub(r"\bi\b", "I", t)
    return _ACRO_RE.sub(lambda m: m.group(1).upper(), t)


class Translator:
    def __init__(self, backend: str = "opus", batch_size: int = 16, log=print, num_beams: int = 2):
        self.backend, self.batch_size, self.log, self.num_beams = backend, batch_size, log, num_beams
        self.cache: dict[str, str] = {}
        if CACHE.exists():
            for row in read_jsonl(CACHE):
                self.cache[row["h"]] = row["fr"]
        self._models: dict = {}
        self._new: list[dict] = []

    def _model(self, name: str):
        if name not in self._models:
            import torch
            from transformers import MarianMTModel, MarianTokenizer

            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.log(f"  chargement de {name} sur {device}")
            tok = MarianTokenizer.from_pretrained(name)
            model = MarianMTModel.from_pretrained(name).to(device).eval()
            if device == "cuda":
                model = model.half()  # demi-précision : environ deux fois plus rapide sur GPU
                self.batch_size = max(self.batch_size, 48)
            self._models[name] = (tok, model, device)
        return self._models[name]

    def _mt(self, sentences: list[str], name: str) -> list[str]:
        import torch

        tok, model, device = self._model(name)
        out = []
        for i in range(0, len(sentences), self.batch_size):
            batch = tok(sentences[i:i + self.batch_size], return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
            with torch.no_grad():
                gen = model.generate(**batch, max_new_tokens=512, num_beams=self.num_beams)
            out += tok.batch_decode(gen, skip_special_tokens=True)
        return out

    def translate(self, texts: list[str], lang: str) -> list[str | None]:
        if self.backend == "none":
            return [None] * len(texts)
        texts = [prepare(t) for t in texts]
        keys =[sha1(lang + "\x00" + t) for t in texts]
        todo = [i for i, k in enumerate(keys) if k not in self.cache]
        if todo:
            sents, owner = [], []
            for i in todo:
                for s in split_sentences(texts[i]):
                    sents.append(s)
                    owner.append(i)
            if lang == "zh":
                mid = self._mt(sents, MODELS["zh"])
                fr = self._mt(mid, MODELS["en"])
            else:
                fr = self._mt(sents, MODELS["en"])
            joined: dict[int, list[str]] = {}
            for i, s in zip(owner, fr):
                joined.setdefault(i, []).append(s)
            for i in todo:
                result = postedit(" ".join(joined.get(i, [])))
                self.cache[keys[i]] = result
                self._new.append({"h": keys[i], "fr": result})
        return [self.cache[k] for k in keys]

    def save(self) -> None:
        if not self._new:
            return
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        with CACHE.open("a", encoding="utf-8") as f:
            for row in self._new:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        self._new = []


def translate_file(path: Path, tr: Translator, limit: int | None = None, redo_uppercase: bool = False) -> tuple[int, int]:
    """Traduit les enregistrements sans text_fr. Renvoie (traduits maintenant, restant à traduire).
    redo_uppercase : retraduit les textes écrits en capitales (traduits avant la remise en casse normale)."""
    rows = list(read_jsonl(path))
    if redo_uppercase:
        for r in rows:
            if r["lang"] != "fr" and upper_ratio(r["text"]) > 0.6:
                r["text_fr"] = None
    pending = [r for r in rows if not r.get("text_fr") and r["lang"] != "fr"]
    if limit is not None:
        pending = pending[:limit]
    done = 0
    for i in range(0, len(pending), 64):
        chunk = pending[i:i + 64]
        by_lang: dict[str, list[dict]] = {}
        for r in chunk:
            by_lang.setdefault(r["lang"], []).append(r)
        for lang, rs in by_lang.items():
            if rs[0]["source"] == "cvffad":
                for r in rs:
                    _translate_cvffad(r, tr)
            else:
                for r, fr in zip(rs, tr.translate([r["text"] for r in rs], lang)):
                    r["text_fr"] = fr
        done += sum(1 for r in chunk if r.get("text_fr"))
        tr.save()
        if i and i % 640 == 0:
            tr.log(f"    {i} traduits…")
    write_jsonl(path, rows)
    remaining = sum(1 for r in rows if not r.get("text_fr") and r["lang"] != "fr")
    return done, remaining


def _translate_cvffad(r: dict, tr: Translator) -> None:
    """Fiche CVFFAD : nom traduit à la main, symptômes/causes/réparations traduits phrase par phrase."""
    m = r["meta"]
    lists = {k: tr.translate(m.get(f"{k}_zh", []), "zh") for k in ("symptoms", "causes", "repairs")}
    if any(v and None in v for v in lists.values()):
        return
    m.update({f"{k}_fr": v for k, v in lists.items()})
    r["text_fr"] = (f"{m['name_fr']}. Symptômes : {' ; '.join(lists['symptoms'])}. "
                    f"Causes : {' ; '.join(lists['causes'])}. Réparations : {' ; '.join(lists['repairs'])}.")


def review_sample(paths: list[Path], n: int = 200, seed: int = 13) -> Path | None:
    rows = [r for p in paths for r in read_jsonl(p) if r.get("text_fr") and r["lang"] == "en"]
    if not rows:
        return None
    random.Random(seed).shuffle(rows)
    out = PROCESSED / "translations" / "relecture.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "source", "texte_anglais", "traduction", "termes_a_verifier", "correct (oui/non)", "correction", "commentaire"])
        for r in rows[:n]:
            w.writerow([r["id"], r["source"], r["text"][:1500], r["text_fr"][:1500],
                        ", ".join(glossary_misses(r["text"], r["text_fr"])), "", "", ""])
    return out
