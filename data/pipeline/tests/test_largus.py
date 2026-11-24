"""Source largus_forum : lecture d'une base de même structure que la collecte, sans réseau ni vraie donnée."""
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

DATA = Path(__file__).resolve().parents[2]
os.environ.setdefault("DALIL_DATABASE_URL", f"sqlite:///{(Path(tempfile.mkdtemp()) / 'pipeline.db').as_posix()}")
sys.path.insert(0, str(DATA))

import pytest  # noqa: E402

from pipeline.load import chunk_rows  # noqa: E402
from pipeline.sources import SOURCES, Context  # noqa: E402
from pipeline.sources import largus  # noqa: E402

TOPICS = [
    # (id, marque, modèle, déclaré, catégorie, titre, résolu, auteur, description, résumé de solution)
    (1, "Renault", "Megane 2", "Megane 2 2005 - Diesel 1l5 dci", "Puissance", "Perte de puissance",
     1, "Jean_Dupont", "Ma voiture n'avance plus en montée, 120000 km 2003, voyant moteur. Écrivez-moi : jean.dupont@mail.fr",
     "C'était la vanne EGR encrassée, nettoyée et tout est rentré dans l'ordre"),
    (2, "Peugeot", "206", "206 2004 - Essence 1l4", "Freinage", "Bruit au freinage", 0, "kader31",
     "Ça grince fort quand je freine depuis une semaine, appelez au 06 12 34 56 78", None),
    (3, "Dacia", "Logan", "Logan 2010 - Diesel 1l5 dci", "Embrayage", "Embrayage qui patine", 1, "m_ali",
     "Le moteur monte dans les tours mais la voiture n'avance pas en côte", "Kit embrayage changé, problème réglé"),
    (4, "Citroen", "C3", "C3 2012", "Lève vitre", "Vitre bloquée", 0, "x", "La vitre conducteur ne remonte plus", None),
    # Base réelle (24/11/2026) : 0,2 % de sujets marqués résolus ; la cause est dans le dernier message de l'auteur
    (5, "Renault", "Clio 2", "Clio 2 2003 - Essence 1l2", "Démarrage", "Ne démarre plus", 0, "nadia",
     "La voiture ne démarre plus le matin, rien ne se passe quand je tourne la clé", None),
    (6, "Peugeot", "307", "307 2006 - Diesel 1l6 hdi", "Freinage", "Pédale molle", 0, "samir",
     "La pédale de frein est molle et s'enfonce presque jusqu'au plancher", None),
    (7, "Renault", "Clio 2", "Clio 2", "clio-2-bruit-au-freinage", "Bruit au freinage clio", 0, "lea",
     "Bruit métallique au freinage depuis hier soir", None),   # catégorie = titre recopié depuis l'adresse
    (8, "Fiat", "Punto", "Punto 2008", "Avis et fiabilité", "Punto fiable ?", 0, "yacine",
     "Je pense acheter une Punto de 2008, est-ce une voiture fiable ?", None),
]
MESSAGES = [  # numéros au format de la collecte : « #2 », « #3 »… (le message #1 recopie la description)
    (2, 2, "pro_meca", "Regarde tes plaquettes, elles doivent être mortes"),
    (2, 3, "autre", "Oui les plaquettes avant, et vérifie les disques @kader31"),
    (1, 2, "pro_meca", "Passe la valise, ça peut être le turbo ou la vanne EGR"),
    (1, 3, "Jean_Dupont", "Merci à tous, c'était bien la vanne EGR"),
    (5, 2, "pro_meca", "Batterie ou démarreur, mesure la tension"),
    (5, 3, "nadia", "J'ai changé la batterie mais rien ne change"),
    *[(5, i, "autre", "Des nouvelles ?") for i in range(4, 11)],
    (5, 11, "nadia", "Merci, c'était bien le démarreur, il est remplacé et tout marche"),   # « #11 » après « #3 »
    (6, 2, "pro_meca", "Fais purger le circuit"),
    (6, 3, "samir", "Merci, je vais vérifier les plaquettes arrière"),
    (7, 2, "pro_meca", "Tes plaquettes avant sont sûrement mortes"),
    (8, 2, "autre", "Oui, bonne voiture"),
]


@pytest.fixture()
def base(tmp_path):
    db = tmp_path / "largus_pannes.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE topics (topic_id, brand, model, brand_slug, model_slug, model_declared, symptom_category, title, "
                "is_resolved, views_count, replies_count, url, author, created_date, problem_description, resolution_summary, scraped_at)")
    con.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, topic_id, post_number, author, post_date, content)")
    for t in TOPICS:
        tid, brand, model, declared, cat, title, res, author, desc, sol = t
        con.execute("INSERT INTO topics VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (tid, brand, model, brand.lower(), model.lower(), declared, cat, title, res, 100, 3,
                     f"https://www.largus.fr/forum-auto/x/{tid}.html", author, "2020-01-01", desc, sol, "2026-11-18"))
    for t in TOPICS:   # message #1 = la description, comme dans la collecte
        con.execute("INSERT INTO messages (topic_id, post_number, author, post_date, content) VALUES (?,?,?,?,?)",
                    (t[0], "#1", t[7], "2020-01-01", t[8]))
    for m in MESSAGES:
        con.execute("INSERT INTO messages (topic_id, post_number, author, post_date, content) VALUES (?,?,?,?,?)",
                    (m[0], f"#{m[1]}", m[2], "2020-01-02", m[3]))
    con.commit()
    con.close()
    return db


def _collect(db, monkeypatch):
    monkeypatch.setenv("DALIL_LARGUS_AUTORISATION", "test")
    return {r.id: r for r in largus.collect(Context(options={"largus_db": str(db)}, log=lambda m: None))}


def test_verrou_sans_autorisation(base, monkeypatch):
    monkeypatch.delenv("DALIL_LARGUS_AUTORISATION", raising=False)
    with pytest.raises(SystemExit, match="AUTORISATION"):
        list(largus.collect(Context(options={"largus_db": str(base)}, log=lambda m: None)))


def test_anonymisation_et_question_sans_solution(base, monkeypatch):
    recs = _collect(base, monkeypatch)
    for r in recs.values():
        blob = f"{r.text} {r.meta} {r.vehicle}"
        for author in ("Jean_Dupont", "kader31", "m_ali", "pro_meca"):
            assert author not in blob
    r1 = recs["largus_forum:1"]
    assert "jean.dupont@mail.fr" not in r1.text and "[e-mail]" in r1.text
    assert "120000 km 2003" in r1.text                    # kilométrage et année ne sont pas pris pour un numéro
    assert "06 12 34 56 78" not in recs["largus_forum:2"].text
    assert "EGR" not in r1.text                            # la solution n'est pas dans le texte d'entraînement
    assert r1.meta["solution"] and "EGR" in r1.meta["solution"]


def test_etiquettes_par_niveau_de_confiance(base, monkeypatch):
    recs = _collect(base, monkeypatch)
    assert recs["largus_forum:1"].categories[0] == "vanne-egr" and recs["largus_forum:1"].label_quality == "solution"
    r2 = recs["largus_forum:2"]
    assert r2.categories[0] == "plaquettes-avant" and r2.label_quality == "reponses+component" and r2.fault is None
    r3 = recs["largus_forum:3"]
    assert r3.categories[0] == "kit-embrayage" and r3.label_quality == "solution+component" and r3.fault
    assert recs["largus_forum:4"].categories == []         # lève-vitre : hors taxonomie, pas d'étiquette forcée
    assert recs["largus_forum:1"].vehicle["year"] == 2005 and recs["largus_forum:1"].vehicle["fuel"] == "diesel"


def test_lecture_seule_et_licence_du_registre(base, monkeypatch):
    avant = base.stat().st_mtime_ns
    recs = _collect(base, monkeypatch)
    assert base.stat().st_mtime_ns == avant
    rows = chunk_rows([r.__dict__ for r in recs.values()])  # refuserait une licence différente du registre
    assert rows and all(r["license"] == SOURCES["largus_forum"].license for r in rows)


def test_base_reelle_dernier_message_auteur_ordre_categories(base, monkeypatch):
    recs = _collect(base, monkeypatch)
    r5 = recs["largus_forum:5"]   # non marqué résolu ; « #11 » lu après « #3 » (ordre d'enregistrement, pas du texte)
    assert r5.categories[0] == "demarreur" and r5.label_quality == "solution" and not r5.meta["resolved"]
    assert "démarreur" in r5.meta["solution"] and "démarreur" not in r5.text
    r6 = recs["largus_forum:6"]   # dernier message de l'auteur sans tournure de solution
    assert r6.categories[0] == "plaquettes-arriere" and r6.label_quality == "auteur+component" and r6.fault is None
    r7 = recs["largus_forum:7"]   # catégorie illisible : ni « +component », ni catégorie enregistrée
    assert r7.label_quality == "reponses" and r7.meta["symptom_category"] is None
    assert recs["largus_forum:8"].meta["diagnostic"] is False      # avis : hors de l'entraînement
    assert recs["largus_forum:2"].meta["diagnostic"] is True and recs["largus_forum:2"].meta["symptom_category"] == "freinage"
    for author in ("nadia", "samir", "lea", "yacine"):
        assert all(author not in f"{r.text} {r.meta}" for r in recs.values())
