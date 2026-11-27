"""Import OpenStreetMap : brouillons jamais recommandés, rejouable, liste de visite réimportable."""
from openpyxl import load_workbook
from sqlalchemy import select

from app.import_osm import run
from app.models import PartCategory, Shop
from app.services.imports import import_shops, read_table

CSV = """name;phone;lat;lng;address;hours;shop_type;source;osm_id
Pièces auto Test OSM;;35.6975;-0.6300;Rue X Oran;;pieces;osm;node/999000001
Sans nom (OSM node/999000002);;35.8557;-0.3103;;;garage;osm;node/999000002
Très loin;;36.9;3.0;;;pieces;osm;node/999000003
"""


def test_plusieurs_numeros_et_meme_telephone(db, tmp_path):
    src = tmp_path / "osm.csv"
    src.write_text("""name;phone;lat;lng;address;hours;shop_type;source;osm_id
SARL Test GPL;041274367 / 0661999001 / 0660999002;35.70;-0.63;;;pieces;osm;node/999100001
Accessoires Test;0542999003;35.7291;-0.5740;;;pieces;osm;node/999100002
Boulevard Test;0542999003;35.7253;-0.5735;;;pieces;osm;node/999100003
Auto Test;;35.71;-0.62;0792999004;;pieces;osm;node/999100004
""", encoding="utf-8")
    res = run(db, src, tmp_path / "liste.xlsx")
    assert not res["erreurs"] and res["crees"] == 3 and res["mis_a_jour"] == 1
    moved = db.scalar(select(Shop).where(Shop.osm_id == "node/999100004"))
    assert moved.phone.endswith("792999004") and not moved.address    # numéro saisi dans l'adresse sur OSM
    gpl = db.scalar(select(Shop).where(Shop.osm_id == "node/999100001"))
    assert gpl.phone.endswith("661999001")                      # premier mobile valide, le fixe est écarté
    first = db.scalar(select(Shop).where(Shop.osm_id == "node/999100002"))
    assert first is not None and first.lat == 35.7291           # le second point n'écrase ni l'identifiant ni la position
    assert len(res["a_verifier"]) == 1 and "node/999100003" in res["a_verifier"][0]["note"]
    ws = load_workbook(tmp_path / "liste.xlsx")["À visiter"]
    col = [c.value for c in ws[1]].index("Remarques") + 1
    remarks = {ws.cell(row=r, column=7).value: ws.cell(row=r, column=col).value for r in range(2, ws.max_row + 1)}
    assert remarks["node/999100003"].startswith("À vérifier : même téléphone")


def test_import_osm_brouillons_rejouable_et_liste(db, client, tmp_path):
    src = tmp_path / "osm.csv"
    src.write_text(CSV, encoding="utf-8")
    liste = tmp_path / "liste.xlsx"
    res = run(db, src, liste)
    assert res["crees"] == 3 and not res["erreurs"] and res["sans_commune"] == 1   # Alger : hors de toute commune d'Oran
    shop = db.scalar(select(Shop).where(Shop.osm_id == "node/999000001"))
    assert shop.status == "draft" and shop.source == "osm" and shop.commune_id is not None

    again = run(db, src, liste)                                   # rejouable : aucune fiche en double
    assert again["crees"] == 0 and again["mis_a_jour"] == 3

    ws = load_workbook(liste)["À visiter"]
    header = [c.value for c in ws[1]]
    assert ws.max_row == 4 and header[0] == "Commune" and "Marques" in header
    assert ws.cell(row=2, column=6).hyperlink.target.startswith("https://www.openstreetmap.org/")

    # liste remplie sur le terrain puis réimportée : la fiche est complétée, toujours en brouillon
    row = next(r for r in range(2, 5) if ws.cell(row=r, column=7).value == "node/999000001")
    ws.cell(row=row, column=header.index("Téléphone") + 1, value="0550123456")
    ws.cell(row=row, column=header.index("Origine des pièces") + 1, value="origine;adaptable")
    ws.cell(row=row, column=header.index("Enquêteur") + 1, value="équipe")
    cat = db.scalar(select(PartCategory).where(PartCategory.slug == "plaquettes-avant"))
    ws.cell(row=row, column=header.index("Familles") + 1, value=cat.slug)
    filled = tmp_path / "remplie.xlsx"
    ws.parent.save(filled)
    rep = import_shops(db, read_table(filled.read_bytes(), "remplie.xlsx"), default_source="osm")
    db.commit()
    assert not rep.errors and rep.created == 0
    db.refresh(shop)
    assert shop.phone and shop.phone.endswith("550123456") and shop.parts_origin == ["adaptable", "origine"]
    assert shop.status == "draft" and shop.surveyor == "équipe"

    # un brouillon n'est jamais recommandé ; il l'est une fois vérifié par l'équipe
    def recommended():
        r = client.get("/api/v1/shops/recommend", params={"category_id": cat.id, "lat": 35.6975, "lng": -0.63})
        assert r.status_code == 200, r.text
        return {s["id"] for s in r.json()}
    assert shop.id not in recommended()
    shop.status = "verified"
    db.commit()
    assert shop.id in recommended()
