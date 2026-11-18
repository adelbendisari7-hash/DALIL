"""data/scripts/anonymiser_ouedkniss.py : tous les champs texte sont nettoyés, pas seulement titre et description."""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "data" / "scripts"))

from anonymiser_ouedkniss import anonymize  # noqa: E402


def test_numero_dans_le_modele_masque_date_et_nombres_intacts():
    row = {"id": 123, "seller_username": "vendeur_x", "brand": "Lifan", "model": "0664 21 62 78",
           "version_trim": "appelez 0770.12.34.56", "city": "Oran", "created_date": "2026-11-17T09:30:45.000Z",
           "price_dzd": 560000000, "kilometrage": 150000, "title": "Lifan X60", "description": "bon état"}
    out = anonymize(row, b"sel", Counter())
    assert out["model"] == "[téléphone]" and "0770" not in out["version_trim"]
    assert out["created_date"] == "2026-11-17T09:30:45.000Z"
    assert out["price_dzd"] == 560000000 and out["kilometrage"] == 150000 and out["city"] == "Oran"
    assert "seller_username" not in out and out["id"] != 123
