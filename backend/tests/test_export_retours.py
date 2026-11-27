"""Retours « ce diagnostic était-il juste ? » -> vrais exemples candidats (python -m app.export_retours)."""
import json

from sqlalchemy import select

from app import export_retours
from app.models import PartCategory

API = "/api/v1"


def _diag(client, text):
    r = client.post(f"{API}/diagnosis", json={"text": text, "dtc_codes": []})
    assert r.status_code == 200, r.text
    return r.json()


def _cat(db, slug):
    return db.scalar(select(PartCategory).where(PartCategory.slug == slug)).id


def test_retours_deviennent_des_exemples(client, db, tmp_path, monkeypatch):
    oui = _diag(client, "ça grince fort quand je freine depuis une semaine")
    first = oui["causes"][0]
    assert client.post(f"{API}/feedback", json={"session_id": oui["session_id"], "diagnosis_correct": True,
                                                 "category_id": first["part"]["category_id"]}).status_code == 201
    non = _diag(client, "la voiture ne démarre pas le matin, elle tousse puis s'arrête")
    assert client.post(f"{API}/feedback", json={
        "session_id": non["session_id"], "diagnosis_correct": False, "category_id": _cat(db, "batterie"),
        "comment": "Le mécanicien a changé la batterie, appelez-moi au 0550 12 34 56 ou ali@exemple.dz"}).status_code == 201
    inconnu = _diag(client, "bruit bizarre à l'arrière sur les bosses")
    client.post(f"{API}/feedback", json={"session_id": inconnu["session_id"], "diagnosis_correct": False})

    rows, stats = export_retours.export(db)
    by_id = {r["id"]: r for r in rows}
    a, b = by_id[f"retour:{oui['session_id']}"], by_id[f"retour:{non['session_id']}"]
    assert a["correct"] is True and a["fault"] == first["fault"] and a["part"] == first["part"]["slug"]
    assert b["correct"] is False and b["part"] == "batterie" and b["fault"] == "batterie-faible"
    assert "0550" not in b["comment"] and "@" not in b["comment"] and "[numéro]" in b["comment"]
    assert f"retour:{inconnu['session_id']}" not in by_id and stats["sans_piece"] >= 1
    assert all(r["verifie"] is False for r in rows)

    out = tmp_path / "retours.jsonl"
    monkeypatch.setattr("sys.argv", ["export_retours", "--out", str(out)])
    export_retours.main()
    once = out.read_text(encoding="utf-8")
    export_retours.main()   # rejouable : même sortie
    assert out.read_text(encoding="utf-8") == once
    assert all("client_hash" not in json.loads(l) for l in once.splitlines())


def test_retour_refuse_une_piece_ou_un_diagnostic_inconnu(client):
    assert client.post(f"{API}/feedback", json={"diagnosis_correct": False, "category_id": 999999}).status_code == 404
    assert client.post(f"{API}/feedback", json={"diagnosis_correct": True, "session_id": 999999}).status_code == 404
