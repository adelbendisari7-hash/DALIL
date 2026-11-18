# Graph Report - DALIL  (2026-11-18)

## Corpus Check
- 206 files · ~357,954 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 28 file(s) not represented in the graph (top: (none) 6, .ipynb 6, .jsonl 4)

## Summary
- 1552 nodes · 3593 edges · 113 communities (90 shown, 23 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 286 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `26fbcabb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- llm.py
- run_diagnosis
- public.py
- security.py
- environment
- imports.py
- package.json
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- load_vectors.py
- t
- models.py
- test_recommendation.py
- mot.py
- largus.py
- oran_csv_to_jsonl.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- admin/page.tsx
- steps
- retrieval.py
- espace-magasin/page.tsx
- compilerOptions
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- shops.py
- taxonomy_map.py
- SOURCES.md
- ZipMemberStream
- test_concurrence.py
- to_french
- diagnostic/[id]/page.tsx
- api
- make_notebooks.py
- seed.py
- Modèles (étape 7)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- common.py
- next.config.mjs
- sw.js
- report.md
- Étape 11 : essais à Oran (protocole et compte rendu)
- classifier.py
- test_llm_chaine.py
- db.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- magasins/page.tsx
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- get_settings
- DenseIndex
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
- Étape 8 : chaîne de diagnostic, plan proposé (à valider avant de coder)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Embedding
- eval_with_llm.sh
- magasins/[id]/page.tsx
- test_pipeline.py
- build_vehicles.py
- i18n.ts
- pipeline.py
- Étape 9 : vérification sur un vrai téléphone
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- schemas.py
- test_referentiel.py
- kaggle_run.py
- build_llm_dataset.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- train_baseline.py
- stackexchange.py
- argparse
- get_settings
- evaluate.py
- sources/__init__.py
- Le marché automobile algérien : ce qu'il implique pour DALIL
- config.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- re
- main.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 60 edges
2. `run_diagnosis()` - 53 edges
3. `t()` - 50 edges
4. `Shop` - 39 edges
5. `User` - 39 edges
6. `api()` - 39 edges
7. `Base` - 32 edges
8. `PartCategory` - 31 edges
9. `DiagnosisInput` - 28 edges
10. `VehicleVariant` - 28 edges

## Surprising Connections (you probably didn't know these)
- `Carte du code` --references--> `score_shop()`  [INFERRED]
  CLAUDE.md → backend/app/services/recommendation.py
- `Conventions` --references--> `t()`  [INFERRED]
  CLAUDE.md → frontend/lib/i18n.ts
- `1. Où on en est` --references--> `score_shop()`  [INFERRED]
  docs/SUIVI.md → backend/app/services/recommendation.py
- `1. Ce qui existe déjà (étapes 3 à 7)` --references--> `_CallBudget`  [INFERRED]
  docs/plan-etape-8.md → backend/app/services/diagnosis/llm.py
- `3. Écrire le module de collecte` --references--> `ZipMemberStream`  [INFERRED]
  .claude/skills/ajouter-source-donnees/SKILL.md → data/pipeline/common.py

## Import Cycles
- None detected.

## Communities (113 total, 23 thin omitted)

### Community 0 - "llm.py"
Cohesion: 0.13
Nodes (9): AnthropicProvider, build_user_message(), _CallBudget, get_llm(), LLMProvider, OpenAICompatProvider, _parse_json(), rerank_with_llm() (+1 more)

### Community 1 - "run_diagnosis"
Cohesion: 0.23
Nodes (9): DiagnosisInput, informative_words(), test_demo_case(), test_mot_seul_avec_code_obd_reste_un_diagnostic(), test_mot_seul_pas_de_resultat_sur(), test_mot_seul_puis_reponse_donne_un_resultat(), test_motorisation_inconnue_ne_penalise_aucune_panne(), test_diagnostic_en_mode_hybride() (+1 more)

### Community 2 - "public.py"
Cohesion: 0.15
Nodes (20): DiagnosisSession, VehicleVariant, brands(), categories(), communes(), _defer(), diagnosis(), diagnosis_answers() (+12 more)

### Community 3 - "security.py"
Cohesion: 0.11
Nodes (8): client_hash(), ConsoleSms, current_user(), current_user_optional(), get_sms_sender(), RateLimiter, require_role(), SmsSender

### Community 4 - "environment"
Cohesion: 0.05
Nodes (39): build, depends_on, environment, ports, volumes, NEXT_PUBLIC_API_URL, args, context (+31 more)

### Community 5 - "imports.py"
Cohesion: 0.14
Nodes (11): PartCategory, resolve_category(), resolve_variants(), search_categories(), parts_to_faults(), _float(), import_products(), import_shops() (+3 more)

### Community 6 - "package.json"
Cohesion: 0.06
Nodes (31): ADMIN_PHONE, makeCatalog(), OTP, PY_PATH, VENV, FakeRecognition, react-dom@^19.3.1, devDependencies (+23 more)

### Community 7 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.07
Nodes (27): Carte du code, Commandes, Conventions, DALIL — consignes pour Claude Code, 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes (+19 more)

### Community 8 - "load_vectors.py"
Cohesion: 0.40
Nodes (5): check_ids(), check_queries(), fill_db(), install(), main()

### Community 9 - "t"
Cohesion: 0.09
Nodes (23): Home(), submit(), Family, Hit, PartsPage(), RefHit, ContactShop, Ctx (+15 more)

### Community 10 - "models.py"
Cohesion: 0.15
Nodes (15): AdminAction, ContactEvent, Feedback, VehicleRequest, admin_actions(), admin_import(), admin_merge(), admin_metrics() (+7 more)

### Community 11 - "test_recommendation.py"
Cohesion: 0.11
Nodes (31): category_lineage(), freshness(), haversine_km(), proximity(), rank(), recommend(), reliability(), score_shop() (+23 more)

### Community 12 - "mot.py"
Cohesion: 0.31
Nodes (7): Context, aggregate(), _band(), collect(), _n(), _pct(), rfr_categories()

### Community 13 - "largus.py"
Cohesion: 0.14
Nodes (14): category_family(), collect(), _connect(), label(), _plain(), scrub(), _vehicle(), _with_family() (+6 more)

### Community 14 - "oran_csv_to_jsonl.py"
Cohesion: 0.15
Nodes (11): test_conversion_des_fiches(), test_lignes_invalides_refusees_avec_la_raison(), test_modele_fourni_ne_contient_que_l_exemple(), test_vehicule_inconnu_garde_sans_vehicule_et_signale(), sha1(), convert(), _fuzzy(), main() (+3 more)

### Community 15 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.09
Nodes (22): A-amorcage / classifieur seul | demo_cases (0), A-amorcage / classifieur seul | dev_fr_synthetique (4), A-amorcage / D (chaîne complète) | demo_cases (0), A-amorcage / D (chaîne complète) | dev_fr_synthetique (3), A-corpus-panne / classifieur seul | demo_cases (1), A-corpus-panne / classifieur seul | dev_fr_synthetique (4), A-corpus-panne / D (chaîne complète) | demo_cases (1), A-corpus-panne / D (chaîne complète) | dev_fr_synthetique (3) (+14 more)

### Community 16 - "admin/page.tsx"
Cohesion: 0.29
Nodes (7): Admin(), act(), upload(), Metrics, pct(), Shop, Tab

### Community 17 - "steps"
Cohesion: 0.12
Nodes (20): runs-on, steps, DALIL_DATABASE_URL, runs-on, steps, jobs, backend, frontend (+12 more)

### Community 18 - "retrieval.py"
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
Cohesion: 0.13
Nodes (33): PartRequest, Product, RequestResponse, Shop, User, admin_stale(), catalog_template(), contact_event() (+25 more)

### Community 23 - "taxonomy_map.py"
Cohesion: 0.19
Nodes (17): 4. Relier à la taxonomie, collect(), categories_en(), categories_fr(), family_fr(), family_of(), _match(), nhtsa_family() (+9 more)

### Community 24 - "SOURCES.md"
Cohesion: 0.09
Nodes (14): Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`), Anonymisation, Commande, Contenu, Forum L'Argus : « Panne auto, mécanique et entretien » (`largus_forum`), Limites, Usage dans DALIL, Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`) (+6 more)

### Community 25 - "ZipMemberStream"
Cohesion: 0.20
Nodes (3): ZipMemberStream, test_lecture_en_flux_d_un_zip(), test_reprise_apres_coupure_reseau()

### Community 26 - "test_concurrence.py"
Cohesion: 0.24
Nodes (5): warmup(), _diagnose(), test_diagnostics_simultanes_pendant_la_reconstruction_des_index(), test_prechargement_sans_erreur(), Étape 8 : recherche hybride et chaîne complète (16/11/2026)

### Community 27 - "to_french"
Cohesion: 0.14
Nodes (13): _ar_word(), _french_like_hits(), _norm_ar(), _replace_phrases(), to_french(), strip_accents(), test_arabe_incompris_message_clair(), test_diagnostic_en_darija() (+5 more)

### Community 28 - "diagnostic/[id]/page.tsx"
Cohesion: 0.22
Nodes (10): Cause, DiagnosticResult(), answer(), rate(), Part, PartLabel(), Question, Ref (+2 more)

### Community 29 - "api"
Cohesion: 0.23
Nodes (15): Account(), remove(), errMsg(), ShopAdmin(), addProduct(), importFile(), respond(), saveProfile() (+7 more)

### Community 31 - "seed.py"
Cohesion: 0.14
Nodes (28): Base, Brand, Commune, DtcCode, DtcPart, Fault, FaultPart, Model (+20 more)

### Community 32 - "Modèles (étape 7)"
Cohesion: 0.13
Nodes (13): Faire tourner les modèles sur le portable, Mesurer (portable), Mettre un modèle en service, Ordre conseillé, Préparer le jeu de données Kaggle « dalil-pipeline », Étape 7 sur Kaggle : traduction et entraînement, Ce que le banc a déjà appris (matière pour le mémoire), Données d'entraînement (+5 more)

### Community 33 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), B-enfr / classifieur seul | demo_cases (6), B-enfr / classifieur seul | dev_fr_synthetique (14), B-enfr / D (chaîne complète) | demo_cases (3), B-enfr / D (chaîne complète) | dev_fr_synthetique (10) (+2 more)

### Community 34 - "common.py"
Cohesion: 0.20
Nodes (11): 3. Écrire le module de collecte, client(), download(), get_json(), Record, collectors(), collect(), collect_complaints() (+3 more)

### Community 38 - "Étape 11 : essais à Oran (protocole et compte rendu)"
Cohesion: 0.18
Nodes (10): 1. Ce que les essais doivent mesurer, 2. Avant les essais, 3. Déroulé, 4. Fiches de relevé, 5. Questionnaire (1 à 5, de « pas du tout » à « tout à fait »), 6. Modèle de compte rendu, A. Mécaniciens : constituer le jeu de test (le plus important), B. Magasins (environ 15 min chacun, sur leur propre téléphone) (+2 more)

### Community 40 - "classifier.py"
Cohesion: 0.11
Nodes (13): build_pipeline(), FaultClassifier, get_classifier(), load_classifier(), load_examples(), OnnxEncoderClassifier, train_baseline(), _maps() (+5 more)

### Community 43 - "test_llm_chaine.py"
Cohesion: 0.17
Nodes (15): Fake, fake(), install(), _run(), test_cache_expire(), test_cache_une_question_identique_ne_coute_qu_un_appel(), test_cas_de_demonstration_en_mode_complet_avec_modele(), test_le_classifieur_seul_n_appelle_pas_le_modele() (+7 more)

### Community 44 - "db.py"
Cohesion: 0.14
Nodes (6): get_db(), make_engine(), admin_headers(), client(), db(), _db()

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

### Community 50 - "get_settings"
Cohesion: 0.10
Nodes (15): KnowledgeChunk, get_index(), _diag(), FakeEmbedder, FakeReranker, hybrid(), test_garde_fou_vectoriel_absent_en_mode_mots_cles(), test_garde_fou_vectoriel_du_domaine() (+7 more)

### Community 51 - "DenseIndex"
Cohesion: 0.07
Nodes (17): get_embedder(), DenseIndex, Hit, HybridIndex, KeywordIndex, 0. Objectifs et critères de fin, 1. Phase A : référentiel des véhicules, 2. Phase B : collecte des nouvelles données (+9 more)

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
Cohesion: 0.08
Nodes (23): upgrade(), upgrade(), upgrade(), login(), cat_id(), test_admin_saisie_terrain_apparait_sur_la_carte(), test_contact_et_retour_modifient_le_score(), test_demande_diffusee() (+15 more)

### Community 61 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (2), C (recherche + LM) | demo_cases (2), C (recherche + LM) | dev_fr_synthetique (14), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261115-2250 hybride-sans-lm

### Community 62 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), C (recherche + LM) | demo_cases (2), C (recherche + LM) | dev_fr_synthetique (11), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261116-0000 hybride-garde-vecteurs

### Community 63 - "Étape 8 : chaîne de diagnostic, plan proposé (à valider avant de coder)"
Cohesion: 0.33
Nodes (5): 2. Ce qui manque, par ordre de priorité, 3. Hors périmètre de l'étape 8, 4. Tests ajoutés, 5. Décisions demandées à l'équipe, Étape 8 : chaîne de diagnostic, plan proposé (à valider avant de coder)

### Community 64 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261115-2244 lora-q8

### Community 65 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (1), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261116-0054 lora-q8-hybride

### Community 68 - "magasins/[id]/page.tsx"
Cohesion: 0.14
Nodes (13): Family, Named, Product, Shop, ShopMap, MapShop, ORAN, ShopMap() (+5 more)

### Community 69 - "test_pipeline.py"
Cohesion: 0.09
Nodes (32): read_jsonl(), write_jsonl(), chunk_rows(), dump(), export_training(), LicenseError, load_source(), summary() (+24 more)

### Community 70 - "build_vehicles.py"
Cohesion: 0.29
Nodes (5): clean_name(), _dump(), main(), norm(), variants_for()

### Community 73 - "i18n.ts"
Cohesion: 0.11
Nodes (15): Login(), send(), LoginPage(), body, display, metadata, RootLayout(), viewport (+7 more)

### Community 74 - "pipeline.py"
Cohesion: 0.19
Nodes (12): extract_dtc(), normalize(), non_fault_question(), _normalized(), _part_view(), _part_words(), _pick_questions(), question_bank() (+4 more)

### Community 75 - "Étape 9 : vérification sur un vrai téléphone"
Cohesion: 0.40
Nodes (4): Parcours à suivre (cocher), Préparer, Résultat, Étape 9 : vérification sur un vrai téléphone

### Community 76 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1533 hybride-int8-10x256

### Community 77 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1542 hybride-int8-10x256-vecteurs-repares

### Community 78 - "schemas.py"
Cohesion: 0.18
Nodes (13): AnswersRequest, ContactEventIn, DiagnosisRequest, FeedbackIn, _iso(), MePatch, OtpRequest, OtpVerify (+5 more)

### Community 85 - "test_referentiel.py"
Cohesion: 0.15
Nodes (3): anonymize(), main(), scrub()

### Community 86 - "kaggle_run.py"
Cohesion: 0.27
Nodes (10): cmd_adapter(), cmd_dataset(), cmd_output(), cmd_push(), cmd_status(), _force_remove(), kaggle(), main() (+2 more)

### Community 87 - "build_llm_dataset.py"
Cohesion: 0.43
Nodes (3): build(), explanation(), french_examples()

### Community 88 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (6), A / D (chaîne complète) | audit_ecriture_oran_controle (0), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-2103 referentiel

### Community 89 - "train_baseline.py"
Cohesion: 0.23
Nodes (7): fiche_examples(), export(), corpus_examples(), evaluate(), fault_to_part(), main(), relabel()

### Community 90 - "stackexchange.py"
Cohesion: 0.23
Nodes (7): collect(), _extract(), _rows(), strip_html(), fault_for(), primary_part_to_fault(), test_panne_type_seulement_si_sans_ambiguite()

### Community 91 - "argparse"
Cohesion: 0.26
Nodes (7): _as_list(), _first(), iter_records(), main(), make_translator(), fetch(), main()

### Community 93 - "get_settings"
Cohesion: 0.19
Nodes (12): get_settings(), OtpCode, me(), me_delete(), me_patch(), otp_request(), otp_verify(), _user_out() (+4 more)

### Community 94 - "evaluate.py"
Cohesion: 0.31
Nodes (5): test_banc_evaluation(), load_cases(), main(), ranked_parts(), run()

### Community 95 - "sources/__init__.py"
Cohesion: 0.29
Nodes (6): 1. Vérifier avant d'écrire du code, 2. Déclarer la source, 5. Tester, charger, mesurer, Ajouter une source de données à DALIL, Ce qu'il ne faut pas faire, SourceSpec

### Community 97 - "Le marché automobile algérien : ce qu'il implique pour DALIL"
Cohesion: 0.25
Nodes (7): 1. Le parc : vieux, français, et de plus en plus diesel à la revente, 2. Oran, 3. Ce qui se vend aujourd'hui (2023-2026), 4. Écarts avec le référentiel actuel de DALIL (`data/seed/vehicles.json`), 5. Recommandations pour le site, Le marché automobile algérien : ce qu'il implique pour DALIL, Sources

### Community 98 - "config.py"
Cohesion: 0.20
Nodes (4): Settings, _owner(), test_catalogue_d_une_fiche_non_validee_cache_au_public(), test_les_exemples_du_modele_s_importent_sans_erreur()

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

### Community 106 - "re"
Cohesion: 0.51
Nodes (7): brand_name(), engine_of(), fuel_of(), main(), model_key(), pct(), _plain()

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
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `score_shop()` connect `test_recommendation.py` to `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)`?**
  _High betweenness centrality (0.187) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `run_diagnosis()` (e.g. with `DtcCode` and `DtcPart`) actually correct?**
  _`run_diagnosis()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._
- **Why does `Carte du code` connect `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` to `test_recommendation.py`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Shop` (e.g. with `admin_merge()` and `admin_metrics()`) actually correct?**
  _`Shop` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Should `public.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14919354838709678 - nodes in this community are weakly interconnected._
- **Should `security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10507246376811594 - nodes in this community are weakly interconnected._