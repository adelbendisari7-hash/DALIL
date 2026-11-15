"""Étape 1 de la chaîne : normalisation du texte (section 6.1)."""
from __future__ import annotations

import re
import unicodedata

DTC_RE = re.compile(r"\b([PCBU])\s?([0-3][0-9A-F]{3})\b", re.IGNORECASE)
ARABIC_RE = re.compile(r"[؀-ۿ]")

# Lexique local : formes orales ou fautives -> terme du lexique des pièces.
# La darija (V2) s'ajoutera ici, en lettres arabes et latines.
LEXICON = {
    "plakette": "plaquettes", "plaquete": "plaquettes", "frain": "frein", "frein a main": "frein de stationnement",
    "amorto": "amortisseur", "amortos": "amortisseurs", "ventilo": "ventilateur", "alterno": "alternateur",
    "baterie": "batterie", "batri": "batterie", "demareur": "demarreur", "embrayge": "embrayage",
    "gazoil": "gasoil", "gas oil": "gasoil", "diesel": "gasoil", "clime": "clim", "radiateure": "radiateur",
    "courroi": "courroie", "durit": "durite", "calorstat": "thermostat", "valise": "diagnostic electronique",
    "voyant orange": "voyant moteur", "check engine": "voyant moteur", "chauffe": "surchauffe chauffe",
    # synonymes de bruits et d'organes (formulations courantes des clients)
    "ronronnement": "ronflement grondement", "bourdonnement": "ronflement grondement", "vrombissement": "ronflement grondement",
    "crisse": "grince", "crissement": "grincement", "couine": "grince", "couinement": "grincement",
    "aerateurs": "ventilation", "aerateur": "ventilation", "aerations": "ventilation", "bouches d'air": "ventilation",
    "clim": "climatisation", "moisi": "mauvaise odeur", "pue": "mauvaise odeur",
}


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def detect_lang(text: str) -> str:
    if ARABIC_RE.search(text):
        return "ar"  # arabe ou darija en lettres arabes : hors périmètre V1
    return "fr"


def extract_dtc(text: str) -> list[str]:
    return sorted({(m.group(1) + m.group(2)).upper() for m in DTC_RE.finditer(text or "")})


def normalize(text: str) -> str:
    t = strip_accents((text or "").lower())
    t = t.replace("’", "'")
    t = re.sub(r"\s+", " ", t).strip()
    for k, v in LEXICON.items():
        t = re.sub(rf"\b{re.escape(k)}\b", v, t)
    return t
