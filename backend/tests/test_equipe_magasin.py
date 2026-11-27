"""Plan côté magasin, phase 3 : l'équipe du magasin. Le gérant ajoute autant d'employés qu'il veut, coche leurs
accès, suspend, retire, passe la main ; l'équipe DALIL (administrateur) n'a aucun droit sur l'équipe."""
import pytest
from sqlalchemy import select

from app.models import PartCategory, PartRequest, RequestResponse, Shop

API = "/api/v1"


def _account(client, phone, first="Employé"):
    r = client.post(f"{API}/auth/register", json={"first_name": first, "last_name": "Test", "phone": phone,
                                                  "password": "equipe-123", "consent": True})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture()
def shop(client, db):
    """Un magasin avec son gérant, un produit, et une demande de client en attente."""
    n = shop.counter = getattr(shop, "counter", 0) + 1
    manager = _account(client, f"06900{n:05d}", "Gérant")
    client.patch(f"{API}/auth/me", headers=manager, json={"role": "shop_owner"})
    sid = client.post(f"{API}/shops", headers=manager, json={"name": f"Équipe {n}", "lat": 35.7, "lng": -0.63}).json()["id"]
    cat = db.scalar(select(PartCategory).where(PartCategory.slug == "plaquettes-avant")).id
    pid = client.post(f"{API}/shops/{sid}/products", headers=manager, json={"title": "Plaquettes", "category_id": cat,
                                                                             "price": 4000}).json()["id"]
    req = PartRequest(category_id=cat)
    db.add(req)
    db.flush()
    db.add(RequestResponse(request_id=req.id, shop_id=sid))
    db.commit()
    return {"id": sid, "manager": manager, "product": pid, "request": req.id, "cat": cat, "n": n}


def _add(client, shop, phone, permissions=None):
    h = _account(client, phone)
    body = {"phone": phone} if permissions is None else {"phone": phone, "permissions": permissions}
    r = client.post(f"{API}/shops/{shop['id']}/team", headers=shop["manager"], json=body)
    assert r.status_code == 201, r.text
    return h, r.json()["user_id"]


def test_vendeur_par_defaut_repond_et_change_les_prix_mais_rien_d_autre(client, shop):
    sid = shop["id"]
    vendeur, _ = _add(client, shop, f"07910{shop['n']:05d}")
    mine = client.get(f"{API}/shops/mine", headers=vendeur).json()
    assert mine[0]["id"] == sid and mine[0]["my_role"] == "employee" and mine[0]["my_permissions"] == ["requests", "prices"]
    # Autorisé : répondre à une demande, changer prix et stock
    assert client.get(f"{API}/part-requests/inbox", headers=vendeur).json()[0]["request_id"] == shop["request"]
    assert client.post(f"{API}/part-requests/{shop['request']}/responses?shop_id={sid}", headers=vendeur,
                       json={"available": True, "price": 4200}).status_code == 200
    assert client.patch(f"{API}/shops/{sid}/products/{shop['product']}", headers=vendeur, json={"in_stock": False}).status_code == 200
    # Refusé : ajouter ou supprimer un produit, modifier la fiche, voir ou gérer l'équipe
    assert client.post(f"{API}/shops/{sid}/products", headers=vendeur, json={"title": "Filtre", "category_id": shop["cat"]}).status_code == 403
    assert client.delete(f"{API}/shops/{sid}/products/{shop['product']}", headers=vendeur).status_code == 403
    assert client.patch(f"{API}/shops/{sid}", headers=vendeur, json={"name": "Piraté"}).status_code == 403
    assert client.get(f"{API}/shops/{sid}/team", headers=vendeur).status_code == 403
    assert client.post(f"{API}/shops/{sid}/team", headers=vendeur, json={"phone": "0791099999"}).status_code == 403


@pytest.mark.parametrize("perm, call", [
    ("products", lambda c, s, h: c.post(f"{API}/shops/{s['id']}/products", headers=h, json={"title": "Filtre", "category_id": s["cat"]})),
    ("products_delete", lambda c, s, h: c.delete(f"{API}/shops/{s['id']}/products/{s['product']}", headers=h)),
    ("profile", lambda c, s, h: c.patch(f"{API}/shops/{s['id']}", headers=h, json={"landmark": "à côté de la poste"})),
    ("prices", lambda c, s, h: c.patch(f"{API}/shops/{s['id']}/products/{s['product']}", headers=h, json={"price": 1})),
    ("requests", lambda c, s, h: c.post(f"{API}/part-requests/{s['request']}/responses?shop_id={s['id']}", headers=h, json={"available": False})),
])
def test_chaque_acces_coche_ou_non(client, shop, perm, call):
    """Un accès par case : sans la case, refusé ; le gérant coche, autorisé."""
    h, uid = _add(client, shop, f"07920{shop['n']:05d}", permissions=[])
    assert call(client, shop, h).status_code == 403
    assert client.patch(f"{API}/shops/{shop['id']}/team/{uid}", headers=shop["manager"], json={"permissions": [perm]}).status_code == 200
    assert call(client, shop, h).status_code in (200, 201, 204)


def test_suspendu_puis_retire_perd_l_acces_tout_de_suite(client, shop):
    sid = shop["id"]
    h, uid = _add(client, shop, f"07930{shop['n']:05d}")
    assert client.patch(f"{API}/shops/{sid}/products/{shop['product']}", headers=h, json={"price": 10}).status_code == 200
    client.patch(f"{API}/shops/{sid}/team/{uid}", headers=shop["manager"], json={"status": "suspended"})
    assert client.patch(f"{API}/shops/{sid}/products/{shop['product']}", headers=h, json={"price": 11}).status_code == 403
    assert client.get(f"{API}/shops/mine", headers=h).json() == []
    client.patch(f"{API}/shops/{sid}/team/{uid}", headers=shop["manager"], json={"status": "active"})
    assert client.patch(f"{API}/shops/{sid}/products/{shop['product']}", headers=h, json={"price": 12}).status_code == 200
    assert client.delete(f"{API}/shops/{sid}/team/{uid}", headers=shop["manager"]).status_code == 204
    assert client.patch(f"{API}/shops/{sid}/products/{shop['product']}", headers=h, json={"price": 13}).status_code == 403


def test_l_administrateur_dalil_ne_touche_pas_a_l_equipe(client, shop, admin_headers):
    sid = shop["id"]
    _, uid = _add(client, shop, f"07940{shop['n']:05d}")
    assert client.get(f"{API}/shops/{sid}/team", headers=admin_headers).status_code == 403
    assert client.post(f"{API}/shops/{sid}/team", headers=admin_headers, json={"phone": "0550000099"}).status_code == 403
    assert client.patch(f"{API}/shops/{sid}/team/{uid}", headers=admin_headers, json={"permissions": []}).status_code == 403
    assert client.delete(f"{API}/shops/{sid}/team/{uid}", headers=admin_headers).status_code == 403
    assert client.get(f"{API}/shops/{sid}/team/activity", headers=admin_headers).status_code == 403
    paths = [r.path for r in client.app.routes if hasattr(r, "path")]
    assert not [p for p in paths if p.startswith("/api/v1/admin") and ("team" in p or "member" in p)]


def test_ajout_refuse_sans_compte_ou_en_double(client, shop):
    sid = shop["id"]
    r = client.post(f"{API}/shops/{sid}/team", headers=shop["manager"], json={"phone": f"07950{shop['n']:05d}"})
    assert r.status_code == 404 and "créer son compte" in r.json()["detail"]
    _add(client, shop, f"07960{shop['n']:05d}")
    again = client.post(f"{API}/shops/{sid}/team", headers=shop["manager"], json={"phone": f"07960{shop['n']:05d}"})
    assert again.status_code == 409
    assert client.post(f"{API}/shops/{sid}/team", headers=shop["manager"], json={"phone": f"07960{shop['n']:05d}",
                                                                              "permissions": ["tout"]}).status_code == 422


def test_sans_limite_d_employes(client, shop):
    for i in range(12):
        _add(client, shop, f"0797{shop['n']:02d}{i:04d}")
    assert len(client.get(f"{API}/shops/{shop['id']}/team", headers=shop["manager"]).json()["members"]) == 12


def test_passer_la_main(client, shop, db):
    sid = shop["id"]
    h, uid = _add(client, shop, f"07980{shop['n']:05d}")
    assert client.post(f"{API}/shops/{sid}/team/transfer", headers=shop["manager"],
                       json={"user_id": uid, "password": "faux"}).status_code == 403
    r = client.post(f"{API}/shops/{sid}/team/transfer", headers=shop["manager"], json={"user_id": uid, "password": "equipe-123"})
    assert r.status_code == 200
    db.expire_all()
    assert db.get(Shop, sid).owner_user_id == uid
    assert client.get(f"{API}/shops/{sid}/team", headers=h).status_code == 200           # nouveau gérant
    assert client.get(f"{API}/shops/{sid}/team", headers=shop["manager"]).status_code == 403   # ancien : employé
    old = client.get(f"{API}/shops/mine", headers=shop["manager"]).json()[0]
    assert old["my_role"] == "employee" and "profile" in old["my_permissions"]


def test_journal_qui_a_fait_quoi(client, shop):
    sid = shop["id"]
    h, _ = _add(client, shop, f"07990{shop['n']:05d}")
    client.post(f"{API}/part-requests/{shop['request']}/responses?shop_id={sid}", headers=h, json={"available": True, "price": 3900})
    client.patch(f"{API}/shops/{sid}/products/{shop['product']}", headers=h, json={"price": 4100})
    log = client.get(f"{API}/shops/{sid}/team/activity", headers=shop["manager"]).json()
    actions = [(x["who"], x["action"]) for x in log]
    assert ("Employé Test", "request.answer") in actions and ("Employé Test", "product.quick") in actions
    assert ("Gérant Test", "team.add") in actions and ("Gérant Test", "product.create") in actions
    answer = next(x for x in log if x["action"] == "request.answer")
    assert "disponible" in answer["target"] and "3900 DA" in answer["target"]


def test_compte_supprime_quitte_l_equipe(client, shop):
    h, _ = _add(client, shop, f"07990{shop['n'] + 50:05d}")
    assert client.delete(f"{API}/auth/me", headers=h).status_code == 204
    assert client.get(f"{API}/shops/{shop['id']}/team", headers=shop["manager"]).json()["members"] == []
