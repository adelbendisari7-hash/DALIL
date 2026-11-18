# Graph Report - DALIL  (2026-11-18)

## Corpus Check
- 214 files · ~367,219 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 29 file(s) not represented in the graph (top: .ipynb 7, (none) 6, .jsonl 4)

## Summary
- 1624 nodes · 3742 edges · 109 communities (88 shown, 21 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 290 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ff79a00`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- llm.py
- run_diagnosis
- models.py
- security.py
- environment
- imports.py
- package.json
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- train_baseline.py
- t
- models.py
- test_recommendation.py
- Context
- largus.py
- oran_csv_to_jsonl.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- admin/page.tsx
- steps
- config.py
- espace-magasin/page.tsx
- compilerOptions
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- shops.py
- taxonomy_map.py
- SOURCES.md
- ZipMemberStream
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- to_french
- diagnostic/[id]/page.tsx
- api
- make_notebooks.py
- build_training_set.py
- Modèles (étape 7)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- common.py
- next.config.mjs
- sw.js
- report.md
- Étape 11 : essais à Oran (protocole et compte rendu)
- classifier.py
- test_llm_chaine.py
- sqlalchemy
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
- public.py
- eval_with_llm.sh
- magasins/[id]/page.tsx
- run.py
- re
- i18n.ts
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Étape 9 : vérification sur un vrai téléphone
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- schemas.py
- main.py
- Plan : référentiel complet des véhicules d'Algérie et nouveaux jeux de données pour le diagnostic
- build_llm_dataset.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- load_vectors.py
- stackexchange.py
- argparse
- chunk_rows
- argparse
- RateLimiter
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
1. `get_settings()` - 60 edges
2. `run_diagnosis()` - 53 edges
3. `t()` - 50 edges
4. `Shop` - 40 edges
5. `User` - 39 edges
6. `api()` - 39 edges
7. `Base` - 32 edges
8. `PartCategory` - 31 edges
9. `DiagnosisInput` - 28 edges
10. `VehicleVariant` - 28 edges

## Surprising Connections (you probably didn't know these)
- `Conventions` --references--> `t()`  [INFERRED]
  CLAUDE.md → frontend/lib/i18n.ts
- `Carte du code` --references--> `score_shop()`  [INFERRED]
  CLAUDE.md → backend/app/services/recommendation.py
- `3. Phase C : apprentissage` --references--> `DenseIndex`  [INFERRED]
  docs/plan-referentiel-et-donnees.md → backend/app/services/diagnosis/retrieval.py
- `Décisions déjà prises par l'utilisateur (17/11/2026)` --references--> `glossary_misses()`  [INFERRED]
  docs/plan-referentiel-et-donnees.md → data/pipeline/translate.py
- `1. Où on en est` --references--> `score_shop()`  [INFERRED]
  docs/SUIVI.md → backend/app/services/recommendation.py

## Import Cycles
- None detected.

## Communities (109 total, 21 thin omitted)

### Community 0 - "llm.py"
Cohesion: 0.13
Nodes (9): AnthropicProvider, build_user_message(), _CallBudget, get_llm(), LLMProvider, OpenAICompatProvider, _parse_json(), rerank_with_llm() (+1 more)

### Community 1 - "run_diagnosis"
Cohesion: 0.11
Nodes (23): DiagnosisInput, informative_words(), non_fault_question(), _normalized(), _part_view(), _part_words(), parts_to_faults(), _pick_questions() (+15 more)

### Community 2 - "models.py"
Cohesion: 0.10
Nodes (27): Base, Brand, Commune, DtcCode, DtcPart, Embedding, Fault, FaultPart (+19 more)

### Community 3 - "security.py"
Cohesion: 0.08
Nodes (18): get_db(), make_engine(), OtpCode, me(), me_delete(), me_patch(), otp_request(), otp_verify() (+10 more)

### Community 4 - "environment"
Cohesion: 0.05
Nodes (39): build, depends_on, environment, ports, volumes, NEXT_PUBLIC_API_URL, args, context (+31 more)

### Community 5 - "imports.py"
Cohesion: 0.12
Nodes (17): PartCategory, ShopBrand, ShopCategory, admin_refs_import(), _mark_observed(), resolve_category(), resolve_variants(), search_categories() (+9 more)

### Community 6 - "package.json"
Cohesion: 0.06
Nodes (31): ADMIN_PHONE, makeCatalog(), OTP, PY_PATH, VENV, FakeRecognition, react-dom@^19.3.1, devDependencies (+23 more)

### Community 7 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.07
Nodes (27): Carte du code, Commandes, Conventions, DALIL — consignes pour Claude Code, 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes (+19 more)

### Community 8 - "train_baseline.py"
Cohesion: 0.21
Nodes (7): fiche_examples(), corpus_examples(), evaluate(), fault_to_part(), main(), relabel(), train_on_set()

### Community 9 - "t"
Cohesion: 0.09
Nodes (23): Home(), submit(), Family, Hit, PartsPage(), RefHit, ContactShop, Ctx (+15 more)

### Community 10 - "models.py"
Cohesion: 0.17
Nodes (14): AdminAction, ContactEvent, Feedback, VehicleRequest, admin_actions(), admin_import(), admin_merge(), admin_metrics() (+6 more)

### Community 11 - "test_recommendation.py"
Cohesion: 0.12
Nodes (29): freshness(), haversine_km(), proximity(), rank(), reliability(), score_shop(), ScoredShop, ShopSignals (+21 more)

### Community 12 - "Context"
Cohesion: 0.18
Nodes (9): download(), Record, collect(), aggregate(), _band(), collect(), _n(), _pct() (+1 more)

### Community 13 - "largus.py"
Cohesion: 0.17
Nodes (15): Context, category_family(), collect(), _connect(), label(), _plain(), scrub(), _vehicle() (+7 more)

### Community 14 - "oran_csv_to_jsonl.py"
Cohesion: 0.18
Nodes (10): test_conversion_des_fiches(), test_lignes_invalides_refusees_avec_la_raison(), test_modele_fourni_ne_contient_que_l_exemple(), test_vehicule_inconnu_garde_sans_vehicule_et_signale(), convert(), _fuzzy(), main(), _slugs() (+2 more)

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
Cohesion: 0.12
Nodes (5): Settings, Embedder, get_reranker(), _load(), Reranker

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
Cohesion: 0.12
Nodes (33): PartRequest, RequestResponse, Shop, User, catalog_template(), contact_event(), feedback(), _owned_shop() (+25 more)

### Community 23 - "taxonomy_map.py"
Cohesion: 0.16
Nodes (18): 4. Relier à la taxonomie, collect(), categories_en(), categories_fr(), family_fr(), family_of(), _match(), _norm() (+10 more)

### Community 24 - "SOURCES.md"
Cohesion: 0.09
Nodes (14): Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`), Anonymisation, Commande, Contenu, Forum L'Argus : « Panne auto, mécanique et entretien » (`largus_forum`), Limites, Usage dans DALIL, Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`) (+6 more)

### Community 25 - "ZipMemberStream"
Cohesion: 0.11
Nodes (10): 1. Vérifier avant d'écrire du code, 2. Déclarer la source, 3. Écrire le module de collecte, 5. Tester, charger, mesurer, Ajouter une source de données à DALIL, Ce qu'il ne faut pas faire, ZipMemberStream, SourceSpec (+2 more)

### Community 26 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.11
Nodes (18): A-actuel / classifieur seul | audit_ecriture_oran (8), A-actuel / classifieur seul | audit_ecriture_oran_controle (0), A-actuel / classifieur seul | demo_cases (0), A-actuel / classifieur seul | dev_fr_synthetique (2), A-actuel / D (chaîne complète) | audit_ecriture_oran (6), A-actuel / D (chaîne complète) | audit_ecriture_oran_controle (0), A-actuel / D (chaîne complète) | demo_cases (0), A-actuel / D (chaîne complète) | dev_fr_synthetique (1) (+10 more)

### Community 27 - "to_french"
Cohesion: 0.16
Nodes (11): _ar_word(), _french_like_hits(), _norm_ar(), _replace_phrases(), to_french(), extract_dtc(), strip_accents(), test_francais_inchange() (+3 more)

### Community 28 - "diagnostic/[id]/page.tsx"
Cohesion: 0.22
Nodes (10): Cause, DiagnosticResult(), answer(), rate(), Part, PartLabel(), Question, Ref (+2 more)

### Community 29 - "api"
Cohesion: 0.23
Nodes (15): Account(), remove(), errMsg(), ShopAdmin(), addProduct(), importFile(), respond(), saveProfile() (+7 more)

### Community 31 - "build_training_set.py"
Cohesion: 0.20
Nodes (11): dump(), test_poids_seuil_doublons_et_fuite(), test_validation_stable(), _write(), build(), is_val(), main(), norm() (+3 more)

### Community 32 - "Modèles (étape 7)"
Cohesion: 0.12
Nodes (14): Entraîner avec L'Argus (variante A contre CamemBERT), Faire tourner les modèles sur le portable, Mesurer (portable), Mettre un modèle en service, Ordre conseillé, Préparer le jeu de données Kaggle « dalil-pipeline », Étape 7 sur Kaggle : traduction et entraînement, Ce que le banc a déjà appris (matière pour le mémoire) (+6 more)

### Community 33 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), B-enfr / classifieur seul | demo_cases (6), B-enfr / classifieur seul | dev_fr_synthetique (14), B-enfr / D (chaîne complète) | demo_cases (3), B-enfr / D (chaîne complète) | dev_fr_synthetique (10) (+2 more)

### Community 34 - "common.py"
Cohesion: 0.27
Nodes (8): client(), get_json(), collectors(), collect_complaints(), collect_recalls(), _fetch(), _vehicle(), nhtsa_family()

### Community 38 - "Étape 11 : essais à Oran (protocole et compte rendu)"
Cohesion: 0.18
Nodes (10): 1. Ce que les essais doivent mesurer, 2. Avant les essais, 3. Déroulé, 4. Fiches de relevé, 5. Questionnaire (1 à 5, de « pas du tout » à « tout à fait »), 6. Modèle de compte rendu, A. Mécaniciens : constituer le jeu de test (le plus important), B. Magasins (environ 15 min chacun, sur leur propre téléphone) (+2 more)

### Community 40 - "classifier.py"
Cohesion: 0.11
Nodes (13): build_pipeline(), FaultClassifier, get_classifier(), load_classifier(), load_examples(), OnnxEncoderClassifier, train_baseline(), _maps() (+5 more)

### Community 43 - "test_llm_chaine.py"
Cohesion: 0.17
Nodes (15): Fake, fake(), install(), _run(), test_cache_expire(), test_cache_une_question_identique_ne_coute_qu_un_appel(), test_cas_de_demonstration_en_mode_complet_avec_modele(), test_le_classifieur_seul_n_appelle_pas_le_modele() (+7 more)

### Community 44 - "sqlalchemy"
Cohesion: 0.08
Nodes (12): upgrade(), upgrade(), upgrade(), km(), main(), nearest_commune(), prepare(), read_osm() (+4 more)

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
Cohesion: 0.11
Nodes (16): get_settings(), KnowledgeChunk, get_index(), _diag(), FakeEmbedder, FakeReranker, hybrid(), test_garde_fou_vectoriel_absent_en_mode_mots_cles() (+8 more)

### Community 51 - "DenseIndex"
Cohesion: 0.11
Nodes (6): get_embedder(), DenseIndex, Hit, HybridIndex, KeywordIndex, Étape 8 : recherche hybride et chaîne complète (16/11/2026)

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
Cohesion: 0.05
Nodes (39): admin_headers(), client(), db(), _db(), login(), cat_id(), test_admin_saisie_terrain_apparait_sur_la_carte(), test_contact_et_retour_modifient_le_score() (+31 more)

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

### Community 66 - "public.py"
Cohesion: 0.15
Nodes (20): DiagnosisSession, VehicleVariant, brands(), categories(), communes(), _defer(), diagnosis(), diagnosis_answers() (+12 more)

### Community 68 - "magasins/[id]/page.tsx"
Cohesion: 0.14
Nodes (13): Family, Named, Product, Shop, ShopMap, MapShop, ORAN, ShopMap() (+5 more)

### Community 69 - "run.py"
Cohesion: 0.11
Nodes (24): read_jsonl(), sha1(), write_jsonl(), export_training(), load_source(), summary(), cmd_collect(), cmd_load() (+16 more)

### Community 70 - "re"
Cohesion: 0.21
Nodes (12): clean_name(), _dump(), main(), norm(), variants_for(), brand_name(), engine_of(), fuel_of() (+4 more)

### Community 73 - "i18n.ts"
Cohesion: 0.11
Nodes (15): Login(), send(), LoginPage(), body, display, metadata, RootLayout(), viewport (+7 more)

### Community 74 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.13
Nodes (14): A-fort-x1 / D (chaîne complète) | audit_ecriture_oran (5), A-fort-x1 / D (chaîne complète) | audit_ecriture_oran_controle (1), A-fort-x1 / D (chaîne complète) | demo_cases (3), A-fort-x1 / D (chaîne complète) | dev_fr_synthetique (2), A-fort-x5 / D (chaîne complète) | audit_ecriture_oran (6), A-fort-x5 / D (chaîne complète) | audit_ecriture_oran_controle (0), A-fort-x5 / D (chaîne complète) | demo_cases (1), A-fort-x5 / D (chaîne complète) | dev_fr_synthetique (1) (+6 more)

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

### Community 85 - "main.py"
Cohesion: 0.14
Nodes (6): health(), start_warmup(), warmup(), _diagnose(), test_diagnostics_simultanes_pendant_la_reconstruction_des_index(), test_prechargement_sans_erreur()

### Community 86 - "Plan : référentiel complet des véhicules d'Algérie et nouveaux jeux de données pour le diagnostic"
Cohesion: 0.14
Nodes (13): 0. Objectifs et critères de fin, 1. Phase A : référentiel des véhicules, 2. Phase B : collecte des nouvelles données, 3. Phase C : apprentissage, 4. Phase D : documentation et clôture, 5. Ordre et volume estimé, 6. Sources consultées pour ce plan, A1. Modèles à ajouter (+5 more)

### Community 87 - "build_llm_dataset.py"
Cohesion: 0.43
Nodes (3): build(), explanation(), french_examples()

### Community 88 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.29
Nodes (6): A / D (chaîne complète) | audit_ecriture_oran (6), A / D (chaîne complète) | audit_ecriture_oran_controle (0), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (1), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261118-2103 referentiel

### Community 89 - "load_vectors.py"
Cohesion: 0.40
Nodes (5): check_ids(), check_queries(), fill_db(), install(), main()

### Community 90 - "stackexchange.py"
Cohesion: 0.17
Nodes (7): collect(), _extract(), _rows(), strip_html(), fault_for(), primary_part_to_fault(), test_panne_type_seulement_si_sans_ambiguite()

### Community 91 - "argparse"
Cohesion: 0.48
Nodes (5): _as_list(), _first(), iter_records(), main(), make_translator()

### Community 93 - "chunk_rows"
Cohesion: 0.47
Nodes (5): chunk_rows(), LicenseError, _rec(), test_chargement_refuse_sans_licence(), test_texte_original_garde_a_cote_de_la_traduction()

### Community 94 - "argparse"
Cohesion: 0.16
Nodes (10): test_banc_evaluation(), anonymize(), main(), scrub(), fetch(), main(), load_cases(), main() (+2 more)

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
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `score_shop()` connect `test_recommendation.py` to `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `run_diagnosis()` (e.g. with `DtcCode` and `DtcPart`) actually correct?**
  _`run_diagnosis()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._
- **Why does `Carte du code` connect `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` to `test_recommendation.py`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **Should `run_diagnosis` be split into smaller, more focused modules?**
  _Cohesion score 0.10960960960960961 - nodes in this community are weakly interconnected._
- **Should `models.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10204081632653061 - nodes in this community are weakly interconnected._
- **Should `security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0782608695652174 - nodes in this community are weakly interconnected._