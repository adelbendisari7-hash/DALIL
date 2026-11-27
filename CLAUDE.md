# DALIL — consignes pour Claude Code

Cahier des charges complet : `docs/cahier-des-charges.md` (le relire pour toute étape ; la section 11 donne le plan en 12 étapes).

**Suivi : `docs/SUIVI.md`.**
- **Au début de chaque session**, le lire en premier : il dit ce qui est fait, les décisions en attente et les prochaines actions. Reprendre à partir de là, sans redemander à l'utilisateur où on en est.
- **À la fin de chaque étape, et après chaque décision**, le mettre à jour : état des étapes, résultats, prochaines actions, journal.

## Conventions
- Backend en Python avec FastAPI, SQLAlchemy et Alembic (`backend/`) ; frontend en Next.js avec TypeScript (`frontend/`) ; base PostgreSQL + PostGIS + pgvector (SQLite accepté en local et dans les tests).
- Aucune donnée externe sans licence notée dans `data/SOURCES.md`.
- Tout texte d'interface passe par les fichiers de traduction (`frontend/messages/fr.json`, `ar.json`) via `t()`.
- Le modèle de langage est appelé derrière une interface unique (`backend/app/services/diagnosis/llm.py`), pour pouvoir changer de fournisseur.
- Chaque point d'entrée a un test ; chaque script de données est rejouable.
- Ne jamais inventer de magasin, de prix ou de référence de pièce : données de démonstration clairement marquées comme fictives (`is_demo`, préfixe « [DÉMO] », références « FICTIF-… »). Une référence de pièce est toujours lue dans une table, jamais générée par un modèle.
- Avant de chercher dans le code, lire `graphify-out/GRAPH_REPORT.md` et interroger le graphe ; ne relire un fichier que pour le modifier.
- Mettre à jour le graphe (`/graphify`, mode incrémental) à la fin de chaque étape, avant le commit.
- Au début de chaque étape, lister les skills disponibles et charger ceux qui s'appliquent (section « Étape 0 »).

## Commandes
- Backend : `cd backend && .venv/Scripts/python -m pytest -q` ; API : `uvicorn app.main:app --reload` (docs sur /docs).
- Migrations : `alembic upgrade head` ; référentiels + démo : `python -m app.seed` ; purge démo : `python -m app.seed --purge-demo`.
- Magasins OpenStreetMap -> brouillons + liste de visite : `cd backend && python -m app.import_osm` (rejouable ; `--dry-run`). La liste remplie se réimporte dans Admin > Import CSV.
- Modèle de référence : `python ml/train_baseline.py [--target part] [--corpus]` (exporte dans `ml/artifacts/`).
- Évaluation des variantes : `python ml/evaluate.py --model NOM=chemin --modes classifier,retrieval,full [--test data/test/oran_test.jsonl]` (résultats dans `ml/results/`). Le jeu de test d'Oran ne sert jamais à entraîner ni à régler un seuil ; les réglages se font sur `data/test/dev_fr_synthetique.jsonl`.
- Jeu d'entraînement commun (variantes A et B) : `python ml/build_training_set.py` puis `python ml/train_baseline.py --set` ; relecture d'étiquettes : `python ml/relecture_etiquettes.py tirer --source largus_forum` puis `mesurer <fichier.xlsx>`.
- Classifieur à deux niveaux (familles apprises sur L'Argus, fichier local hors git) : `python ml/train_family_reranker.py --alphas 0.25` ; le lanceur l'utilise s'il existe (`DALIL_CLASSIFIER_PATH`).
- Jeu de test L'Argus (104 vrais cas, privé, hors git) : `python ml/evaluate.py ... --test data/test_prive/largus_test.jsonl` ; ses résultats détaillés restent hors git.
- Vrais exemples L'Argus vérifiés (identifiants sans texte dans `data/largus/causes_verifiees.json`) : `python ml/extraire_causes_largus.py --verifiees` puis `train_baseline.py --exemples-reels data/processed/largus_causes_verifiees.jsonl --out <base>` et `train_family_reranker.py --base <base> --alphas 0.25` (voir `ml/README.md`).
- Techniconnexion (accord déclaré, écrit à archiver) : `DALIL_TECHNICONNEXION_AUTORISATION="..." python data/pipeline/run.py collect --sources techniconnexion --techniconnexion-dir <ml_ready>` ; vrais exemples : `extraire_causes_largus.py --source techniconnexion --verifiees` (contrôle de 39 cas dans `data/test_prive/techniconnexion_controle.jsonl`).
- CamemBERT (jeu Kaggle privé `dalil-camembert`, données nettoyées) : `python ml/kaggle/build_camembert_sets.py`, `kaggle_run.py dataset-camembert`, carnets `02_camembert_familles` / `02_camembert_pieces`, puis `python ml/assembler_deux_niveaux.py` (voir `ml/kaggle/README.md`).
- Jeu de test d'Oran : `python ml/oran_csv_to_jsonl.py fiches.csv [--check]` (protocole des essais : `docs/essais-oran.md`).
- Étape 7 sur Kaggle : `ml/kaggle/README.md` ; carnets générés par `python ml/kaggle/make_notebooks.py` (modifier ce script, pas les .ipynb) ; jeu d'affinage du modèle de langage : `python ml/build_llm_dataset.py`.
- Retours des utilisateurs (« Non, c'était telle pièce ») -> vrais exemples candidats à vérifier : `cd backend && python -m app.export_retours` (`data/processed/retours_dalil.jsonl`, hors git, données personnelles masquées).
- Frontend : `cd frontend && npm run dev` (le lanceur sert la version de production, construite si le code a changé : `node scripts/build-si-besoin.mjs && npm run start` ; `SITE_DEV=1` dans `DEMARRER-DALIL.bat` pour le mode développement) ; e2e : `cd frontend && npx playwright test` (téléphone simulé ; trouve seul `backend/.venv`).
- Vérification « comme un téléphone » contre un DALIL lancé (360 px, tactile, 3G, adresse Wi-Fi) : `cd frontend && TEL_URL=http://<ip>:3000 npx playwright test -c playwright.telephone.config.ts` (`docs/test-telephone.md`).
- Captures de l'interface pour une revue de design (360 px, clair et sombre, sur la base des tests) : `cd frontend && E2E_API_PORT=8100 E2E_WEB_PORT=3100 npx playwright test -c playwright.captures.config.ts` (sortie `test-results/captures/`). Principes de l'interface : en tête de `frontend/app/globals.css`.
- Pipeline de données (étape 6) : `python data/pipeline/run.py all` (collecte, chargement, rapport ; `--sources`, `--limit`, `--refresh`) ; traduction : `run.py translate` sur Kaggle (`ml/kaggle/README.md`) ; tests : `cd backend && .venv/Scripts/python -m pytest -q ../data/pipeline/tests`.
- Ajouter une source de données : skill de projet `ajouter-source-donnees` (`.claude/skills/`).
- Tout : `docker compose up --build`.

## Carte du code
- `backend/app/services/recommendation.py` : score des magasins (section 6.4), fonction pure `score_shop` testée par 10 scénarios.
- `backend/app/services/diagnosis/pipeline.py` : chaîne de diagnostic (normalisation, recherche, classifieur, modèle de langage, sûreté, questions de précision, niveaux de référence).
- `backend/app/routers/` : `public` (véhicules, pièces, OBD, diagnostic), `shops` (recommandation, espace magasin, contacts, retours, demandes), `auth` (inscription et connexion par mot de passe, profil du compte client ; code SMS gardé pour plus tard), `account` (voitures du client au matricule unique, signalements, historique), `admin`.
- `data/seed/` : référentiels JSON ; `data/scripts/` : OSM Overpass, OBDex.
- `data/pipeline/` : `sources/` (un module par source + registre des licences), `taxonomy_map.py` (texte -> famille de pièce), `translate.py`, `load.py` (base de connaissances + `data/processed/train/`), `run.py`. Fiches des sources : `data/sources/<id>.md`.
