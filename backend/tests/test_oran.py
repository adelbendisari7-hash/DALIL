"""Jeu de test d'Oran : conversion des fiches des mécaniciens (ml/oran_csv_to_jsonl.py)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml"))

import oran_csv_to_jsonl as O  # noqa: E402

HEAD = "id;date;mecanicien;marque;modele;motorisation;annee;symptome_mots_du_client;codes_obd;cause_trouvee;pieces_changees;commentaire\n"


def test_modele_fourni_ne_contient_que_l_exemple():
    cases, errors = O.convert((ROOT / "data" / "test" / "modele_annotation_oran.csv").read_text(encoding="utf-8-sig"))
    assert cases == [] and errors == []  # la ligne d'exemple est ignorée


def test_conversion_des_fiches():
    text = HEAD + (
        "oran002;2027-02-11;M1;Dacia;Logan;1.5 dCi;2015;ça grince fort en freinant;;usure;plaquettes avant;\n"
        "oran003;2027-02-11;M2;Peugeot;301;1.6 HDi;2015;voyant moteur;p0420;catalyseur;catalyseur|sonde-lambda;\n"
        "oran004;2027-02-12;M2;;;;;combien coûte une vidange;;;hors sujet;\n"
    )
    cases, errors = O.convert(text)
    assert errors == []
    by_id = {c["id"]: c for c in cases}
    assert by_id["oran002"]["expect"] == ["plaquettes-avant"]
    assert by_id["oran002"]["variant"] == ["Dacia", "Logan", "1.5 dCi", 2015]
    assert by_id["oran003"]["dtc"] == ["P0420"] and set(by_id["oran003"]["expect"]) == {"catalyseur", "sonde-lambda"}
    assert by_id["oran004"]["expect_status"] == "unknown" and "variant" not in by_id["oran004"]


def test_lignes_invalides_refusees_avec_la_raison():
    text = HEAD + (
        "a1;;M1;;;;;ça vibre;;;pièce magique;\n"
        "a2;;M1;;;;;;;;batterie;\n"
        "a3;;M1;;;;;démarre mal;;;batterie;\n"
        "a3;;M1;;;;;doublon;;;batterie;\n"
        "a4;;M1;;;;;bruit;;;;\n"
    )
    cases, errors = O.convert(text)
    assert [c["id"] for c in cases] == ["a3"]
    joined = " | ".join(errors)
    assert "pièce inconnue" in joined and "ni symptôme ni code" in joined
    assert "en double" in joined and "pièce changée manquante" in joined


def test_vehicule_inconnu_garde_sans_vehicule_et_signale():
    cases, errors = O.convert(HEAD + "b1;;M1;Zastava;Yugo;1.1;1988;le moteur chauffe;;;thermostat;\n")
    assert errors == [] and "variant" not in cases[0]
    assert any("véhicule inconnu" in w for w in O.warnings)
