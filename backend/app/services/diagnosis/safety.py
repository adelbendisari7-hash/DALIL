"""Règles de sûreté (section 6.1)."""
from __future__ import annotations

import re

from .normalize import normalize

DISCLAIMER = (
    "DALIL est une aide au diagnostic, pas un diagnostic certifié. "
    "Faites confirmer la panne par un mécanicien avant d'acheter une pièce."
)
TOO_SHORT = (
    "Votre description est trop courte pour trouver la panne. Précisez quand cela arrive (au freinage, au démarrage, "
    "en virage, à froid…) et ce que vous remarquez (bruit, voyant, fumée, odeur, vibration)."
)
DO_NOT_DRIVE = "Ne roulez pas avec ce véhicule : le problème touche un organe de sécurité. Faites-le remorquer ou examiner sur place."
UNKNOWN = (
    "Je ne sais pas identifier cette panne avec assez de confiance. "
    "Décrivez le symptôme autrement (quand, où, quel bruit) ou consultez un mécanicien."
)

# Freinage, direction, odeur de carburant, surchauffe (textes normalisés, sans accents).
DANGER_PATTERNS = [
    r"\bfrein", r"pedale (molle|s'enfonce|au plancher)", r"ne freine (plus|pas)",
    r"\bdirection\b.*(dure|bloque|lache)", r"volant (bloque|tres dur)",
    r"odeur (d'|de )?(essence|gasoil|carburant)", r"fuite (d'|de )?(essence|gasoil|carburant)",
    r"surchauffe", r"temperature (monte|dans le rouge)", r"aiguille.*rouge", r"fumee blanche epaisse",
]


def text_is_dangerous(text: str) -> bool:
    t = normalize(text)
    return any(re.search(p, t) for p in DANGER_PATTERNS)
