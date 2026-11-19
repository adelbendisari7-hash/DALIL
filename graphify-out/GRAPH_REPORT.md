# Graph Report - DALIL  (2026-11-19)

## Corpus Check
- 219 files · ~212,842 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 29 file(s) not represented in the graph (top: .ipynb 7, (none) 6, .jsonl 4)

## Summary
- 1651 nodes · 3825 edges · 104 communities (90 shown, 14 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 300 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `75dd6075`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- llm.py
- run_diagnosis
- to_french
- security.py
- environment
- pipeline.py
- package.json
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- config.py
- t
- helpers.ts
- recommendation.py
- Context
- largus.py
- kaggle_run.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- admin/page.tsx
- steps
- config.py
- espace-magasin/page.tsx
- compilerOptions
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- shops.py
- test_pipeline.py
- SOURCES.md
- ZipMemberStream
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- oran_csv_to_jsonl.py
- diagnostic/[id]/page.tsx
- api
- conftest.py
- build_training_set.py
- Modèles (étape 7)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- taxonomy_map.py
- next.config.mjs
- sw.js
- report.md
- Étape 11 : essais à Oran (protocole et compte rendu)
- anonymiser_ouedkniss.py
- classifier.py
- test_llm_chaine.py
- re
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- magasins/page.tsx
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- test_retrieval_hybride.py
- common.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Jeux de test
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- test_api.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- _references
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- models.py
- eval_with_llm.sh
- magasins/[id]/page.tsx
- run.py
- argparse
- i18n.ts
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Étape 9 : vérification sur un vrai téléphone
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- auth.py
- fiche-telephone.spec.ts
- DeniedRecognition
- FakeRecognition
- scripts
- make_notebooks.py
- @playwright/test
- main.py
- DenseIndex
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- load_vectors.py
- argparse
- evaluate.py
- test_espace_magasin.py
- test_concurrence.py
- Le marché automobile algérien : ce qu'il implique pour DALIL
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 61 edges
2. `run_diagnosis()` - 53 edges
3. `t()` - 50 edges
4. `Shop` - 43 edges
5. `User` - 39 edges
6. `api()` - 37 edges
7. `PartCategory` - 33 edges
8. `Base` - 32 edges
9. `VehicleVariant` - 28 edges
10. `DiagnosisInput` - 28 edges

## Surprising Connections (you probably didn't know these)
- `Carte du code` --references--> `score_shop()`  [INFERRED]
  CLAUDE.md → backend/app/services/recommendation.py
- `Décisions déjà prises par l'utilisateur (17/11/2026)` --references--> `glossary_misses()`  [INFERRED]
  docs/plan-referentiel-et-donnees.md → data/pipeline/translate.py
- `Conventions` --references--> `t()`  [INFERRED]
  CLAUDE.md → frontend/lib/i18n.ts
- `1. Ce qui existe déjà (étapes 3 à 7)` --references--> `_CallBudget`  [INFERRED]
  docs/plan-etape-8.md → backend/app/services/diagnosis/llm.py
- `1. Ce qui existe déjà (étapes 3 à 7)` --references--> `rerank_with_llm()`  [INFERRED]
  docs/plan-etape-8.md → backend/app/services/diagnosis/llm.py

## Import Cycles
- None detected.

## Communities (104 total, 14 thin omitted)

### Community 0 - "llm.py"
Cohesion: 0.15
Nodes (10): get_settings(), AnthropicProvider, build_user_message(), _CallBudget, get_llm(), LLMProvider, OpenAICompatProvider, _parse_json() (+2 more)

### Community 1 - "run_diagnosis"
Cohesion: 0.22
Nodes (13): DiagnosisInput, informative_words(), run_diagnosis(), test_arabe_incompris_message_clair(), test_diagnostic_en_darija(), test_hors_sujet_en_darija_refuse(), test_demo_case(), test_mot_seul_avec_code_obd_reste_un_diagnostic() (+5 more)

### Community 2 - "to_french"
Cohesion: 0.20
Nodes (10): _ar_word(), _french_like_hits(), _norm_ar(), _replace_phrases(), to_french(), strip_accents(), test_francais_inchange(), test_mots_arabes_inconnus_retires() (+2 more)

### Community 3 - "security.py"
Cohesion: 0.11
Nodes (7): client_hash(), ConsoleSms, current_user(), current_user_optional(), get_sms_sender(), RateLimiter, SmsSender

### Community 4 - "environment"
Cohesion: 0.05
Nodes (39): build, depends_on, environment, ports, volumes, NEXT_PUBLIC_API_URL, args, context (+31 more)

### Community 5 - "pipeline.py"
Cohesion: 0.16
Nodes (8): extract_dtc(), normalize(), non_fault_question(), _normalized(), _part_view(), _part_words(), parts_to_faults(), text_is_dangerous()

### Community 6 - "package.json"
Cohesion: 0.14
Nodes (17): react-dom@^19.3.1, devDependencies, @playwright/test@^1.65.1, @types/leaflet@^1.9.22, @types/node@^26.6.6, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@^5.9.3 (+9 more)

### Community 7 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.07
Nodes (27): Carte du code, Commandes, Conventions, DALIL — consignes pour Claude Code, 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes (+19 more)

### Community 8 - "config.py"
Cohesion: 0.13
Nodes (3): Settings, get_db(), make_engine()

### Community 9 - "t"
Cohesion: 0.09
Nodes (23): Home(), submit(), Family, Hit, PartsPage(), RefHit, ContactShop, Ctx (+15 more)

### Community 10 - "helpers.ts"
Cohesion: 0.21
Nodes (6): ADMIN_PHONE, makeCatalog(), OTP, PY_PATH, VENV, WEB_ENV

### Community 11 - "recommendation.py"
Cohesion: 0.06
Nodes (47): km(), main(), nearest_commune(), prepare(), read_osm(), run(), write_visit_list(), freshness() (+39 more)

### Community 12 - "Context"
Cohesion: 0.15
Nodes (15): download(), Record, collect(), Context, aggregate(), _band(), collect(), _n() (+7 more)

### Community 13 - "largus.py"
Cohesion: 0.13
Nodes (14): category_family(), collect(), _connect(), label(), _plain(), scrub(), _vehicle(), _with_family() (+6 more)

### Community 14 - "kaggle_run.py"
Cohesion: 0.27
Nodes (10): cmd_adapter(), cmd_dataset(), cmd_output(), cmd_push(), cmd_status(), _force_remove(), kaggle(), main() (+2 more)

### Community 15 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.09
Nodes (22): A-amorcage / classifieur seul | demo_cases (0), A-amorcage / classifieur seul | dev_fr_synthetique (4), A-amorcage / D (chaîne complète) | demo_cases (0), A-amorcage / D (chaîne complète) | dev_fr_synthetique (3), A-corpus-panne / classifieur seul | demo_cases (1), A-corpus-panne / classifieur seul | dev_fr_synthetique (4), A-corpus-panne / D (chaîne complète) | demo_cases (1), A-corpus-panne / D (chaîne complète) | dev_fr_synthetique (3) (+14 more)

### Community 16 - "admin/page.tsx"
Cohesion: 0.29
Nodes (7): Admin(), act(), upload(), Metrics, pct(), Shop, Tab

### Community 17 - "steps"
Cohesion: 0.12
Nodes (20): runs-on, steps, DALIL_DATABASE_URL, runs-on, steps, jobs, backend, frontend (+12 more)

### Community 18 - "config.py"
Cohesion: 0.14
Nodes (4): Embedder, get_reranker(), _load(), Reranker

### Community 19 - "espace-magasin/page.tsx"
Cohesion: 0.16
Nodes (15): FieldForm(), submit(), Claimable, Family, Inbox, Product, Shop, cleanShop() (+7 more)

### Community 20 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 21 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.11
Nodes (17): 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes, 14. Protection du projet et statut de startup, 15. Sources, 1. Vision et périmètre, 2. Acteurs et parcours (+9 more)

### Community 22 - "shops.py"
Cohesion: 0.05
Nodes (76): ContactEvent, Feedback, PartCategory, PartRequest, Product, RequestResponse, Shop, ShopBrand (+68 more)

### Community 23 - "test_pipeline.py"
Cohesion: 0.10
Nodes (22): sha1(), chunk_rows(), LicenseError, _rec(), test_chaque_source_a_sa_fiche_et_sa_licence(), test_chargement_refuse_sans_licence(), test_correspondance_anglais(), test_decoupage_en_phrases() (+14 more)

### Community 24 - "SOURCES.md"
Cohesion: 0.09
Nodes (14): Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`), Anonymisation, Commande, Contenu, Forum L'Argus : « Panne auto, mécanique et entretien » (`largus_forum`), Limites, Usage dans DALIL, Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`) (+6 more)

### Community 25 - "ZipMemberStream"
Cohesion: 0.11
Nodes (10): 1. Vérifier avant d'écrire du code, 2. Déclarer la source, 3. Écrire le module de collecte, 5. Tester, charger, mesurer, Ajouter une source de données à DALIL, Ce qu'il ne faut pas faire, ZipMemberStream, SourceSpec (+2 more)

### Community 26 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.11
Nodes (18): A-actuel / classifieur seul | audit_ecriture_oran (8), A-actuel / classifieur seul | audit_ecriture_oran_controle (0), A-actuel / classifieur seul | demo_cases (0), A-actuel / classifieur seul | dev_fr_synthetique (2), A-actuel / D (chaîne complète) | audit_ecriture_oran (6), A-actuel / D (chaîne complète) | audit_ecriture_oran_controle (0), A-actuel / D (chaîne complète) | demo_cases (0), A-actuel / D (chaîne complète) | dev_fr_synthetique (1) (+10 more)

### Community 27 - "oran_csv_to_jsonl.py"
Cohesion: 0.18
Nodes (9): test_conversion_des_fiches(), test_lignes_invalides_refusees_avec_la_raison(), test_modele_fourni_ne_contient_que_l_exemple(), test_vehicule_inconnu_garde_sans_vehicule_et_signale(), convert(), _fuzzy(), _slugs(), walk() (+1 more)

### Community 28 - "diagnostic/[id]/page.tsx"
Cohesion: 0.22
Nodes (10): Cause, DiagnosticResult(), answer(), rate(), Part, PartLabel(), Question, Ref (+2 more)

### Community 29 - "api"
Cohesion: 0.23
Nodes (15): Account(), remove(), errMsg(), ShopAdmin(), addProduct(), importFile(), respond(), saveProfile() (+7 more)

### Community 30 - "conftest.py"
Cohesion: 0.36
Nodes (4): admin_headers(), client(), db(), _db()

### Community 31 - "build_training_set.py"
Cohesion: 0.12
Nodes (17): fiche_examples(), load_examples(), dump(), test_poids_seuil_doublons_et_fuite(), test_validation_stable(), _write(), build(), explanation() (+9 more)

### Community 32 - "Modèles (étape 7)"
Cohesion: 0.10
Nodes (15): OnnxEncoderClassifier, Entraîner avec L'Argus (variante A contre CamemBERT), Faire tourner les modèles sur le portable, Mesurer (portable), Mettre un modèle en service, Ordre conseillé, Préparer le jeu de données Kaggle « dalil-pipeline », Étape 7 sur Kaggle : traduction et entraînement (+7 more)

### Community 33 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), B-enfr / classifieur seul | demo_cases (6), B-enfr / classifieur seul | dev_fr_synthetique (14), B-enfr / D (chaîne complète) | demo_cases (3), B-enfr / D (chaîne complète) | dev_fr_synthetique (10) (+2 more)

### Community 34 - "taxonomy_map.py"
Cohesion: 0.17
Nodes (19): 4. Relier à la taxonomie, collect_complaints(), collect_recalls(), _vehicle(), collect(), categories_en(), categories_fr(), family_fr() (+11 more)

### Community 38 - "Étape 11 : essais à Oran (protocole et compte rendu)"
Cohesion: 0.18
Nodes (10): 1. Ce que les essais doivent mesurer, 2. Avant les essais, 3. Déroulé, 4. Fiches de relevé, 5. Questionnaire (1 à 5, de « pas du tout » à « tout à fait »), 6. Modèle de compte rendu, A. Mécaniciens : constituer le jeu de test (le plus important), B. Magasins (environ 15 min chacun, sur leur propre téléphone) (+2 more)

### Community 39 - "anonymiser_ouedkniss.py"
Cohesion: 0.29
Nodes (4): test_numero_dans_le_modele_masque_date_et_nombres_intacts(), anonymize(), main(), scrub()

### Community 40 - "classifier.py"
Cohesion: 0.09
Nodes (17): build_pipeline(), FaultClassifier, get_classifier(), load_classifier(), train_baseline(), _maps(), test_carnets_kaggle_a_jour_et_valides(), test_chaine_avec_classifieur_de_pieces() (+9 more)

### Community 43 - "test_llm_chaine.py"
Cohesion: 0.17
Nodes (15): Fake, fake(), install(), _run(), test_cache_expire(), test_cache_une_question_identique_ne_coute_qu_un_appel(), test_cas_de_demonstration_en_mode_complet_avec_modele(), test_le_classifieur_seul_n_appelle_pas_le_modele() (+7 more)

### Community 44 - "re"
Cohesion: 0.51
Nodes (7): brand_name(), engine_of(), fuel_of(), main(), model_key(), pct(), _plain()

### Community 45 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.22
Nodes (8): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), C (recherche + LM) | demo_cases (4), C (recherche + LM) | dev_fr_synthetique (13), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261114-1722 couverture

### Community 46 - "magasins/page.tsx"
Cohesion: 0.30
Nodes (10): ShopPage(), Rec, ShopMap, Shops(), broadcast(), ShopsPage(), ShopContact(), log() (+2 more)

### Community 47 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.15
Nodes (12): A-panne / classifieur seul | demo_cases (0), A-panne / classifieur seul | dev_fr_synthetique (4), A-panne / D (chaîne complète) | demo_cases (0), A-panne / D (chaîne complète) | dev_fr_synthetique (3), A-piece / classifieur seul | demo_cases (0), A-piece / classifieur seul | dev_fr_synthetique (5), A-piece / D (chaîne complète) | demo_cases (0), A-piece / D (chaîne complète) | dev_fr_synthetique (3) (+4 more)

### Community 48 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A-panne / classifieur seul | demo_cases (0), A-panne / classifieur seul | dev_fr_synthetique (5), A-panne / D (chaîne complète) | demo_cases (0), A-panne / D (chaîne complète) | dev_fr_synthetique (5), A-piece / classifieur seul | demo_cases (0), A-piece / classifieur seul | dev_fr_synthetique (6), A-piece / D (chaîne complète) | demo_cases (0), A-piece / D (chaîne complète) | dev_fr_synthetique (5) (+2 more)

### Community 49 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A-panne / classifieur seul | demo_cases (0), A-panne / classifieur seul | dev_fr_synthetique (4), A-piece / classifieur seul | demo_cases (0), A-piece / classifieur seul | dev_fr_synthetique (5), A-piece / D (chaîne complète) | demo_cases (0), A-piece / D (chaîne complète) | dev_fr_synthetique (3), C (recherche + LM) | demo_cases (1), C (recherche + LM) | dev_fr_synthetique (7) (+2 more)

### Community 50 - "test_retrieval_hybride.py"
Cohesion: 0.11
Nodes (13): get_index(), _diag(), FakeEmbedder, FakeReranker, hybrid(), test_garde_fou_vectoriel_absent_en_mode_mots_cles(), test_garde_fou_vectoriel_du_domaine(), encode_query() (+5 more)

### Community 51 - "common.py"
Cohesion: 0.46
Nodes (3): client(), get_json(), _fetch()

### Community 52 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A-panne / classifieur seul | demo_cases (1), A-panne / classifieur seul | dev_fr_synthetique (5), A-panne / D (chaîne complète) | demo_cases (1), A-panne / D (chaîne complète) | dev_fr_synthetique (4), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261114-1234 hors-sujet-domaine

### Community 53 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A-panne / classifieur seul | demo_cases (0), A-panne / classifieur seul | dev_fr_synthetique (4), A-panne / D (chaîne complète) | demo_cases (0), A-panne / D (chaîne complète) | dev_fr_synthetique (4), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261114-1234 seuil-012

### Community 54 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / classifieur seul | demo_cases (2), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (2), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261114-1718 base-traduite

### Community 56 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261114-1719 index-domaine

### Community 57 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), C (recherche + LM) | demo_cases (2), C (recherche + LM) | dev_fr_synthetique (13), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261115-1924 lora-q4

### Community 58 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1627 mot-seul-hybride

### Community 59 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1627 mot-seul-mots-cles

### Community 60 - "test_api.py"
Cohesion: 0.09
Nodes (21): login(), cat_id(), test_admin_saisie_terrain_apparait_sur_la_carte(), test_contact_et_retour_modifient_le_score(), test_demande_diffusee(), test_diagnostic_et_session(), test_import_excel_500_lignes(), test_magasins_demo_marques() (+13 more)

### Community 61 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (2), C (recherche + LM) | demo_cases (2), C (recherche + LM) | dev_fr_synthetique (14), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261115-2250 hybride-sans-lm

### Community 62 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), C (recherche + LM) | demo_cases (2), C (recherche + LM) | dev_fr_synthetique (11), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261116-0000 hybride-garde-vecteurs

### Community 63 - "_references"
Cohesion: 0.18
Nodes (9): _pick_questions(), question_bank(), _references(), 1. Ce qui existe déjà (étapes 3 à 7), 2. Ce qui manque, par ordre de priorité, 3. Hors périmètre de l'étape 8, 4. Tests ajoutés, 5. Décisions demandées à l'équipe (+1 more)

### Community 64 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261115-2244 lora-q8

### Community 65 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (1), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261116-0054 lora-q8-hybride

### Community 66 - "models.py"
Cohesion: 0.05
Nodes (54): upgrade(), upgrade(), upgrade(), Base, AdminAction, Brand, Commune, DiagnosisSession (+46 more)

### Community 68 - "magasins/[id]/page.tsx"
Cohesion: 0.14
Nodes (13): Family, Named, Product, Shop, ShopMap, MapShop, ORAN, ShopMap() (+5 more)

### Community 69 - "run.py"
Cohesion: 0.21
Nodes (13): read_jsonl(), write_jsonl(), export_training(), load_source(), summary(), cmd_collect(), cmd_load(), cmd_report() (+5 more)

### Community 70 - "argparse"
Cohesion: 0.29
Nodes (5): clean_name(), _dump(), main(), norm(), variants_for()

### Community 73 - "i18n.ts"
Cohesion: 0.11
Nodes (14): Login(), LoginPage(), body, display, metadata, RootLayout(), viewport, NotFound() (+6 more)

### Community 74 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.13
Nodes (14): A-fort-x1 / D (chaîne complète) | audit_ecriture_oran (5), A-fort-x1 / D (chaîne complète) | audit_ecriture_oran_controle (1), A-fort-x1 / D (chaîne complète) | demo_cases (3), A-fort-x1 / D (chaîne complète) | dev_fr_synthetique (2), A-fort-x5 / D (chaîne complète) | audit_ecriture_oran (6), A-fort-x5 / D (chaîne complète) | audit_ecriture_oran_controle (0), A-fort-x5 / D (chaîne complète) | demo_cases (1), A-fort-x5 / D (chaîne complète) | dev_fr_synthetique (1) (+6 more)

### Community 75 - "Étape 9 : vérification sur un vrai téléphone"
Cohesion: 0.33
Nodes (5): Parcours à suivre (cocher), Préparer, Résultat, Vérification automatique « comme un téléphone » (à refaire avant les essais d'Oran), Étape 9 : vérification sur un vrai téléphone

### Community 76 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1533 hybride-int8-10x256

### Community 77 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1542 hybride-int8-10x256-vecteurs-repares

### Community 78 - "auth.py"
Cohesion: 0.21
Nodes (9): OtpCode, me(), me_delete(), me_patch(), otp_request(), otp_verify(), _user_out(), create_token() (+1 more)

### Community 79 - "fiche-telephone.spec.ts"
Cohesion: 0.25
Nodes (3): constats, mesures, report

### Community 82 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, start, test:e2e, typecheck

### Community 86 - "DenseIndex"
Cohesion: 0.07
Nodes (18): get_embedder(), DenseIndex, Hit, HybridIndex, KeywordIndex, 0. Objectifs et critères de fin, 1. Phase A : référentiel des véhicules, 2. Phase B : collecte des nouvelles données (+10 more)

### Community 88 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (6), A / D (chaîne complète) | audit_ecriture_oran_controle (0), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-2103 referentiel

### Community 89 - "load_vectors.py"
Cohesion: 0.40
Nodes (5): check_ids(), check_queries(), fill_db(), install(), main()

### Community 91 - "argparse"
Cohesion: 0.27
Nodes (7): _as_list(), _first(), iter_records(), main(), make_translator(), fetch(), main()

### Community 94 - "evaluate.py"
Cohesion: 0.36
Nodes (5): test_banc_evaluation(), load_cases(), main(), ranked_parts(), run()

### Community 95 - "test_espace_magasin.py"
Cohesion: 0.24
Nodes (6): new_otp(), _owner(), test_catalogue_d_une_fiche_non_validee_cache_au_public(), test_code_fixe_des_tests_seulement_avec_les_sms_de_console(), test_les_exemples_du_modele_s_importent_sans_erreur(), test_mode_console_annonce_sans_donner_le_code()

### Community 96 - "test_concurrence.py"
Cohesion: 0.24
Nodes (5): warmup(), _diagnose(), test_diagnostics_simultanes_pendant_la_reconstruction_des_index(), test_prechargement_sans_erreur(), Étape 8 : recherche hybride et chaîne complète (16/11/2026)

### Community 97 - "Le marché automobile algérien : ce qu'il implique pour DALIL"
Cohesion: 0.25
Nodes (7): 1. Le parc : vieux, français, et de plus en plus diesel à la revente, 2. Oran, 3. Ce qui se vend aujourd'hui (2023-2026), 4. Écarts avec le référentiel actuel de DALIL (`data/seed/vehicles.json`), 5. Recommandations pour le site, Le marché automobile algérien : ce qu'il implique pour DALIL, Sources

### Community 99 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (12), A / D (chaîne complète) | audit_ecriture_oran_controle (1), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1805 darija-keyword

### Community 100 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (10), A / D (chaîne complète) | audit_ecriture_oran_controle (2), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1806 darija-hybrid

### Community 101 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (7), A / D (chaîne complète) | audit_ecriture_oran_controle (0), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1817 darija-exemples-keyword

### Community 102 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (5), A / D (chaîne complète) | audit_ecriture_oran_controle (1), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1818 darija-exemples-hybrid

### Community 103 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (5), A / D (chaîne complète) | audit_ecriture_oran_controle (0), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1832 qualite-finale-hybrid

### Community 104 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (6), A / D (chaîne complète) | audit_ecriture_oran_controle (0), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1832 qualite-finale-keyword

### Community 108 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.50
Nodes (3): A / D (chaîne complète) | audit_ecriture_oran (19), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1756 audit-keyword

### Community 109 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.50
Nodes (3): A / D (chaîne complète) | audit_ecriture_oran (21), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1757 audit-hybrid

### Community 110 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.50
Nodes (3): A / D (chaîne complète) | audit_ecriture_oran_controle (9), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1801 controle-avant-keyword

### Community 111 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.50
Nodes (3): A / D (chaîne complète) | audit_ecriture_oran_controle (10), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-1802 controle-avant-hybrid

## Knowledge Gaps
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `score_shop()` connect `recommendation.py` to `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `run_diagnosis()` (e.g. with `DtcCode` and `DtcPart`) actually correct?**
  _`run_diagnosis()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14855072463768115 - nodes in this community are weakly interconnected._
- **Why does `Carte du code` connect `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` to `recommendation.py`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Should `security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11067193675889328 - nodes in this community are weakly interconnected._
- **Should `environment` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.1437908496732026 - nodes in this community are weakly interconnected._