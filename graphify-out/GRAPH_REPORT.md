# Graph Report - DALIL  (2026-11-24)

## Corpus Check
- 219 files · ~214,233 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 29 file(s) not represented in the graph (top: .ipynb 7, (none) 6, .jsonl 4)

## Summary
- 1664 nodes · 3840 edges · 119 communities (96 shown, 23 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 302 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `623d061b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- llm.py
- run_diagnosis
- to_french
- client_hash
- environment
- pipeline.py
- package.json
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- config.py
- t
- helpers.ts
- test_recommendation.py
- mot.py
- largus.py
- imports.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- admin/page.tsx
- steps
- get_settings
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
- models.py
- build_training_set.py
- Étape 7 sur Kaggle : traduction et entraînement
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- taxonomy_map.py
- next.config.mjs
- sw.js
- report.md
- Étape 11 : essais à Oran (protocole et compte rendu)
- argparse
- classifier.py
- test_llm_chaine.py
- re
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- magasins/page.tsx
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- hybrid
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
- public.py
- eval_with_llm.sh
- magasins/[id]/page.tsx
- run.py
- admin.py
- i18n.ts
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Étape 9 : vérification sur un vrai téléphone
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- security.py
- fiche-telephone.spec.ts
- DeniedRecognition
- FakeRecognition
- scripts
- make_notebooks.py
- @playwright/test
- main.py
- Plan : référentiel complet des véhicules d'Algérie et nouveaux jeux de données pour le diagnostic
- seed.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- load_vectors.py
- schemas.py
- relecture_etiquettes.py
- translate.py
- stackexchange.py
- evaluate.py
- test_espace_magasin.py
- test_concurrence.py
- Le marché automobile algérien : ce qu'il implique pour DALIL
- DenseIndex
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- sqlalchemy
- test_referentiel.py
- build_llm_dataset.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- diagnosis
- .ensure_reference
- Embedder
- Modèles (étape 7)
- KeywordIndex
- HybridIndex

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 61 edges
2. `run_diagnosis()` - 53 edges
3. `t()` - 50 edges
4. `Shop` - 43 edges
5. `User` - 39 edges
6. `api()` - 37 edges
7. `PartCategory` - 33 edges
8. `Base` - 32 edges
9. `DiagnosisInput` - 28 edges
10. `VehicleVariant` - 28 edges

## Surprising Connections (you probably didn't know these)
- `Carte du code` --references--> `score_shop()`  [INFERRED]
  CLAUDE.md → backend/app/services/recommendation.py
- `Conventions` --references--> `t()`  [INFERRED]
  CLAUDE.md → frontend/lib/i18n.ts
- `Modèles (étape 7)` --references--> `OnnxEncoderClassifier`  [INFERRED]
  ml/README.md → backend/app/services/diagnosis/classifier.py
- `1. Où on en est` --references--> `score_shop()`  [INFERRED]
  docs/SUIVI.md → backend/app/services/recommendation.py
- `3. Écrire le module de collecte` --references--> `ZipMemberStream`  [INFERRED]
  .claude/skills/ajouter-source-donnees/SKILL.md → data/pipeline/common.py

## Import Cycles
- None detected.

## Communities (119 total, 23 thin omitted)

### Community 0 - "llm.py"
Cohesion: 0.17
Nodes (8): AnthropicProvider, build_user_message(), get_llm(), LLMProvider, OpenAICompatProvider, _parse_json(), rerank_with_llm(), _ResponseCache

### Community 1 - "run_diagnosis"
Cohesion: 0.12
Nodes (15): DiagnosisInput, informative_words(), _normalized(), run_diagnosis(), test_demo_case(), test_mot_seul_avec_code_obd_reste_un_diagnostic(), test_mot_seul_pas_de_resultat_sur(), test_mot_seul_puis_reponse_donne_un_resultat() (+7 more)

### Community 2 - "to_french"
Cohesion: 0.17
Nodes (13): _ar_word(), _french_like_hits(), _norm_ar(), _replace_phrases(), to_french(), strip_accents(), test_arabe_incompris_message_clair(), test_diagnostic_en_darija() (+5 more)

### Community 4 - "environment"
Cohesion: 0.05
Nodes (39): build, depends_on, environment, ports, volumes, NEXT_PUBLIC_API_URL, args, context (+31 more)

### Community 5 - "pipeline.py"
Cohesion: 0.24
Nodes (5): extract_dtc(), normalize(), non_fault_question(), _part_words(), text_is_dangerous()

### Community 6 - "package.json"
Cohesion: 0.14
Nodes (17): react-dom@^19.3.1, devDependencies, @playwright/test@^1.65.1, @types/leaflet@^1.9.22, @types/node@^26.6.6, @types/react@^19.3.0, @types/react-dom@^19.3.0, typescript@^5.9.3 (+9 more)

### Community 7 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.07
Nodes (27): Carte du code, Commandes, Conventions, DALIL — consignes pour Claude Code, 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes (+19 more)

### Community 9 - "t"
Cohesion: 0.09
Nodes (23): Home(), submit(), Family, Hit, PartsPage(), RefHit, ContactShop, Ctx (+15 more)

### Community 10 - "helpers.ts"
Cohesion: 0.21
Nodes (6): ADMIN_PHONE, makeCatalog(), OTP, PY_PATH, VENV, WEB_ENV

### Community 11 - "test_recommendation.py"
Cohesion: 0.13
Nodes (27): freshness(), rank(), reliability(), score_shop(), ScoredShop, ShopSignals, order(), S() (+19 more)

### Community 12 - "mot.py"
Cohesion: 0.22
Nodes (8): aggregate(), _band(), collect(), _n(), _pct(), family_of(), fetch(), main()

### Community 13 - "largus.py"
Cohesion: 0.13
Nodes (19): Context, author_solution(), category_family(), clean_category(), collect(), _connect(), label(), _plain() (+11 more)

### Community 14 - "imports.py"
Cohesion: 0.12
Nodes (18): km(), main(), nearest_commune(), prepare(), read_osm(), run(), write_visit_list(), Commune (+10 more)

### Community 15 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.09
Nodes (22): A-amorcage / classifieur seul | demo_cases (0), A-amorcage / classifieur seul | dev_fr_synthetique (4), A-amorcage / D (chaîne complète) | demo_cases (0), A-amorcage / D (chaîne complète) | dev_fr_synthetique (3), A-corpus-panne / classifieur seul | demo_cases (1), A-corpus-panne / classifieur seul | dev_fr_synthetique (4), A-corpus-panne / D (chaîne complète) | demo_cases (1), A-corpus-panne / D (chaîne complète) | dev_fr_synthetique (3) (+14 more)

### Community 16 - "admin/page.tsx"
Cohesion: 0.29
Nodes (7): Admin(), act(), upload(), Metrics, pct(), Shop, Tab

### Community 17 - "steps"
Cohesion: 0.12
Nodes (20): runs-on, steps, DALIL_DATABASE_URL, runs-on, steps, jobs, backend, frontend (+12 more)

### Community 18 - "get_settings"
Cohesion: 0.22
Nodes (9): get_settings(), get_embedder(), get_reranker(), _load(), Reranker, get_index(), test_mode_mots_cles_par_defaut(), test_recherche_hybride_fusionne_et_reclasse() (+1 more)

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
Cohesion: 0.13
Nodes (28): PartRequest, Product, Shop, catalog_template(), contact_event(), _owned_shop(), part_request_create(), part_request_inbox() (+20 more)

### Community 23 - "test_pipeline.py"
Cohesion: 0.14
Nodes (15): chunk_rows(), LicenseError, _rec(), test_chaque_source_a_sa_fiche_et_sa_licence(), test_chargement_refuse_sans_licence(), test_correspondance_anglais(), test_decoupage_en_phrases(), test_glossaire_signale_les_termes_mal_traduits() (+7 more)

### Community 24 - "SOURCES.md"
Cohesion: 0.09
Nodes (14): Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`), Anonymisation, Commande, Contenu, Forum L'Argus : « Panne auto, mécanique et entretien » (`largus_forum`), Limites, Usage dans DALIL, Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`) (+6 more)

### Community 25 - "ZipMemberStream"
Cohesion: 0.20
Nodes (3): ZipMemberStream, test_lecture_en_flux_d_un_zip(), test_reprise_apres_coupure_reseau()

### Community 26 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.11
Nodes (18): A-actuel / classifieur seul | audit_ecriture_oran (8), A-actuel / classifieur seul | audit_ecriture_oran_controle (0), A-actuel / classifieur seul | demo_cases (0), A-actuel / classifieur seul | dev_fr_synthetique (2), A-actuel / D (chaîne complète) | audit_ecriture_oran (6), A-actuel / D (chaîne complète) | audit_ecriture_oran_controle (0), A-actuel / D (chaîne complète) | demo_cases (0), A-actuel / D (chaîne complète) | dev_fr_synthetique (1) (+10 more)

### Community 27 - "oran_csv_to_jsonl.py"
Cohesion: 0.13
Nodes (11): test_conversion_des_fiches(), test_lignes_invalides_refusees_avec_la_raison(), test_modele_fourni_ne_contient_que_l_exemple(), test_vehicule_inconnu_garde_sans_vehicule_et_signale(), export(), convert(), _fuzzy(), main() (+3 more)

### Community 28 - "diagnostic/[id]/page.tsx"
Cohesion: 0.22
Nodes (10): Cause, DiagnosticResult(), answer(), rate(), Part, PartLabel(), Question, Ref (+2 more)

### Community 29 - "api"
Cohesion: 0.23
Nodes (15): Account(), remove(), errMsg(), ShopAdmin(), addProduct(), importFile(), respond(), saveProfile() (+7 more)

### Community 30 - "models.py"
Cohesion: 0.12
Nodes (17): Base, DiagnosisSession, Embedding, FaultPart, Feedback, ProductFitment, RequestResponse, ShopBrand (+9 more)

### Community 31 - "build_training_set.py"
Cohesion: 0.25
Nodes (10): dump(), test_poids_seuil_doublons_et_fuite(), test_validation_stable(), _write(), build(), is_val(), main(), norm() (+2 more)

### Community 32 - "Étape 7 sur Kaggle : traduction et entraînement"
Cohesion: 0.22
Nodes (7): Entraîner avec L'Argus (variante A contre CamemBERT), Faire tourner les modèles sur le portable, Mesurer (portable), Mettre un modèle en service, Ordre conseillé, Préparer le jeu de données Kaggle « dalil-pipeline », Étape 7 sur Kaggle : traduction et entraînement

### Community 33 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), B-enfr / classifieur seul | demo_cases (6), B-enfr / classifieur seul | dev_fr_synthetique (14), B-enfr / D (chaîne complète) | demo_cases (3), B-enfr / D (chaîne complète) | dev_fr_synthetique (10) (+2 more)

### Community 34 - "taxonomy_map.py"
Cohesion: 0.18
Nodes (19): 4. Relier à la taxonomie, client(), get_json(), rfr_categories(), collect_complaints(), collect_recalls(), _fetch(), _vehicle() (+11 more)

### Community 38 - "Étape 11 : essais à Oran (protocole et compte rendu)"
Cohesion: 0.18
Nodes (10): 1. Ce que les essais doivent mesurer, 2. Avant les essais, 3. Déroulé, 4. Fiches de relevé, 5. Questionnaire (1 à 5, de « pas du tout » à « tout à fait »), 6. Modèle de compte rendu, A. Mécaniciens : constituer le jeu de test (le plus important), B. Magasins (environ 15 min chacun, sur leur propre téléphone) (+2 more)

### Community 39 - "argparse"
Cohesion: 0.21
Nodes (9): test_numero_dans_le_modele_masque_date_et_nombres_intacts(), anonymize(), main(), scrub(), _as_list(), _first(), iter_records(), main() (+1 more)

### Community 40 - "classifier.py"
Cohesion: 0.08
Nodes (20): build_pipeline(), FaultClassifier, fiche_examples(), get_classifier(), load_classifier(), load_examples(), OnnxEncoderClassifier, train_baseline() (+12 more)

### Community 43 - "test_llm_chaine.py"
Cohesion: 0.17
Nodes (15): Fake, fake(), install(), _run(), test_cache_expire(), test_cache_une_question_identique_ne_coute_qu_un_appel(), test_cas_de_demonstration_en_mode_complet_avec_modele(), test_le_classifieur_seul_n_appelle_pas_le_modele() (+7 more)

### Community 44 - "re"
Cohesion: 0.21
Nodes (12): clean_name(), _dump(), main(), norm(), variants_for(), brand_name(), engine_of(), fuel_of() (+4 more)

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

### Community 50 - "hybrid"
Cohesion: 0.21
Nodes (5): FakeEmbedder, FakeReranker, hybrid(), encode_query(), _vec()

### Community 51 - "common.py"
Cohesion: 0.11
Nodes (12): 1. Vérifier avant d'écrire du code, 2. Déclarer la source, 3. Écrire le module de collecte, 5. Tester, charger, mesurer, Ajouter une source de données à DALIL, Ce qu'il ne faut pas faire, download(), Record (+4 more)

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
Cohesion: 0.06
Nodes (35): admin_headers(), client(), db(), _db(), login(), cat_id(), test_admin_saisie_terrain_apparait_sur_la_carte(), test_contact_et_retour_modifient_le_score() (+27 more)

### Community 61 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (2), C (recherche + LM) | demo_cases (2), C (recherche + LM) | dev_fr_synthetique (14), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261115-2250 hybride-sans-lm

### Community 62 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), C (recherche + LM) | demo_cases (2), C (recherche + LM) | dev_fr_synthetique (11), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261116-0000 hybride-garde-vecteurs

### Community 63 - "_references"
Cohesion: 0.17
Nodes (9): _CallBudget, _pick_questions(), question_bank(), 1. Ce qui existe déjà (étapes 3 à 7), 2. Ce qui manque, par ordre de priorité, 3. Hors périmètre de l'étape 8, 4. Tests ajoutés, 5. Décisions demandées à l'équipe (+1 more)

### Community 64 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261115-2244 lora-q8

### Community 65 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (1), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261116-0054 lora-q8-hybride

### Community 66 - "public.py"
Cohesion: 0.12
Nodes (20): DtcCode, DtcPart, PartCategory, brands(), categories(), communes(), diagnosis_get(), dtc() (+12 more)

### Community 68 - "magasins/[id]/page.tsx"
Cohesion: 0.14
Nodes (13): Family, Named, Product, Shop, ShopMap, MapShop, ORAN, ShopMap() (+5 more)

### Community 69 - "run.py"
Cohesion: 0.23
Nodes (13): read_jsonl(), write_jsonl(), export_training(), load_source(), summary(), cmd_collect(), cmd_load(), cmd_report() (+5 more)

### Community 70 - "admin.py"
Cohesion: 0.17
Nodes (15): AdminAction, ContactEvent, User, admin_actions(), admin_import(), admin_merge(), admin_metrics(), admin_refs_import() (+7 more)

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

### Community 78 - "security.py"
Cohesion: 0.10
Nodes (16): get_db(), OtpCode, me(), me_delete(), me_patch(), otp_request(), otp_verify(), _user_out() (+8 more)

### Community 79 - "fiche-telephone.spec.ts"
Cohesion: 0.25
Nodes (3): constats, mesures, report

### Community 82 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, start, test:e2e, typecheck

### Community 86 - "Plan : référentiel complet des véhicules d'Algérie et nouveaux jeux de données pour le diagnostic"
Cohesion: 0.17
Nodes (11): 0. Objectifs et critères de fin, 1. Phase A : référentiel des véhicules, 2. Phase B : collecte des nouvelles données, 4. Phase D : documentation et clôture, 5. Ordre et volume estimé, 6. Sources consultées pour ce plan, A1. Modèles à ajouter, A2. Méthode (rejouable, sans rien inventer) (+3 more)

### Community 87 - "seed.py"
Cohesion: 0.19
Nodes (21): Brand, Fault, KnowledgeChunk, Model, PartReference, VehicleVariant, Wilaya, _load() (+13 more)

### Community 88 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (6), A / D (chaîne complète) | audit_ecriture_oran_controle (0), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-2103 referentiel

### Community 89 - "load_vectors.py"
Cohesion: 0.40
Nodes (5): check_ids(), check_queries(), fill_db(), install(), main()

### Community 90 - "schemas.py"
Cohesion: 0.18
Nodes (13): AnswersRequest, ContactEventIn, DiagnosisRequest, FeedbackIn, _iso(), MePatch, OtpRequest, OtpVerify (+5 more)

### Community 91 - "relecture_etiquettes.py"
Cohesion: 0.18
Nodes (12): _rows(), test_intervalle_wilson(), test_separateur_unicode_dans_un_texte(), test_tirage_stratifie_et_mesure(), labelled(), main(), measure(), part_names() (+4 more)

### Community 92 - "translate.py"
Cohesion: 0.20
Nodes (7): sha1(), prepare(), split_sentences(), _translate_cvffad(), translate_file(), Translator, upper_ratio()

### Community 93 - "stackexchange.py"
Cohesion: 0.23
Nodes (7): collect(), _extract(), _rows(), strip_html(), fault_for(), primary_part_to_fault(), test_panne_type_seulement_si_sans_ambiguite()

### Community 94 - "evaluate.py"
Cohesion: 0.31
Nodes (5): test_banc_evaluation(), load_cases(), main(), ranked_parts(), run()

### Community 95 - "test_espace_magasin.py"
Cohesion: 0.24
Nodes (6): new_otp(), _owner(), test_catalogue_d_une_fiche_non_validee_cache_au_public(), test_code_fixe_des_tests_seulement_avec_les_sms_de_console(), test_les_exemples_du_modele_s_importent_sans_erreur(), test_mode_console_annonce_sans_donner_le_code()

### Community 96 - "test_concurrence.py"
Cohesion: 0.28
Nodes (4): warmup(), _diagnose(), test_diagnostics_simultanes_pendant_la_reconstruction_des_index(), test_prechargement_sans_erreur()

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

### Community 105 - "sqlalchemy"
Cohesion: 0.27
Nodes (3): upgrade(), upgrade(), upgrade()

### Community 107 - "build_llm_dataset.py"
Cohesion: 0.31
Nodes (3): build(), explanation(), french_examples()

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

### Community 112 - "diagnosis"
Cohesion: 0.33
Nodes (5): _defer(), diagnosis(), diagnosis_answers(), _refine(), _save()

### Community 115 - "Modèles (étape 7)"
Cohesion: 0.29
Nodes (7): Ce que le banc a déjà appris (matière pour le mémoire), Données d'entraînement, Mesurer, Modèles (étape 7), Premiers résultats (14/11/2026, jeux synthétiques, sans modèle de langage), Qualité des réponses sur des textes écrits comme à Oran (18/11/2026), Variante D : modèle de langage affiné par LoRA (15/11/2026)

## Knowledge Gaps
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `score_shop()` connect `test_recommendation.py` to `models.py`, `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)`?**
  _High betweenness centrality (0.228) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `run_diagnosis()` (e.g. with `DtcCode` and `DtcPart`) actually correct?**
  _`run_diagnosis()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `run_diagnosis` be split into smaller, more focused modules?**
  _Cohesion score 0.12315270935960591 - nodes in this community are weakly interconnected._
- **Why does `Carte du code` connect `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` to `test_recommendation.py`?**
  _High betweenness centrality (0.225) - this node is a cross-community bridge._
- **Should `environment` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.1437908496732026 - nodes in this community are weakly interconnected._
- **Should `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._