"""Troisième série d'améliorations (28/11/2026) : photo jointe à une demande, alerte de baisse de prix, rappels des
constructeurs, récapitulatif de la semaine des magasins, mécaniciens, carnet transmis à la revente."""
from datetime import datetime, timezone

from sqlalchemy import select

from app.models import PartCategory, PartRequest, Shop, ShopCategory, User

from .conftest import login
from .test_catalogue_rapide import jpeg

API = "/api/v1"


def _cat(db, slug="plaquettes-avant"):
    return db.scalar(select(PartCategory).where(PartCategory.slug == slug))


def _owned_shop(db, phone_user: User, name: str, category_id: int) -> Shop:
    s = Shop(name=name, status="verified", source="declared", owner_user_id=phone_user.id,
             verified_at=datetime.now(timezone.utc))
    db.add(s)
    db.flush()
    db.add(ShopCategory(shop_id=s.id, category_id=category_id, source="declared"))
    db.commit()
    return s


def _user(db, phone: str) -> User:
    return db.scalar(select(User).where(User.phone == "+213" + phone[1:]))


# --- 1. Photo jointe à une demande -----------------------------------------------------------------------------------

def test_photo_de_demande_envoyee_par_jeton_vue_par_le_magasin(client, db):
    hm = login(client, "0698000001")
    owner = _user(db, "0698000001")
    owner.role = "shop_owner"
    fam = db.scalar(select(PartCategory).where(PartCategory.slug == "freinage"))
    shop = _owned_shop(db, owner, "Magasin photo", fam.id)
    req = client.post(f"{API}/part-requests", json={"category_id": _cat(db).id}).json()   # sans compte
    files = {"file": ("piece.jpg", jpeg(), "image/jpeg")}
    assert client.post(f"{API}/part-requests/{req['id']}/photo", files=files).status_code == 404            # sans jeton
    assert client.post(f"{API}/part-requests/{req['id']}/photo", params={"token": "faux"}, files=files).status_code == 404
    r = client.post(f"{API}/part-requests/{req['id']}/photo", params={"token": req["token"]}, files=files)
    assert r.status_code == 200 and r.json()["photo_url"].startswith("/api/v1/media/demandes/")
    url = r.json()["photo_url"]
    photo = client.get(url)
    assert photo.status_code == 200 and b"GPS" not in photo.content and b"Exif" not in photo.content   # métadonnées retirées
    inbox = [x for x in client.get(f"{API}/part-requests/inbox", headers=hm).json() if x["request_id"] == req["id"]]
    assert inbox and inbox[0]["shop_id"] == shop.id and inbox[0]["photo_url"] == url
    assert client.get(f"{API}/part-requests/{req['id']}", params={"token": req["token"]}).json()["photo_url"] == url
    # Pas une image : refusée ; retrait par le client
    bad = {"file": ("x.jpg", b"pas une image", "image/jpeg")}
    assert client.post(f"{API}/part-requests/{req['id']}/photo", params={"token": req["token"]}, files=bad).status_code == 422
    assert client.delete(f"{API}/part-requests/{req['id']}/photo", params={"token": req["token"]}).status_code == 204
    assert client.get(url).status_code == 404


def test_photo_effacee_avec_le_compte(client, db):
    h = login(client, "0698000002")
    req = client.post(f"{API}/part-requests", headers=h, json={"category_id": _cat(db).id}).json()
    url = client.post(f"{API}/part-requests/{req['id']}/photo", headers=h,
                      files={"file": ("p.jpg", jpeg(), "image/jpeg")}).json()["photo_url"]
    assert client.delete(f"{API}/auth/me", headers=h).status_code == 204
    assert client.get(url).status_code == 404
    db.expire_all()
    assert db.get(PartRequest, req["id"]).photo_url is None


# --- 2. Alerte de baisse de prix ---------------------------------------------------------------------------------------

def test_prix_suivi_baisse_puis_vu(client, db):
    from app.models import Product
    from .test_avis_prix import _free_category, _shop
    h = login(client, "0698000010")
    cat = _free_category(db)
    shop = _shop(db, "Prix suivi A")
    p = Product(shop_id=shop.id, category_id=cat.id, title="Pièce suivie", price=5000)
    db.add(p)
    db.commit()
    w = client.post(f"{API}/me/price-watches", headers=h, json={"category_id": cat.id}).json()
    assert w["reference_price"] == 5000 and w["alert"] is None and w["lowest"]["shop"]["name"] == "Prix suivi A"
    assert client.post(f"{API}/me/price-watches", headers=h, json={"category_id": cat.id}).json()["id"] == w["id"]   # pas de doublon
    p.price = 4000
    db.commit()
    w2 = client.get(f"{API}/me/price-watches", headers=h).json()[0]
    assert w2["alert"] == "drop" and w2["drop_pct"] == 20 and w2["lowest"]["price"] == 4000
    assert client.get(f"{API}/me/alerts", headers=h).json()["prices"] == 1
    seen = client.post(f"{API}/me/price-watches/{w['id']}/seen", headers=h).json()
    assert seen["reference_price"] == 4000 and seen["alert"] is None
    assert client.get(f"{API}/me/alerts", headers=h).json()["prices"] == 0
    p.price = 4500          # une hausse ne déclenche rien
    db.commit()
    assert client.get(f"{API}/me/price-watches", headers=h).json()[0]["alert"] is None
    assert client.delete(f"{API}/me/price-watches/{w['id']}", headers=h).status_code == 204
    assert client.get(f"{API}/me/price-watches", headers=h).json() == []


def test_prix_suivi_piece_sans_prix_puis_disponible(client, db):
    from app.models import Product
    from .test_avis_prix import _free_category, _shop
    h = login(client, "0698000011")
    cat = _free_category(db)
    w = client.post(f"{API}/me/price-watches", headers=h, json={"category_id": cat.id}).json()
    assert w["reference_price"] is None and w["lowest"] is None and w["alert"] is None
    shop = _shop(db, "Prix suivi B")
    db.add(Product(shop_id=shop.id, category_id=cat.id, title="Enfin là", price=3000))
    db.commit()
    assert client.get(f"{API}/me/price-watches", headers=h).json()[0]["alert"] == "available"


def test_prix_suivi_refus_et_suivi_d_un_autre(client, db):
    h = login(client, "0698000012")
    assert client.post(f"{API}/me/price-watches", headers=h, json={"category_id": 999999}).status_code == 404
    w = client.post(f"{API}/me/price-watches", headers=h, json={"category_id": _cat(db).id}).json()
    h2 = login(client, "0698000013")
    assert client.delete(f"{API}/me/price-watches/{w['id']}", headers=h2).status_code == 404
    assert client.post(f"{API}/me/price-watches/{w['id']}/seen", headers=h2).status_code == 404
    assert client.get(f"{API}/me/price-watches").status_code == 401


# --- 3. Rappels des constructeurs ------------------------------------------------------------------------------------

def _recall(db, make, models, motif, date="2025-01-10"):
    from app.models import KnowledgeChunk
    c = KnowledgeChunk(source="rappelconso", lang="fr", license="Licence Ouverte v2.0",
                       text=f"Rappel {make.lower()} {models} : {motif} Risque : blessures.",
                       meta={"url": "https://rappel.conso.gouv.fr/fiche-rappel/1/x", "date": date,
                             "vehicle": {"make": make, "model": models}})
    db.add(c)
    db.commit()
    return c


def test_correspondance_des_rappels():
    from app.services.recalls import brand_key, split_model, _generation_after
    assert split_model("Clio 4") == ("clio", 4) and split_model("208") == ("208", None)
    assert split_model("Logan MCV") == ("logan mcv", None) and split_model("Clio V") == ("clio", 5)
    assert _generation_after("captur, clio iv, kangoo ii", "clio") == {4}
    assert _generation_after("208 v2, 2008 v2", "208") == {2}
    assert brand_key("Vw") == brand_key("Volkswagen") and brand_key("Citroën") == brand_key("Citroen")


def test_rappels_d_une_voiture(client, db):
    from app.models import Brand, Model, VehicleVariant
    from app.services import recalls
    variant = db.scalar(select(VehicleVariant).join(Model).join(Brand)
                        .where(Brand.name == "Renault", Model.name == "Clio 4"))
    assert variant is not None
    _recall(db, "Renault", "captur, clio iv voiture de tourisme.", "le frein peut lâcher.", "2025-03-01")
    _recall(db, "Renault", "clio v voiture de tourisme.", "autre génération.")
    _recall(db, "Renault", "clio voiture de tourisme. niv : vf1rjb00012345", "sans génération.", "2024-02-01")
    _recall(db, "Renault Trucks", "clio", "camion, écarté.")
    _recall(db, "Peugeot", "clio", "autre marque.")
    recalls._index.cache_clear()
    h = login(client, "0698000020")
    cid = client.post(f"{API}/me/vehicles", headers=h, json={"plate": "50001-115-31", "variant_id": variant.id}).json()["id"]
    r = client.get(f"{API}/me/vehicles/{cid}/recalls", headers=h).json()
    assert [x["motif"] for x in r["recalls"]] == ["le frein peut lâcher.", "sans génération."]   # plus récent d'abord
    assert r["recalls"][0]["match"] == "generation" and r["recalls"][1]["match"] == "model"
    assert r["recalls"][0]["url"].startswith("https://rappel.conso.gouv.fr/") and "RappelConso" in r["source"]
    car = next(c for c in client.get(f"{API}/me/vehicles", headers=h).json() if c["id"] == cid)
    assert car["recalls_count"] == 2
    # Voiture saisie à la main (« Renault Clio 4 ») : même résultat ; voiture d'un autre : 404
    cid2 = client.post(f"{API}/me/vehicles", headers=h, json={"plate": "50002-115-31", "label": "Renault Clio 4"}).json()["id"]
    assert len(client.get(f"{API}/me/vehicles/{cid2}/recalls", headers=h).json()["recalls"]) == 2
    h2 = login(client, "0698000021")
    assert client.get(f"{API}/me/vehicles/{cid}/recalls", headers=h2).status_code == 404


# --- 4. Récapitulatif de la semaine des magasins ----------------------------------------------------------------------

def test_recapitulatif_de_la_semaine(client, db):
    from datetime import timedelta
    from app.models import Product
    from .test_statistiques_magasin import _client, _shop
    h, sid = _shop(client, db, 40, families=("freinage",))
    plaq = _cat(db).id
    batt = _cat(db, "batterie").id
    near = _client("10.9.40.1")
    for _ in range(4):
        near.get(f"{API}/shops/recommend?category_id={batt}&lat=35.71&lng=-0.62")   # cherchée, pas vendue
    near.get(f"{API}/shops/recommend?category_id={plaq}&lat=35.71&lng=-0.62")       # vendue (famille), pas au catalogue
    old = datetime.now(timezone.utc) - timedelta(days=90)
    db.add(Product(shop_id=sid, category_id=_cat(db, "disques-frein").id if _cat(db, "disques-frein") else plaq,
                   title="Disques", price=7000, price_confirmed_at=old))
    db.commit()
    req = client.post(f"{API}/part-requests", json={"category_id": plaq}).json()   # demande reçue, sans réponse
    w = client.get(f"{API}/shops/{sid}/weekly", headers=h).json()
    assert w["week"].startswith(str(datetime.now(timezone.utc).isocalendar()[0]))
    missing = {m["category_id"]: m for m in w["missing"]}
    assert missing[batt]["sold"] is False and missing[batt]["searches"] >= 4
    assert missing[plaq]["sold"] is True and missing[plaq]["in_catalog"] is False
    assert w["stale_prices"] == 1 and w["products"] == 1
    assert w["pending_requests"] >= 1 and req["notified_shops"] >= 1
    assert {"impressions", "views", "calls", "requests"} <= set(w["current"])
    h2 = login(client, "0698000040")
    assert client.get(f"{API}/shops/{sid}/weekly", headers=h2).status_code in (403, 404)


# --- 5. Mécaniciens et garages ---------------------------------------------------------------------------------------

def _garage(db, name, specialties, lat=35.70, lng=-0.63, status="verified"):
    g = Shop(name=name, shop_type="garage", specialties=specialties, status=status, source="terrain", lat=lat, lng=lng,
             verified_at=datetime.now(timezone.utc) if status == "verified" else None)
    db.add(g)
    db.commit()
    return g


def test_garages_classes_par_specialite_et_proximite(client, db):
    from app.services.garages import family_of, match
    plaq = _cat(db)
    assert family_of(db, plaq.id) == "freinage"
    assert match(["freinage-suspension"], "freinage")[0] == 1.0 and match(["mecanique-generale"], "freinage")[0] == 0.5
    frein = _garage(db, "Garage Frein Test", ["freinage-suspension"], lat=35.71, lng=-0.62)
    general = _garage(db, "Garage Général Test", ["mecanique-generale"], lat=35.70, lng=-0.63)
    elec = _garage(db, "Garage Élec Test", ["electricite"], lat=35.70, lng=-0.63)
    draft = _garage(db, "Garage Brouillon Test", ["freinage-suspension"], status="draft")
    r = client.get(f"{API}/garages/recommend", params={"category_id": plaq.id, "lat": 35.70, "lng": -0.63}).json()
    names = [g["name"] for g in r]
    assert names.index("Garage Frein Test") < names.index("Garage Général Test") < names.index("Garage Élec Test")
    assert "Garage Brouillon Test" not in names and all(g["shop_type"] == "garage" for g in r)
    top = next(g for g in r if g["id"] == frein.id)
    assert top["specialties"] == ["Freinage et suspension"] and "spécialité : freinage et suspension" in top["reasons"]
    assert top["distance_km"] is not None
    assert client.get(f"{API}/garages/recommend", params={"category_id": 999999}).status_code == 404
    assert len(client.get(f"{API}/garages/specialties").json()) == 10
    _ = (general, elec, draft)


def test_garage_s_inscrit_avec_ses_specialites(client, db):
    h = login(client, "0698000050")
    client.patch(f"{API}/auth/me", headers=h, json={"role": "shop_owner"})
    bad = client.post(f"{API}/shops", headers=h, json={"name": "Garage X", "shop_type": "garage", "specialties": ["magie"]})
    assert bad.status_code == 422
    r = client.post(f"{API}/shops", headers=h, json={"name": "Garage Inscrit", "shop_type": "garage", "lat": 35.7, "lng": -0.63,
                                                    "specialties": ["diesel-injection", "electricite", "electricite"]})
    assert r.status_code == 201 and r.json()["shop_type"] == "garage"
    assert r.json()["specialties"] == ["diesel-injection", "electricite"]
    sid = r.json()["id"]
    p = client.patch(f"{API}/shops/{sid}", headers=h, json={"specialties": ["climatisation"], "shop_type": None})
    assert p.status_code == 200 and p.json()["specialties"] == ["climatisation"] and p.json()["shop_type"] == "garage"


def test_import_de_la_colonne_specialites(db):
    from app.services.imports import import_shops
    rows = [{"nom": "Garage Importé", "type": "garage", "specialites": "Diesel et injection ; electricite", "lat": "35.7", "lng": "-0.63"},
            {"nom": "Garage Faux", "type": "garage", "specialites": "voyance"}]
    rep = import_shops(db, rows, default_source="terrain")
    db.commit()
    g = db.scalar(select(Shop).where(Shop.name == "Garage Importé"))
    assert g.specialties == ["diesel-injection", "electricite"] and g.shop_type == "garage"
    assert len(rep.errors) == 1 and "spécialité inconnue" in rep.errors[0]["error"]


# --- 6. Carnet transmis à la revente ---------------------------------------------------------------------------------

def test_transfert_du_carnet_avec_accord_du_vendeur(client, db):
    from datetime import date, timedelta
    hv = login(client, "0698000060")      # vendeur
    from app.models import VehicleVariant
    vid = db.scalar(select(VehicleVariant).order_by(VehicleVariant.id)).id
    car = client.post(f"{API}/me/vehicles", headers=hv, json={"plate": "60001-115-31", "variant_id": vid, "mileage_km": 120000,
                                                             "nickname": "La grise", "vin": "VF1ABC12345678901"}).json()
    cid = car["id"]
    client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=hv,
                json={"items": ["vidange"], "km": 119000, "price": 6500, "place": "Garage du quartier", "note": "Huile 5W40"})
    client.post(f"{API}/me/vehicles/{cid}/papers", headers=hv, json={"kind": "controle", "valid_until": (date.today() + timedelta(days=200)).isoformat()})
    client.post(f"{API}/me/vehicles/{cid}/papers", headers=hv, json={"kind": "assurance", "valid_until": (date.today() + timedelta(days=100)).isoformat()})
    diag = client.post(f"{API}/diagnosis", headers=hv, json={"text": "ça grince quand je freine", "user_vehicle_id": cid}).json()

    t = client.post(f"{API}/me/vehicles/{cid}/transfer", headers=hv, json={}).json()
    code = t["code"]
    assert len(code) == 9 and code[4] == "-" and t["include_prices"] is False
    assert "code" not in client.get(f"{API}/me/vehicles/{cid}/transfer", headers=hv).json()   # code montré une seule fois

    hb = login(client, "0698000061")      # acheteur
    bad = client.post(f"{API}/me/vehicle-transfers/preview", headers=hb, json={"code": code, "plate": "60002-115-31"})
    assert bad.status_code == 404                                           # code juste, mauvais matricule
    assert client.post(f"{API}/me/vehicle-transfers/preview", headers=hb, json={"code": "AAAA-BBBB", "plate": "60001-115-31"}).status_code == 404
    pv = client.post(f"{API}/me/vehicle-transfers/preview", headers=hb, json={"code": code.lower(), "plate": "60001 115 31"}).json()
    assert pv["visits"] == 1 and pv["controles"] == 1 and pv["include_prices"] is False and "Garage" not in str(pv)
    got = client.post(f"{API}/me/vehicle-transfers/accept", headers=hb, json={"code": code, "plate": "60001-115-31"}).json()
    assert got["id"] == cid and got["nickname"] is None and got["vin"] == "VF1ABC12345678901" and got["mileage_km"] == 120000

    # L'acheteur a le carnet (sans prix ni remarque) et le contrôle technique ; pas l'assurance du vendeur
    v = client.get(f"{API}/me/vehicles/{cid}/maintenance/history", headers=hb).json()["visits"][0]
    assert v["operations"][0]["item"] == "vidange" and v["km"] == 119000 and v["place"] == "Garage du quartier"
    assert v["price"] is None and v["note"] is None
    p = client.get(f"{API}/me/vehicles/{cid}/papers", headers=hb).json()["current"]
    assert p["controle"] is not None and p["assurance"] is None
    # Le vendeur n'a plus la voiture ; son diagnostic reste à lui, détaché de la voiture
    assert all(c["id"] != cid for c in client.get(f"{API}/me/vehicles", headers=hv).json())
    hist = client.get(f"{API}/me/diagnoses", headers=hv).json()
    assert any(h["session_id"] == diag["session_id"] for h in hist)
    assert client.get(f"{API}/me/diagnoses", headers=hb).json() == []
    # Code déjà utilisé : refusé
    assert client.post(f"{API}/me/vehicle-transfers/accept", headers=hb, json={"code": code, "plate": "60001-115-31"}).status_code == 404


def test_transfert_avec_les_prix_et_annulation(client, db):
    from app.models import VehicleVariant
    hv = login(client, "0698000062")
    vid = db.scalar(select(VehicleVariant).order_by(VehicleVariant.id)).id
    cid = client.post(f"{API}/me/vehicles", headers=hv, json={"plate": "60003-115-31", "variant_id": vid}).json()["id"]
    client.post(f"{API}/me/vehicles/{cid}/maintenance", headers=hv, json={"items": ["vidange"], "price": 5000, "note": "ok"})
    first = client.post(f"{API}/me/vehicles/{cid}/transfer", headers=hv, json={}).json()["code"]
    second = client.post(f"{API}/me/vehicles/{cid}/transfer", headers=hv, json={"include_prices": True}).json()["code"]
    hb = login(client, "0698000063")
    body = {"code": first, "plate": "60003-115-31"}
    assert client.post(f"{API}/me/vehicle-transfers/preview", headers=hb, json=body).status_code == 404   # remplacé
    assert client.delete(f"{API}/me/vehicles/{cid}/transfer", headers=hv).status_code == 204
    assert client.post(f"{API}/me/vehicle-transfers/preview", headers=hb, json={**body, "code": second}).status_code == 404   # annulé
    third = client.post(f"{API}/me/vehicles/{cid}/transfer", headers=hv, json={"include_prices": True}).json()["code"]
    assert client.post(f"{API}/me/vehicle-transfers/accept", headers=hv, json={**body, "code": third}).status_code == 409   # à soi-même
    client.post(f"{API}/me/vehicle-transfers/accept", headers=hb, json={**body, "code": third})
    v = client.get(f"{API}/me/vehicles/{cid}/maintenance/history", headers=hb).json()["visits"][0]
    assert v["price"] == 5000 and v["note"] == "ok"
    assert client.post(f"{API}/me/vehicle-transfers/preview", headers=hb, json={**body, "plate": "pas un matricule"}).status_code == 422


# --- 7. Scénario de démonstration de soutenance ----------------------------------------------------------------------

def test_demo_soutenance_rejouable_puis_purgee(client, db):
    from app import demo_soutenance
    from app.models import UserVehicle
    out = demo_soutenance.run(db)
    out2 = demo_soutenance.run(db)                       # rejouable : rien en double
    assert db.scalar(select(UserVehicle).where(UserVehicle.plate == demo_soutenance.PLATE)).id == out2["car_id"]
    tok = client.post(f"{API}/auth/login", json={"phone": out["phone"], "password": out["password"]}).json()["token"]
    h = {"Authorization": f"Bearer {tok}"}
    alerts = client.get(f"{API}/me/alerts", headers=h).json()
    assert alerts["papers"] == 1 and alerts["prices"] == 1 and alerts["maintenance"] >= 1
    car = client.get(f"{API}/me/vehicles", headers=h).json()[0]
    assert car["nickname"].startswith("[DÉMO]") and car["maintenance_items"]
    hist = client.get(f"{API}/me/vehicles/{car['id']}/maintenance/history", headers=h).json()
    assert len(hist["visits"]) == 3 and any(v["shop"] for v in hist["visits"])
    assert client.get(f"{API}/me/part-requests", headers=h).json()[0]["answered"] == 1
    assert client.get(f"{API}/shops/{out['shop_id']}").json()["reviews"]["found"] >= 1
    assert any(g["id"] == out["garage_id"] for g in client.get(f"{API}/garages/recommend").json())
    # Purge : le compte de démonstration disparaît avec les magasins fictifs ; on les remet pour les autres tests
    from app.seed import purge_demo, run as seed_run
    purge_demo(db)
    db.commit()
    assert db.scalar(select(User).where(User.phone == demo_soutenance.PHONE)) is None
    assert db.scalar(select(Shop).where(Shop.name == demo_soutenance.GARAGE)) is None
    seed_run(db, demo=True)


# --- Démarrage : imports de transformers résolus avant le chargement en parallèle (défaut du 28/11/2026) ---------------

def test_imports_resolus_avant_le_chargement_en_parallele(monkeypatch):
    import app.main as main
    from app.config import get_settings
    from app.services.diagnosis import embeddings
    order: list[str] = []
    monkeypatch.setattr(get_settings(), "retrieval_mode", "hybrid")
    monkeypatch.setattr(embeddings, "preimport", lambda: order.append("preimport"))
    monkeypatch.setattr(embeddings, "get_embedder", lambda: order.append("embedder") or object())
    monkeypatch.setattr(embeddings, "get_reranker", lambda: order.append("reranker"))   # absent : signalé
    main.warmup()
    assert order[0] == "preimport" and {"embedder", "reranker"} <= set(order)
    assert main.MODELS == {"embedder": True, "reranker": False}
    main.MODELS.clear()


# --- Mise en ligne : adresse réelle du client derrière le frontal, réglages de production ------------------------------

def test_adresse_du_client_derriere_le_frontal(client):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.security import client_hash, client_ip
    relais = TestClient(app, client=("127.0.0.1", 50000))        # le relais du site, sur le serveur
    direct = TestClient(app, client=("41.200.0.9", 50000))      # une adresse d'Internet
    seen = {}

    @app.get("/__ip_test")
    def _ip(request: __import__("fastapi").Request):
        return {"ip": client_ip(request), "hash": client_hash(request)}
    try:
        a = relais.get("/__ip_test", headers={"X-Real-IP": "41.100.1.1"}).json()
        b = relais.get("/__ip_test", headers={"X-Real-IP": "41.100.1.2"}).json()
        c = direct.get("/__ip_test", headers={"X-Real-IP": "41.100.1.1"}).json()   # en-tête forgé : ignoré
        d = relais.get("/__ip_test").json()
        seen.update(a=a, b=b, c=c, d=d)
    finally:
        app.router.routes = [r for r in app.router.routes if getattr(r, "path", "") != "/__ip_test"]
    assert seen["a"]["ip"] == "41.100.1.1" and seen["a"]["hash"] != seen["b"]["hash"]   # deux clients distincts
    assert seen["c"]["ip"] == "41.200.0.9" and seen["d"]["ip"] == "127.0.0.1"


def test_limite_d_essais_par_vrai_client_derriere_le_relais():
    from fastapi import HTTPException
    from starlette.requests import Request
    from app.security import RateLimiter

    def req(real):
        return Request({"type": "http", "client": ("10.0.0.5", 1), "headers": [(b"x-real-ip", real.encode())]})
    lim = RateLimiter(2)
    lim(req("41.1.1.1")); lim(req("41.1.1.1"))
    lim(req("41.1.1.2"))                     # un autre client derrière le même relais n'est pas bloqué
    try:
        lim(req("41.1.1.1"))
        raise AssertionError("troisième essai du même client accepté")
    except HTTPException as e:
        assert e.status_code == 429


def test_reglages_de_production_refuses():
    from app.config import DEV_SECRET, Settings, production_problems
    bad = Settings(jwt_secret=DEV_SECRET, otp_test_code="424242", database_url="sqlite:///x.db")
    assert len(production_problems(bad)) == 3
    good = Settings(jwt_secret="x" * 48, otp_test_code="", database_url="postgresql+psycopg2://dalil:Long-Secret@db/dalil")
    assert production_problems(good) == []
