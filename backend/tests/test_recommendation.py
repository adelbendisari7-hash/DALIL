"""Dix scénarios de classement écrits à la main (critère de fin de l'étape 5)."""
from datetime import datetime, timedelta, timezone

from app.services.recommendation import ShopSignals, rank, score_shop

NOW = datetime(2027, 3, 1, tzinfo=timezone.utc)
FRESH = NOW - timedelta(days=30)
OLD = NOW - timedelta(days=300)


def S(i, **kw):
    kw.setdefault("confirmed_at", FRESH)
    return ShopSignals(shop_id=i, name=f"M{i}", **kw)


def order(signals):
    return [r.shop_id for r in rank(signals, NOW)]


def test_1_catalogue_compatible_bat_marque_seule():
    assert order([S(1, sells_brand=True), S(2, catalog=1.0)]) == [2, 1]


def test_2_marque_et_famille_battent_famille_seule():
    assert order([S(1, sells_category=True), S(2, sells_brand=True, sells_category=True)]) == [2, 1]


def test_3_a_signaux_egaux_le_plus_proche_gagne():
    assert order([S(1, sells_brand=True, distance_km=8), S(2, sells_brand=True, distance_km=1)]) == [2, 1]


def test_4_la_proximite_ne_compense_pas_la_marque():
    # vend la marque à 10 km > ne vend que la famille à 100 m
    assert order([S(1, distance_km=0.1, sells_category=True), S(2, distance_km=10, sells_brand=True, sells_category=True)]) == [2, 1]


def test_5_fiche_perimee_perd_des_points():
    a = score_shop(S(1, sells_brand=True, confirmed_at=FRESH), NOW)
    b = score_shop(S(2, sells_brand=True, confirmed_at=OLD), NOW)
    assert a.score > b.score and b.stale and not a.stale
    assert "fiche à reconfirmer" in b.reasons


def test_6_retours_pieces_trouvees_font_monter():
    assert order([S(1, sells_brand=True), S(2, sells_brand=True, found_yes=5)]) == [2, 1]


def test_7_retours_negatifs_font_descendre():
    assert order([S(1, sells_brand=True, found_no=6), S(2, sells_brand=True)]) == [2, 1]


def test_8_taux_de_reponse_aux_demandes():
    assert order([S(1, sells_category=True, requests_notified=10, requests_answered=0),
                  S(2, sells_category=True, requests_notified=10, requests_answered=9)]) == [2, 1]


def test_9_position_inconnue_reste_neutre():
    r = score_shop(S(1, sells_brand=True, distance_km=None), NOW)
    assert r.breakdown["proximity"] == 0.5


def test_10_score_maximal_et_raisons_expliquees():
    r = score_shop(S(1, catalog=1.0, sells_brand=True, sells_category=True, distance_km=0, found_yes=50,
                     requests_notified=10, requests_answered=10, brand_name="Renault", category_name="Freinage",
                     matching_refs=["FICTIF-1"]), NOW)
    assert 0.95 < r.score <= 1.0
    assert r.reasons[:3] == ["a la pièce au catalogue (réf. FICTIF-1)", "vend Renault", "vend freinage"]
    assert any(x.startswith("à 0,0 km") for x in r.reasons)


def test_ordre_stable_a_score_egal():
    assert order([S(3, sells_brand=True), S(1, sells_brand=True), S(2, sells_brand=True)]) == [1, 2, 3]
