"""Référentiel véhicules complété le 18/11/2026 (data/scripts/build_vehicles.py) : contrôles de cohérence."""
import json
from collections import Counter
from pathlib import Path

from sqlalchemy import func, select

from app.config import get_settings
from app.models import Brand, Model, VehicleVariant
from app.seed import seed_vehicles

DATA = json.loads((Path(get_settings().data_dir) / "seed" / "vehicles.json").read_text(encoding="utf-8"))

# Marques de plus de 0,15 % du parc national (ONS, parc au 31/12/2020, tableau 7)
MARQUES_ONS = ["Peugeot", "Renault", "Volkswagen", "Toyota", "Hyundai", "Dacia", "Fiat", "Chevrolet", "Citroën",
               "Mazda", "Mitsubishi", "Ford", "Mercedes", "Seat", "Daewoo", "Honda", "Nissan", "Kia", "Isuzu", "Audi",
               "BMW", "Land Rover", "Opel"]


def test_marques_du_parc_presentes():
    noms = {b["name"] for b in DATA["brands"]}
    assert not [m for m in MARQUES_ONS if m not in noms]


def test_noms_uniques_et_annees_coherentes():
    assert len({b["name"] for b in DATA["brands"]}) == len(DATA["brands"])
    for b in DATA["brands"]:
        doublons = [n for n, c in Counter(m["name"].lower() for m in b["models"]).items() if c > 1]
        assert not doublons, (b["name"], doublons)
        for m in b["models"]:
            assert m["variants"], (b["name"], m["name"])
            for v in m["variants"]:
                assert 1950 <= v["year_from"] <= 2027, (b["name"], m["name"], v)
                assert v["year_to"] is None or v["year_from"] <= v["year_to"], (b["name"], m["name"], v)
                assert v["fuel"] in {"essence", "diesel", "gpl", "hybride", "electrique", "inconnu"}, v


def test_chaque_ajout_porte_sa_source():
    for b in DATA["brands"]:
        for m in b["models"]:
            for v in m["variants"]:
                if v.get("a_verifier"):
                    assert v.get("source"), (b["name"], m["name"], v)


def test_modeles_courants_en_algerie():
    noms = {(b["name"], m["name"]) for b in DATA["brands"] for m in b["models"]}
    for attendu in [("Renault", "Clio 4"), ("Renault", "Clio 2"), ("Renault", "R19"), ("Peugeot", "405"), ("Peugeot", "Partner"),
                    ("Geely", "Coolray"), ("Livan", "X3 Pro"), ("Seat", "Ibiza"), ("Chevrolet", "Aveo"), ("Citroën", "C3"),
                    ("Toyota", "Hiace"), ("Mazda", "B2500"), ("Lada", "Niva"), ("Suzuki", "Maruti 800")]:
        assert attendu in noms, attendu


def test_rechargement_garde_les_identifiants(db):
    """Les produits des magasins et les compatibilités pointent sur les motorisations : un nouveau chargement du
    référentiel ne doit ni les renuméroter ni les dupliquer."""
    avant = dict(db.execute(select(VehicleVariant.id, VehicleVariant.engine)).all())
    seed_vehicles(db)
    db.commit()
    apres = dict(db.execute(select(VehicleVariant.id, VehicleVariant.engine)).all())
    assert avant == apres
    n_modeles = db.scalar(select(func.count()).select_from(Model))
    assert n_modeles == sum(len(b["models"]) for b in DATA["brands"])
    assert db.scalar(select(func.count()).select_from(Brand)) == len(DATA["brands"])


def test_motorisation_inconnue_ne_penalise_aucune_panne(db, client):
    from app.services.diagnosis.pipeline import DiagnosisInput, run_diagnosis

    v = db.scalar(select(VehicleVariant).where(VehicleVariant.fuel == "inconnu"))
    r, _ = run_diagnosis(db, DiagnosisInput(text="mon diesel démarre très mal le matin, voyant de préchauffage", variant_id=v.id))
    assert r["causes"] and r["causes"][0]["fault"] == "prechauffage-hs"
    label = client.get("/api/v1/vehicles/variants", params={"model_id": v.model_id}).json()
    assert all("inconnu" not in x["label"] for x in label)


def test_modeles_les_plus_courants_d_abord(client):
    renault = next(b for b in client.get("/api/v1/vehicles/brands").json() if b["name"] == "Renault")
    noms = [m["name"] for m in client.get("/api/v1/vehicles/models", params={"brand_id": renault["id"]}).json()]
    assert noms.index("Clio 4") < noms.index("Laguna 1")  # 6 050 annonces contre quelques centaines


def test_recherche_par_saisie(client):
    r = client.get("/api/v1/vehicles/search", params={"q": "clio 2"}).json()
    assert r and r[0]["brand"] == "Renault" and r[0]["model"] == "Clio 2"
    r = client.get("/api/v1/vehicles/search", params={"q": "coolray"}).json()
    assert r[0]["model"] == "Coolray"
    assert client.get("/api/v1/vehicles/search", params={"q": "zzzz"}).json() == []


def test_vehicule_absent_enregistre_et_compte(client, admin_headers):
    body = {"brand": "Zastava", "model": "Yugo", "year": 1988, "engine": "1.1"}
    assert client.post("/api/v1/vehicles/requests", json=body).status_code == 201
    assert client.post("/api/v1/vehicles/requests", json={"brand": "", "model": "x"}).status_code == 422
    m = client.get("/api/v1/admin/metrics", headers=admin_headers).json()
    assert {"vehicle": "Zastava Yugo", "count": 1} in m["requested_missing_vehicles"]
    assert "top_diagnosed_vehicles" in m
