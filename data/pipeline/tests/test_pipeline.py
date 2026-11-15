"""Tests du pipeline de données (étape 6), sans réseau.

    cd backend && .venv/Scripts/python -m pytest -q ../data/pipeline/tests
"""
import io
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

DATA = Path(__file__).resolve().parents[2]
os.environ.setdefault("DALIL_DATABASE_URL", f"sqlite:///{(Path(tempfile.mkdtemp()) / 'pipeline.db').as_posix()}")
sys.path.insert(0, str(DATA))

import httpx  # noqa: E402
import pytest  # noqa: E402

from pipeline import common  # noqa: E402
from pipeline.common import Record, ZipMemberStream, read_jsonl, write_jsonl  # noqa: E402
from pipeline.load import LicenseError, chunk_rows, export_training  # noqa: E402
from pipeline.sources import SOURCES  # noqa: E402
from pipeline.taxonomy_map import (  # noqa: E402
    EN_RULES, categories_en, categories_fr, fault_for, family_fr, nhtsa_family, reconcile, taxonomy,
)
from pipeline.translate import glossary_misses, postedit, split_sentences  # noqa: E402


# --- Licences et fiches ------------------------------------------------------

@pytest.mark.parametrize("sid", list(SOURCES))
def test_chaque_source_a_sa_fiche_et_sa_licence(sid):
    spec = SOURCES[sid]
    fiche = DATA / "sources" / f"{sid}.md"
    assert fiche.exists(), f"fiche manquante : {fiche}"
    text = fiche.read_text(encoding="utf-8")
    assert spec.license in text, "la fiche doit citer la licence du registre"
    assert spec.license_url.startswith("http")
    assert sid in (DATA / "SOURCES.md").read_text(encoding="utf-8"), "ligne manquante dans data/SOURCES.md"


def _rec(**kw):
    base = dict(id="nhtsa_complaints:1", source="nhtsa_complaints", kind="complaint", lang="en",
                text="My brake pads are worn and squeal.", license=SOURCES["nhtsa_complaints"].license)
    base.update(kw)
    from dataclasses import asdict
    return asdict(Record(**base))


def test_chargement_refuse_sans_licence():
    with pytest.raises(LicenseError):
        chunk_rows([_rec(license="")])
    with pytest.raises(LicenseError):
        chunk_rows([_rec(license="CC0")])  # différente du registre
    with pytest.raises(LicenseError):
        chunk_rows([_rec(source="forum_inconnu")])


def test_texte_original_garde_a_cote_de_la_traduction():
    row = chunk_rows([_rec(text_fr="Mes plaquettes de frein sont usées.")])[0]
    assert row["lang"] == "fr" and row["text"].startswith("Mes plaquettes")
    assert row["text_original"].startswith("My brake pads")
    row = chunk_rows([_rec()])[0]
    assert row["lang"] == "en" and row["text_original"] is None


# --- Correspondance avec la taxonomie -----------------------------------------

def test_toutes_les_regles_visent_un_slug_existant():
    names = taxonomy()["names"]
    for slug, _ in EN_RULES:
        assert slug in names, slug
    cv = json.loads((DATA / "pipeline" / "sources" / "cvffad_fr.json").read_text(encoding="utf-8"))["faults"]
    faults = {f["slug"] for f in json.loads((DATA / "seed" / "faults.json").read_text(encoding="utf-8"))["faults"]}
    for code, m in cv.items():
        for c in m.get("categories", []):
            assert c in names, (code, c)
        assert m.get("fault") in faults | {None}, (code, m.get("fault"))


@pytest.mark.parametrize("text,expected", [
    ("The front brake pads were worn down to the metal", "plaquettes-avant"),
    ("rear pads squeal", "plaquettes-arriere"),
    ("timing chain rattle at cold start", "kit-distribution"),
    ("serpentine belt squeal", "courroie-accessoires"),
    ("replaced the outer tie rod end", "rotules-direction"),
    ("CV joint clicking when turning", "cardans"),
    ("high pressure fuel pump failed on the highway", "pompe-carburant"),
    ("catalytic converter clogged", "catalyseur"),
    ("Brake disc(s) seriously weakened", "disques-frein"),
])
def test_correspondance_anglais(text, expected):
    assert categories_en(text)[0] == expected


def test_voyant_ou_indicateur_n_est_pas_une_ampoule():
    assert "ampoules" not in categories_en("the check engine light came on and a warning indicator flashed")


@pytest.mark.parametrize("text,cat,fam", [
    ("la pompe à carburant haute pression peut fuir", "pompe-carburant", "alimentation"),
    ("défaut de serrage des étriers de frein", "etrier-frein", "freinage"),
    ("la ceinture de sécurité peut se détacher", None, None),
])
def test_correspondance_francais(text, cat, fam):
    cats, family, _ = reconcile(categories_fr(text), family_fr(text))
    assert (cats[0] if cats else None) == cat
    assert family == fam


def test_reconciliation_avec_le_composant_nhtsa():
    assert nhtsa_family("SERVICE BRAKES, HYDRAULIC:ANTILOCK") == "freinage"
    assert nhtsa_family("ENGINE AND ENGINE COOLING:ENGINE COOLING:RADIATOR") == "refroidissement"
    cats, fam, q = reconcile(["batterie", "plaquettes-avant"], "freinage")
    assert cats == ["plaquettes-avant"] and q == "keyword+component"
    cats, fam, q = reconcile([], "freinage")
    assert cats == [] and fam == "freinage" and q == "component"


def test_panne_type_seulement_si_sans_ambiguite():
    assert fault_for(["plaquettes-avant"], "keyword+component") == "plaquettes-usees"
    assert fault_for(["plaquettes-avant"], "component") is None
    assert fault_for([], "keyword") is None


# --- Traduction ---------------------------------------------------------------

def test_postedition_impose_le_lexique():
    assert postedit("Les tampons de frein et les rotors sont usés") == "Les plaquettes de frein et les disques sont usés"
    assert postedit("le convertisseur catalytique est bouché") == "le catalyseur est bouché"


def test_glossaire_signale_les_termes_mal_traduits():
    assert glossary_misses("worn brake pads", "les tampons sont usés") == ["plaquette"]
    assert glossary_misses("worn brake pads", "les plaquettes sont usées") == []


def test_decoupage_en_phrases():
    parts = split_sentences("First sentence. Second one! " + "x" * 900)
    assert parts[0] == "First sentence." and all(len(p) <= 400 for p in parts)


# --- Lecture en flux d'un zip distant (MOT) -----------------------------------

def test_lecture_en_flux_d_un_zip(monkeypatch):
    payload = ("test_id|make\n" + "".join(f"{i}|DACIA\n" for i in range(20000))).encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("test_result.csv", payload)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=buf.getvalue()))
    monkeypatch.setattr(common, "client", lambda: httpx.Client(transport=transport))
    stream = io.BufferedReader(ZipMemberStream("https://exemple.test/x.zip"))
    assert stream.raw.member_name == "test_result.csv"
    assert stream.read() == payload


def test_reprise_apres_coupure_reseau(monkeypatch):
    payload = "".join(f"{i}|ligne de test assez longue pour faire plusieurs blocs\n" for i in range(60000)).encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("test_item.csv", payload)
    data = buf.getvalue()
    calls = []

    class CutStream(httpx.SyncByteStream):
        def __iter__(self):
            yield data[:len(data) // 3]
            raise httpx.RemoteProtocolError("peer closed connection")

    def handler(request):
        rng = request.headers.get("range")
        calls.append(rng)
        if rng is None:
            return httpx.Response(200, stream=CutStream())
        start = int(rng.split("=")[1].rstrip("-"))
        return httpx.Response(206, content=data[start:])

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(common, "client", lambda: httpx.Client(transport=transport))
    monkeypatch.setattr(common.time, "sleep", lambda s: None)
    stream = io.BufferedReader(ZipMemberStream("https://exemple.test/y.zip"))
    assert stream.read() == payload
    assert calls == [None, f"bytes={len(data) // 3}-"]


# --- Export d'entraînement ---------------------------------------------------

def test_export_entrainement_exclut_stats_rappels_et_procedures(tmp_path, monkeypatch):
    import pipeline.load as load

    monkeypatch.setattr(load, "PROCESSED", tmp_path)
    src = tmp_path / "x.jsonl"
    write_jsonl(src, [
        _rec(id="a", categories=["plaquettes-avant"], family="freinage"),
        _rec(id="b", kind="recall", categories=["plaquettes-avant"]),
        _rec(id="c", kind="stat", categories=["ampoules"]),
        _rec(id="d", kind="qa", categories=["batterie"], meta={"diagnostic": False}),
        _rec(id="e", categories=[], family=None),
    ])
    assert export_training("x", src) == 1
    assert [r["id"] for r in read_jsonl(tmp_path / "train" / "x.jsonl")] == ["a"]


def test_texte_en_capitales_remis_en_casse_normale():
    from pipeline.translate import prepare

    assert prepare("THE ABS LIGHT CAME ON. I TOOK IT TO THE DEALER.") == "The ABS light came on. I took it to the dealer."
    assert prepare("Normal text, ABS kept.") == "Normal text, ABS kept."
