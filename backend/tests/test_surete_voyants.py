"""Règle de sûreté du voyant de pression d'huile (ajoutée avec la grille des voyants, 28/11/2026) : rouler sans
pression d'huile casse le moteur ; le simple rappel d'entretien (« vidange », clé) n'est pas un danger."""
import pytest

from app.services.diagnosis.safety import text_is_dangerous


@pytest.mark.parametrize("text", [
    "le voyant de pression d'huile rouge s'est allumé", "voyant d'huile allumé en roulant", "la burette rouge clignote",
    "Le voyant de l'huile s'allume dans les virages",
])
def test_voyant_d_huile_dangereux(text):
    assert text_is_dangerous(text)


@pytest.mark.parametrize("text", ["le voyant de vidange (clé) s'est allumé", "il faut faire la vidange, huile noire",
                                  "petite fuite d'huile sous le moteur"])
def test_entretien_pas_dangereux(text):
    assert not text_is_dangerous(text)


def test_diagnostic_du_voyant_d_huile_dit_de_ne_pas_rouler(client):
    r = client.post("/api/v1/diagnosis", json={"text": "le voyant de pression d'huile rouge s'est allumé"}).json()
    assert r["safety"]["do_not_drive"] is True
