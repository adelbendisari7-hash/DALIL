"""Source techniconnexion : lecture de fichiers de même structure que la collecte, sans réseau ni vraie donnée."""
import json
import os
import sys
import tempfile
from pathlib import Path

DATA = Path(__file__).resolve().parents[2]
os.environ.setdefault("DALIL_DATABASE_URL", f"sqlite:///{(Path(tempfile.mkdtemp()) / 'pipeline.db').as_posix()}")
sys.path.insert(0, str(DATA))

import pytest  # noqa: E402

from pipeline.sources import Context  # noqa: E402
from pipeline.sources import techniconnexion as tc  # noqa: E402

TOPICS = [
    # (id, url, section, titre, résolu, section « résolus »)
    (1, "/t1-perte-puissance", "Moteur", "Perte de puissance 307 HDi", False, False),
    (2, "/t2-bruit-frein", "Trains roulants", "Bruit au freinage", True, False),
    (3, "/t3-tuto-distribution", "Moteur", "Remplacement distribution (TUTO)", True, False),
    (4, "/t4-demontage-tableau", "Intérieur", "Démontage du tableau de bord", False, False),
    (5, "/t5-problemes-resolus-moteur-peugeot", "Moteur", "Problèmes résolus et fiches pratiques moteur PEUGEOT", False, True),
    (6, "/t6-clim", "Intérieur", "clim qui fuit a l'interieur", False, False),
]
POSTS = [
    # (topic, index, auteur, rang, html)
    (1, 0, "Jean_Dupont", "Nouveau", "Ma 307 HDi n'avance plus en côte, voyant moteur. Écrivez-moi : jean.dupont@mail.fr "
                                       "ou au 06 12 34 56 78"),
    (1, 1, "pro_meca", "Tech-admin", "Passe la valise, ça peut être le turbo ou la vanne EGR"),
    (1, 2, "Jean_Dupont", "Nouveau", "<blockquote><div><cite>pro_meca a écrit:</cite>ça peut être le turbo</div></blockquote>"
                                       "Merci pro_meca, c'était bien la vanne EGR encrassée, tout marche"),
    (1, 3, "modo", "Tech-modo", "Salut, merci pour le retour d'infos<br/>Sujet répertorié ici : "
                                "https://www.techniconnexion.com/t5-problemes-resolus-moteur-peugeot"),
    (2, 0, "kader31", "Nouveau", "Ça grince fort quand je freine depuis une semaine, plaque AB-123-CD"),
    (2, 1, "autre", "Petit mécano", "Regarde l'embrayage"),
    (2, 2, "pro_meca", "Tech-d'honneur", "Les plaquettes avant sont mortes, change les plaquettes"),
    (3, 0, "pro_meca", "Tech-admin", "Voici la procédure.<br/>Fichiers joints<br/>distri.pdf<br/>"
                                     "Vous n'avez pas la permission de télécharger les fichiers joints.<br/>(191 Ko) Téléchargé 21 fois"),
    (4, 0, "lea", "Nouveau", "Comment on démonte le tableau de bord ? J'ai un souci de compteur"),
    (5, 0, "modo", "Tech-admin", '<a href="/t1-perte-puissance">perte de puissance</a>'),
    (6, 0, "nadia", "Nouveau", "La clim fuit dans l'habitacle côté passager"),
]


@pytest.fixture()
def folder(tmp_path, monkeypatch):
    with (tmp_path / "dataset_full.jsonl").open("w", encoding="utf-8") as f:
        for tid, url, sub, title, res, sec in TOPICS:
            f.write(json.dumps({"topic_id": tid, "topic_url": url, "subsystem": sub, "symptom_title": title,
                                "is_resolved": res, "is_resolved_section": sec, "brand": "Peugeot", "model": "307",
                                "fuel_type": "Diesel", "year": "2004", "brand_group": "PEUGEOT_CITROEN"}) + "\n")
    with (tmp_path / "posts_with_metadata.jsonl").open("w", encoding="utf-8") as f:
        for tid, i, author, rank, html in POSTS:
            text = html.replace("<br/>", "\n")
            f.write(json.dumps({"topic_id": tid, "post_index": i, "author": author, "author_rank": rank,
                                "content_html": f'<div class="content"><div>{html}</div></div>', "content_text": text}) + "\n")
    monkeypatch.setenv("DALIL_TECHNICONNEXION_AUTORISATION", "test")
    return tmp_path


def _collect(folder):
    return {r.id.split(":")[1]: r for r in tc.collect(Context(options={"techniconnexion_dir": str(folder)}, log=lambda m: None))}


def test_verrou_sans_autorisation(folder, monkeypatch):
    monkeypatch.delenv("DALIL_TECHNICONNEXION_AUTORISATION")
    with pytest.raises(SystemExit):
        list(tc.collect(Context(options={"techniconnexion_dir": str(folder)})))


def test_solution_de_l_auteur_sans_la_citation(folder):
    r = _collect(folder)["1"]
    assert r.family == "gestion-moteur" and r.label_quality == "solution+domaine"   # la question ne nomme pas l'EGR
    assert r.fault  # cause donnée par l'auteur, discussion résolue
    assert r.meta["resolved"] and r.meta["repertorie"] and r.meta["diagnostic"]
    assert "turbo" not in r.meta["solution"]           # citation de l'hypothèse retirée
    assert "Jean_Dupont" not in r.text and "pro_meca" not in r.meta["solution"]
    assert "@" not in r.text and "06 12" not in r.text and "[e-mail]" in r.text


def test_reponses_des_techniciens_comptent_double(folder):
    r = _collect(folder)["2"]
    assert r.family == "freinage" and r.label_quality == "reponses+domaine"   # aucune pièce nommée dans la question : pas d'accord
    assert "AB-123-CD" not in r.text


def test_sujets_hors_panne_ecartes(folder):
    rows = _collect(folder)
    assert not rows["3"].meta["diagnostic"]              # tuto
    assert not rows["4"].meta["diagnostic"]              # procédure
    assert not rows["5"].meta["diagnostic"]              # index « problèmes résolus »
    assert rows["6"].meta["diagnostic"]                  # « fuit » est un symptôme


def test_mentions_du_forum_retirees():
    t = tc.scrub("Voici.\nFichiers joints\ndistri.pdf\nVous n'avez pas la permission de télécharger les fichiers joints.\n"
                 "(191 Ko) Téléchargé 21 fois")
    assert t == "Voici."
