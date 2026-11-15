import io

from openpyxl import Workbook
from sqlalchemy import select

from app.models import Brand, Model, PartCategory, Shop, ShopCategory, VehicleVariant
from tests.conftest import login

API = "/api/v1"


def variant_id(db, brand, model, engine, year):
    return db.scalar(
        select(VehicleVariant.id).join(Model).join(Brand)
        .where(Brand.name == brand, Model.name == model, VehicleVariant.engine == engine,
               VehicleVariant.year_from <= year)
        .where((VehicleVariant.year_to.is_(None)) | (VehicleVariant.year_to >= year))
    )


def cat_id(db, slug):
    return db.scalar(select(PartCategory.id).where(PartCategory.slug == slug))


# --- Étape 3 : référentiels -----------------------------------------------

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_vehicle_selection(client):
    brands = client.get(f"{API}/vehicles/brands").json()
    names = [b["name"] for b in brands]
    for b in ("Dacia", "Renault", "Hyundai", "Peugeot", "Kia"):
        assert b in names
    dacia = next(b for b in brands if b["name"] == "Dacia")
    logan = next(m for m in client.get(f"{API}/vehicles/models", params={"brand_id": dacia["id"]}).json() if m["name"] == "Logan")
    assert logan["pilot"] is True
    variants = client.get(f"{API}/vehicles/variants", params={"model_id": logan["id"], "year": 2015}).json()
    assert {v["engine"] for v in variants} == {"1.2 16V", "1.5 dCi"}


def test_dtc_p0420_en_francais(client):
    r = client.get(f"{API}/dtc/P0420").json()
    assert r["title_fr"].startswith("Efficacité du catalyseur")
    assert r["parts"][0]["slug"] == "catalyseur"
    assert client.get(f"{API}/dtc/p0420").status_code == 200
    assert client.get(f"{API}/dtc/P9999").status_code == 404


def test_recherche_plaquettes(client):
    r = client.get(f"{API}/parts/search", params={"q": "plaquettes"}).json()
    assert r[0]["slug"] in ("plaquettes-avant", "plaquettes-arriere")
    r = client.get(f"{API}/parts/search", params={"q": "plaquete"}).json()  # faute de frappe
    assert r[0]["slug"].startswith("plaquettes")
    r = client.get(f"{API}/parts/search", params={"q": "calorstat"}).json()  # synonyme
    assert r[0]["slug"] == "thermostat"


def test_taxonomie_deux_niveaux(client):
    tree = client.get(f"{API}/parts/categories").json()
    assert all(f["children"] for f in tree)
    pilots = [c for f in tree for c in f["children"] if c["pilot"]]
    assert len(pilots) >= 20


# --- Étape 5 : recommandation ---------------------------------------------

def test_recommandation_raisons_et_ordre(client, db):
    vid = variant_id(db, "Dacia", "Logan", "1.5 dCi", 2015)
    r = client.get(f"{API}/shops/recommend", params={
        "category_id": cat_id(db, "plaquettes-avant"), "variant_id": vid, "lat": 35.6971, "lng": -0.6308}).json()
    assert r, "au moins un magasin"
    assert r[0]["breakdown"]["catalog"] == 1.0  # le magasin qui a la pièce au catalogue arrive en tête
    assert "vend Dacia" in r[0]["reasons"]
    assert any(x.startswith("à ") and x.endswith(" km") for x in r[0]["reasons"])
    assert [s["score"] for s in r] == sorted([s["score"] for s in r], reverse=True)


def test_recommandation_categorie_inconnue(client):
    assert client.get(f"{API}/shops/recommend", params={"category_id": 99999}).status_code == 404


# --- Étapes 8 et 11 : diagnostic, contacts, retours -----------------------

def test_diagnostic_et_session(client, db):
    vid = variant_id(db, "Renault", "Symbol", "1.5 dCi", 2016)
    r = client.post(f"{API}/diagnosis", json={"text": "ça grince fort en freinant, bruit de métal", "variant_id": vid}).json()
    assert r["status"] in ("ok", "clarify")
    assert 1 <= len(r["causes"]) <= 3
    assert r["causes"][0]["part"]["slug"] in ("plaquettes-avant", "disques-frein")
    assert r["safety"]["do_not_drive"] is True  # freinage
    assert "pas un diagnostic certifié" in r["disclaimer"]
    got = client.get(f"{API}/diagnosis/{r['session_id']}").json()
    assert got["model_version"]


def test_diagnostic_hors_sujet(client):
    r = client.post(f"{API}/diagnosis", json={"text": "donne moi la recette du gâteau au chocolat"}).json()
    assert r["status"] == "unknown" and r["causes"] == []


def test_diagnostic_vide_refuse(client):
    assert client.post(f"{API}/diagnosis", json={"text": "  "}).status_code == 422
    assert client.post(f"{API}/diagnosis", json={"text": "x", "dtc_codes": ["XYZ"]}).status_code == 422


def test_questions_de_precision(client):
    r = client.post(f"{API}/diagnosis", json={"text": "la température monte et ça chauffe"}).json()
    if r["status"] == "clarify":
        assert 1 <= len(r["questions"]) <= 3
        q = r["questions"][0]
        r2 = client.post(f"{API}/diagnosis/{r['session_id']}/answers", json={"answers": {q["id"]: 0}}).json()
        assert r2["session_id"] == r["session_id"]
        assert q["id"] not in [x["id"] for x in r2["questions"]]


def test_references_jamais_generees(client, db):
    """Toute référence affichée existe en base (section 6.7)."""
    from app.models import PartReference, Product

    known = {r.oem_ref for r in db.scalars(select(PartReference))} | {p.oem_ref for p in db.scalars(select(Product)) if p.oem_ref}
    vid = variant_id(db, "Dacia", "Logan", "1.5 dCi", 2015)
    r = client.post(f"{API}/diagnosis", json={"text": "bruit de ferraille au freinage", "variant_id": vid}).json()
    for c in r["causes"]:
        for ref in c["references"]:
            assert ref["oem_ref"] in known
    assert any(c["reference_level"] >= 2 for c in r["causes"])  # pilote : référence lue en base


def test_contact_et_retour_modifient_le_score(client, db):
    vid = variant_id(db, "Kia", "Picanto", "1.2", 2014)
    cid = cat_id(db, "batterie")
    before = client.get(f"{API}/shops/recommend", params={"category_id": cid, "variant_id": vid}).json()
    target = before[-1]
    assert client.post(f"{API}/contact-events", json={"shop_id": target["id"], "channel": "whatsapp", "category_id": cid}).status_code == 201
    for _ in range(3):
        assert client.post(f"{API}/feedback", json={"shop_id": target["id"], "category_id": cid, "part_found": True}).status_code == 201
    after = {s["id"]: s for s in client.get(f"{API}/shops/recommend", params={"category_id": cid, "variant_id": vid}).json()}
    assert after[target["id"]]["score"] > target["score"]
    db.expire_all()
    sc = db.get(ShopCategory, (target["id"], cid))
    assert sc is not None and sc.source in ("observed", "terrain", "declared")


# --- Connexion et rôles ---------------------------------------------------

def test_otp_mauvais_code_et_roles(client):
    client.post(f"{API}/auth/otp/request", json={"phone": "0661 23 45 67"})
    assert client.post(f"{API}/auth/otp/verify", json={"phone": "0661234567", "code": "000000"}).status_code in (400,)
    h = login(client, "0661234567")
    assert client.get(f"{API}/auth/me", headers=h).json()["role"] == "driver"
    assert client.get(f"{API}/admin/metrics", headers=h).status_code == 403
    assert client.get(f"{API}/admin/metrics").status_code == 401
    assert client.post(f"{API}/auth/otp/request", json={"phone": "12345"}).status_code == 422


# --- Étapes 4 et 10 : back-office et espace magasin ------------------------

def test_admin_saisie_terrain_apparait_sur_la_carte(client, admin_headers, db):
    body = {"name": "Magasin test terrain", "phone": "0770112233", "lat": 35.70, "lng": -0.63,
            "brand_ids": [db.scalar(select(Brand.id).where(Brand.name == "Renault"))],
            "category_ids": [cat_id(db, "freinage")], "survey": {"demandes_par_jour": 20}}
    r = client.post(f"{API}/admin/shops", json=body, headers=admin_headers)
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "verified"
    assert r.json()["id"] in [s["id"] for s in client.get(f"{API}/shops").json()]
    assert client.post(f"{API}/admin/shops", json=body, headers=admin_headers).status_code == 409


def test_admin_import_csv_et_fusion(client, admin_headers):
    csv_text = (
        "name;phone;commune;lat;lng;brands;categories\n"
        "Import A;0770999001;Oran;35.70;-0.62;Renault|Dacia;freinage|filtration\n"
        "Import A bis;0770999001;Bir El Djir;;;Peugeot;embrayage\n"
        "Import B;0770999002;Commune inexistante;;;Renault;freinage\n"
        ";0770999003;Oran;;;Renault;freinage\n"
    )
    r = client.post(f"{API}/admin/shops/import", files={"file": ("shops.csv", csv_text.encode(), "text/csv")}, headers=admin_headers).json()
    assert r["created"] == 1 and r["updated"] == 1
    assert {e["line"] for e in r["errors"]} == {4, 5}
    drafts = client.get(f"{API}/admin/shops", params={"status": "draft", "q": "Import"}, headers=admin_headers).json()
    assert len(drafts) == 1 and len(drafts[0]["brands"]) == 3
    v = client.post(f"{API}/admin/shops/{drafts[0]['id']}/verify", headers=admin_headers).json()
    assert v["status"] == "verified"
    assert client.get(f"{API}/admin/actions", headers=admin_headers).json()[0]["action"] == "shop.verify"


def test_parcours_magasin_inscription_validation_catalogue(client, admin_headers, db):
    h = login(client, "0555443322")
    me = client.patch(f"{API}/auth/me", json={"role": "shop_owner", "consent": True, "name": "Gérant test"}, headers=h).json()
    h = {"Authorization": f"Bearer {me['token']}"}
    body = {"name": "Mon magasin test", "lat": 35.69, "lng": -0.64,
            "brand_ids": [db.scalar(select(Brand.id).where(Brand.name == "Hyundai"))],
            "category_ids": [cat_id(db, "freinage"), cat_id(db, "filtration")]}
    shop = client.post(f"{API}/shops", json=body, headers=h).json()
    assert shop["status"] == "draft" and shop["phone"] == "+213555443322"
    assert shop["id"] not in [s["id"] for s in client.get(f"{API}/shops").json()]  # pas visible avant validation
    client.post(f"{API}/admin/shops/{shop['id']}/verify", headers=admin_headers)

    vid = variant_id(db, "Hyundai", "Accent", "1.4", 2014)
    # 20 produits saisis (critère de l'étape 10)
    for i in range(20):
        r = client.post(f"{API}/shops/{shop['id']}/products", headers=h, json={
            "title": f"Produit test {i}", "category_id": cat_id(db, "plaquettes-avant"), "price": 1000 + i, "variant_ids": [vid]})
        assert r.status_code == 201
    assert len(client.get(f"{API}/shops/{shop['id']}/products").json()) == 20

    # un autre utilisateur ne peut pas modifier ce magasin
    other = login(client, "0555000111")
    assert client.patch(f"{API}/shops/{shop['id']}", json={"name": "pirate"}, headers=other).status_code == 403


def test_import_excel_500_lignes(client, admin_headers, db):
    h = login(client, "0555667788")
    h = {"Authorization": f"Bearer {client.patch(f'{API}/auth/me', json={'role': 'shop_owner'}, headers=h).json()['token']}"}
    shop = client.post(f"{API}/shops", json={"name": "Grossiste test"}, headers=h).json()
    wb = Workbook()
    ws = wb.active
    ws.append(["Titre", "Famille", "Reference", "Marque_piece", "Etat", "Prix", "En_stock", "Compatibilite"])
    fams = ["plaquettes avant", "filtre à huile", "bougies", "amortisseurs", "kit embrayage"]
    for i in range(500):
        ws.append([f"Article {i}", fams[i % 5], f"REF-TEST-{i:04d}", "Marque test", "adaptable", 500 + i, "oui",
                   "Dacia Logan 1.5 dCi 2015; Renault Symbol 2016"])
    buf = io.BytesIO()
    wb.save(buf)
    r = client.post(f"{API}/shops/{shop['id']}/products/import", headers=h,
                    files={"file": ("catalogue.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}).json()
    assert r["errors"] == [] and r["created"] == 500
    # réimport : mise à jour, pas de doublon
    r = client.post(f"{API}/shops/{shop['id']}/products/import", headers=h,
                    files={"file": ("catalogue.xlsx", buf.getvalue(), "application/octet-stream")}).json()
    assert r["updated"] == 500 and r["created"] == 0


def test_revendication_de_fiche(client, admin_headers, db):
    client.post(f"{API}/admin/shops", headers=admin_headers, json={"name": "Fiche à revendiquer", "phone": "0699887766"})
    h = login(client, "0699887766")
    claimable = client.get(f"{API}/shops/claimable", params={"phone": "0699887766"}).json()
    assert len(claimable) == 1
    r = client.post(f"{API}/shops/{claimable[0]['id']}/claim", headers=h).json()
    assert r["status"] == "claimed"
    intruder = login(client, "0699000000")
    assert client.post(f"{API}/shops/{claimable[0]['id']}/claim", headers=intruder).status_code == 409


def test_demande_diffusee(client, admin_headers, db):
    h = login(client, "0699887766")  # propriétaire de la fiche revendiquée, sans marque déclarée
    shop_id = client.get(f"{API}/shops/mine", headers=h).json()[0]["id"]
    client.patch(f"{API}/shops/{shop_id}", headers=h, json={
        "brand_ids": [db.scalar(select(Brand.id).where(Brand.name == "Peugeot"))], "category_ids": [cat_id(db, "distribution")]})
    vid = variant_id(db, "Peugeot", "301", "1.6 HDi", 2015)
    req = client.post(f"{API}/part-requests", json={"category_id": cat_id(db, "kit-distribution"), "variant_id": vid}).json()
    assert req["notified_shops"] >= 1
    inbox = client.get(f"{API}/part-requests/inbox", headers=h).json()
    assert inbox[0]["request_id"] == req["id"]
    r = client.post(f"{API}/part-requests/{req['id']}/responses", params={"shop_id": shop_id}, headers=h, json={"available": True, "price": 19000})
    assert r.status_code == 200
    status = client.get(f"{API}/part-requests/{req['id']}").json()
    assert status["responses"][0]["available"] is True


def test_metrics(client, admin_headers):
    m = client.get(f"{API}/admin/metrics", headers=admin_headers).json()
    assert m["shops"]["total"] > 0 and m["diagnoses"]["total"] > 0 and m["contacts"]["total"] > 0


def test_suppression_compte(client):
    h = login(client, "0777000123")
    assert client.delete(f"{API}/auth/me", headers=h).status_code == 204


def test_magasins_demo_marques(db):
    demo = list(db.scalars(select(Shop).where(Shop.is_demo.is_(True))))
    assert demo and all(s.name.startswith("[DÉMO]") for s in demo)
