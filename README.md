# DALIL

Diagnostic automobile assisté par IA et localisation des pièces détachées dans les magasins d'Oran.
« Ma voiture a ce problème : quelle pièce me faut-il, et quel magasin d'Oran la vend ? »

Cahier des charges : [docs/cahier-des-charges.md](docs/cahier-des-charges.md). Conventions : [CLAUDE.md](CLAUDE.md).

## Démarrer en un clic (Windows)

Double-cliquez sur **`DEMARRER-DALIL.bat`**. La première fois, il installe tout (quelques minutes), puis il ouvre
l'API et le site dans deux fenêtres et lance le navigateur sur http://localhost:3000. Fermez les deux fenêtres pour arrêter.
Mettez votre numéro de mobile dans la ligne `ADMIN_PHONE` du fichier pour devenir administrateur.

## Démarrer à la main (sans Docker)

```bash
# API
cd backend
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Linux/Mac : .venv/bin/
.venv/Scripts/alembic upgrade head
.venv/Scripts/python -m app.seed            # référentiels + magasins FICTIFS de démonstration
set DALIL_ADMIN_PHONES=0550000000            # votre numéro devient administrateur
.venv/Scripts/uvicorn app.main:app --reload  # http://localhost:8000/docs

# Site
cd frontend
npm install && npm run dev                   # http://localhost:3000
```

Connexion : le code SMS s'affiche dans le terminal de l'API (fournisseur SMS « console » en développement).

## Avec Docker

```bash
cp .env.example .env
docker compose up --build    # PostgreSQL + PostGIS + pgvector, API, site
```

## Tests

```bash
cd backend && .venv/Scripts/python -m pytest -q                 # 54 tests : API, imports, score, 20 cas de démo
cd frontend && PYTHON=../backend/.venv/Scripts/python npx playwright test   # parcours dans un navigateur mobile
```

## État par étape (section 11)

| Étape | État |
| --- | --- |
| 0. Graphify | À lancer : `pip install graphifyy && graphify install`, puis `/graphify .` |
| 1. Socle | Fait : mono-repo, Docker Compose, CI |
| 2. Schéma | Fait : toutes les tables, migrations rejouables, communes d'Oran |
| 3. Référentiels | Fait : 15 marques, taxonomie à 2 niveaux (15 familles, 65 sous-familles dont 21 du pilote), 47 codes OBD en français ; import OBDex prêt |
| 4. Annuaire | Fait : back-office, import CSV, script Overpass, formulaire terrain mobile |
| 5. Recommandation | Fait : score section 6.4 avec raisons, 10 scénarios testés |
| 6. Données de diagnostic | Fait : pipeline rejouable (`python data/pipeline/run.py all`), 6 sources avec fiche et licence, base de connaissances chargée ; traduction complète à lancer sur Kaggle |
| 7. Modèles | Banc d'évaluation reproductible (`ml/evaluate.py`), variante A (cible panne ou pièce), carnets Kaggle prêts pour la traduction, mmBERT (B) et le modèle de langage LoRA (D) ; entraînements à lancer sur Kaggle |
| 8. Chaîne de diagnostic | Faite avec le modèle de référence : JSON validé, questions, sûreté, « je ne sais pas », références lues en base |
| 9. Application | Faite : parcours automobiliste et mécanicien, carte, WhatsApp, voix (navigateur), installable |
| 10. Espace magasin | Fait : inscription, revendication, catalogue, import Excel, demandes |
| 11. Retours et tests | Code fait (contacts, retours, indicateurs) ; essais terrain à mener |
| 12. Mise en ligne | Sur décision de l'équipe |
