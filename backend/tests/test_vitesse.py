"""Temps de réponse sur les textes longs : la recherche ne lit que le début du texte, le classifieur lit tout."""
from app.services.diagnosis.pipeline import shorten_query


def test_texte_court_inchange_et_zero_desactive():
    assert shorten_query("ça grince quand je freine", 400) == "ça grince quand je freine"
    long = "mot " * 300
    assert shorten_query(long, 0) == long


def test_coupe_a_la_fin_d_un_mot():
    t = "la voiture ne démarre plus le matin " * 30
    s = shorten_query(t, 100)
    assert len(s) <= 100 and t.startswith(s) and not s.endswith(" ") and t[len(s)] == " "
