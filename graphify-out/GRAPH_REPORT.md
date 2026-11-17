# Graph Report - DALIL  (2026-11-17)

## Corpus Check
- 170 files · ~111,738 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 26 file(s) not represented in the graph (top: (none) 6, .ipynb 6, .csv 3)

## Summary
- 1363 nodes · 3219 edges · 86 communities (63 shown, 23 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 256 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `de7ff0d9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- llm.py
- pipeline.py
- models.py
- User
- environment
- imports.py
- package.json
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- load_vectors.py
- t
- models.py
- test_recommendation.py
- mot.py
- translate.py
- json
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- api.ts
- steps
- retrieval.py
- espace-magasin/page.tsx
- compilerOptions
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- shops.py
- test_pipeline.py
- SOURCES.md
- ZipMemberStream
- main.py
- security.py
- diagnostic/[id]/page.tsx
- api
- make_notebooks.py
- PartCategory
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
- test_retrieval_hybride.py
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
- run.py
- layout.tsx
- RateLimiter
- Étape 9 : vérification sur un vrai téléphone
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 58 edges
2. `t()` - 50 edges
3. `run_diagnosis()` - 41 edges
4. `User` - 39 edges
5. `Shop` - 38 edges
6. `api()` - 38 edges
7. `Base` - 31 edges
8. `PartCategory` - 30 edges
9. `VehicleVariant` - 22 edges
10. `DiagnosisInput` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Carte du code` --references--> `score_shop()`  [INFERRED]
  CLAUDE.md → backend/app/services/recommendation.py
- `Conventions` --references--> `t()`  [INFERRED]
  CLAUDE.md → frontend/lib/i18n.ts
- `1. Où on en est` --references--> `score_shop()`  [INFERRED]
  docs/SUIVI.md → backend/app/services/recommendation.py
- `1. Ce qui existe déjà (étapes 3 à 7)` --references--> `_CallBudget`  [INFERRED]
  docs/plan-etape-8.md → backend/app/services/diagnosis/llm.py
- `3. Écrire le module de collecte` --references--> `Record`  [INFERRED]
  .claude/skills/ajouter-source-donnees/SKILL.md → data/pipeline/common.py

## Import Cycles
- None detected.

## Communities (86 total, 23 thin omitted)

### Community 0 - "llm.py"
Cohesion: 0.13
Nodes (9): AnthropicProvider, build_user_message(), _CallBudget, get_llm(), LLMProvider, OpenAICompatProvider, _parse_json(), rerank_with_llm() (+1 more)

### Community 1 - "pipeline.py"
Cohesion: 0.11
Nodes (20): detect_lang(), extract_dtc(), strip_accents(), DiagnosisInput, informative_words(), _normalized(), _part_view(), parts_to_faults() (+12 more)

### Community 2 - "models.py"
Cohesion: 0.11
Nodes (36): Brand, Commune, DtcCode, DtcPart, Fault, FaultPart, Model, PartReference (+28 more)

### Community 3 - "User"
Cohesion: 0.11
Nodes (22): OtpCode, User, me(), me_delete(), me_patch(), otp_request(), otp_verify(), _user_out() (+14 more)

### Community 4 - "environment"
Cohesion: 0.05
Nodes (39): build, depends_on, environment, ports, volumes, NEXT_PUBLIC_API_URL, args, context (+31 more)

### Community 5 - "imports.py"
Cohesion: 0.17
Nodes (11): normalize_phone(), resolve_category(), resolve_variants(), search_categories(), normalize(), _float(), import_products(), import_shops() (+3 more)

### Community 6 - "package.json"
Cohesion: 0.06
Nodes (31): ADMIN_PHONE, makeCatalog(), OTP, PY_PATH, VENV, FakeRecognition, react-dom@^19.3.1, devDependencies (+23 more)

### Community 7 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.07
Nodes (27): Carte du code, Commandes, Conventions, DALIL — consignes pour Claude Code, 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes (+19 more)

### Community 8 - "load_vectors.py"
Cohesion: 0.25
Nodes (6): Embedder, check_ids(), check_queries(), fill_db(), install(), main()

### Community 9 - "t"
Cohesion: 0.11
Nodes (19): NotFound(), Home(), submit(), Family, Hit, PartsPage(), RefHit, Brand (+11 more)

### Community 10 - "models.py"
Cohesion: 0.12
Nodes (20): Base, AdminAction, ContactEvent, DiagnosisSession, Feedback, PartRequest, Product, utcnow() (+12 more)

### Community 11 - "test_recommendation.py"
Cohesion: 0.13
Nodes (27): freshness(), rank(), reliability(), score_shop(), ScoredShop, ShopSignals, order(), S() (+19 more)

### Community 12 - "mot.py"
Cohesion: 0.13
Nodes (16): download(), Record, collect(), Context, aggregate(), _band(), collect(), _n() (+8 more)

### Community 13 - "translate.py"
Cohesion: 0.18
Nodes (8): test_postedition_impose_le_lexique(), test_texte_en_capitales_remis_en_casse_normale(), postedit(), prepare(), _translate_cvffad(), translate_file(), Translator, upper_ratio()

### Community 14 - "json"
Cohesion: 0.08
Nodes (25): test_banc_evaluation(), test_conversion_des_fiches(), test_lignes_invalides_refusees_avec_la_raison(), test_modele_fourni_ne_contient_que_l_exemple(), test_vehicule_inconnu_garde_sans_vehicule_et_signale(), sha1(), dump(), _as_list() (+17 more)

### Community 15 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.09
Nodes (22): A-amorcage / classifieur seul | demo_cases (0), A-amorcage / classifieur seul | dev_fr_synthetique (4), A-amorcage / D (chaîne complète) | demo_cases (0), A-amorcage / D (chaîne complète) | dev_fr_synthetique (3), A-corpus-panne / classifieur seul | demo_cases (1), A-corpus-panne / classifieur seul | dev_fr_synthetique (4), A-corpus-panne / D (chaîne complète) | demo_cases (1), A-corpus-panne / D (chaîne complète) | dev_fr_synthetique (3) (+14 more)

### Community 16 - "api.ts"
Cohesion: 0.25
Nodes (10): Metrics, Shop, Tab, API, ApiError, session, store, User (+2 more)

### Community 17 - "steps"
Cohesion: 0.12
Nodes (20): runs-on, steps, DALIL_DATABASE_URL, runs-on, steps, jobs, backend, frontend (+12 more)

### Community 18 - "retrieval.py"
Cohesion: 0.12
Nodes (4): Settings, get_reranker(), _load(), Reranker

### Community 19 - "espace-magasin/page.tsx"
Cohesion: 0.12
Nodes (25): FieldForm(), submit(), Claimable, errMsg(), Family, Inbox, Product, Shop (+17 more)

### Community 20 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 21 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.11
Nodes (17): 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes, 14. Protection du projet et statut de startup, 15. Sources, 1. Vision et périmètre, 2. Acteurs et parcours (+9 more)

### Community 22 - "shops.py"
Cohesion: 0.13
Nodes (26): ProductFitment, Shop, catalog_template(), contact_event(), feedback(), _owned_shop(), part_request_inbox(), part_request_respond() (+18 more)

### Community 23 - "test_pipeline.py"
Cohesion: 0.12
Nodes (26): 4. Relier à la taxonomie, collectors(), collect_complaints(), collect_recalls(), _vehicle(), categories_en(), categories_fr(), family_fr() (+18 more)

### Community 24 - "SOURCES.md"
Cohesion: 0.13
Nodes (8): Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`), Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`), Fiche source : NHTSA, plaintes des propriétaires (`nhtsa_complaints`), Fiche source : NHTSA, campagnes de rappel (`nhtsa_recalls`), Fiche source : RappelConso, rappels automobiles (`rappelconso`), Registre des sources de données, Sources exclues, Fiche source : Stack Exchange, Motor Vehicle Maintenance & Repair (`stackexchange_mechanics`)

### Community 25 - "ZipMemberStream"
Cohesion: 0.11
Nodes (10): 1. Vérifier avant d'écrire du code, 2. Déclarer la source, 3. Écrire le module de collecte, 5. Tester, charger, mesurer, Ajouter une source de données à DALIL, Ce qu'il ne faut pas faire, ZipMemberStream, SourceSpec (+2 more)

### Community 26 - "main.py"
Cohesion: 0.13
Nodes (7): health(), start_warmup(), warmup(), _diagnose(), test_diagnostics_simultanes_pendant_la_reconstruction_des_index(), test_prechargement_sans_erreur(), Étape 8 : recherche hybride et chaîne complète (16/11/2026)

### Community 27 - "security.py"
Cohesion: 0.10
Nodes (9): get_db(), make_engine(), client_hash(), ConsoleSms, current_user(), current_user_optional(), hash_code(), require_role() (+1 more)

### Community 28 - "diagnostic/[id]/page.tsx"
Cohesion: 0.22
Nodes (10): Cause, DiagnosticResult(), answer(), rate(), Part, PartLabel(), Question, Ref (+2 more)

### Community 29 - "api"
Cohesion: 0.18
Nodes (15): Admin(), act(), upload(), pct(), Account(), remove(), Login(), send() (+7 more)

### Community 31 - "PartCategory"
Cohesion: 0.25
Nodes (11): PartCategory, RequestResponse, ShopBrand, ShopCategory, VehicleVariant, _mark_observed(), part_request_create(), category_lineage() (+3 more)

### Community 32 - "Modèles (étape 7)"
Cohesion: 0.14
Nodes (12): Faire tourner les modèles sur le portable, Mesurer (portable), Mettre un modèle en service, Ordre conseillé, Préparer le jeu de données Kaggle « dalil-pipeline », Étape 7 sur Kaggle : traduction et entraînement, Ce que le banc a déjà appris (matière pour le mémoire), Données d'entraînement (+4 more)

### Community 33 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), B-enfr / classifieur seul | demo_cases (6), B-enfr / classifieur seul | dev_fr_synthetique (14), B-enfr / D (chaîne complète) | demo_cases (3), B-enfr / D (chaîne complète) | dev_fr_synthetique (10) (+2 more)

### Community 34 - "common.py"
Cohesion: 0.38
Nodes (3): client(), get_json(), _fetch()

### Community 38 - "Étape 11 : essais à Oran (protocole et compte rendu)"
Cohesion: 0.18
Nodes (10): 1. Ce que les essais doivent mesurer, 2. Avant les essais, 3. Déroulé, 4. Fiches de relevé, 5. Questionnaire (1 à 5, de « pas du tout » à « tout à fait »), 6. Modèle de compte rendu, A. Mécaniciens : constituer le jeu de test (le plus important), B. Magasins (environ 15 min chacun, sur leur propre téléphone) (+2 more)

### Community 40 - "classifier.py"
Cohesion: 0.07
Nodes (22): build_pipeline(), FaultClassifier, fiche_examples(), get_classifier(), load_classifier(), load_examples(), OnnxEncoderClassifier, train_baseline() (+14 more)

### Community 43 - "test_llm_chaine.py"
Cohesion: 0.17
Nodes (15): Fake, fake(), install(), _run(), test_cache_expire(), test_cache_une_question_identique_ne_coute_qu_un_appel(), test_cas_de_demonstration_en_mode_complet_avec_modele(), test_le_classifieur_seul_n_appelle_pas_le_modele() (+7 more)

### Community 45 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.22
Nodes (8): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), C (recherche + LM) | demo_cases (4), C (recherche + LM) | dev_fr_synthetique (13), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261114-1722 couverture

### Community 46 - "magasins/page.tsx"
Cohesion: 0.24
Nodes (8): Rec, ShopMap, Shops(), broadcast(), ShopsPage(), ContactShop, Ctx, vehicleStore

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
Nodes (16): get_settings(), KnowledgeChunk, get_index(), _diag(), FakeEmbedder, FakeReranker, hybrid(), test_garde_fou_vectoriel_absent_en_mode_mots_cles() (+8 more)

### Community 51 - "DenseIndex"
Cohesion: 0.12
Nodes (5): get_embedder(), DenseIndex, Hit, HybridIndex, KeywordIndex

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
Nodes (40): new_otp(), admin_headers(), client(), db(), _db(), login(), cat_id(), test_admin_saisie_terrain_apparait_sur_la_carte() (+32 more)

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

### Community 69 - "run.py"
Cohesion: 0.17
Nodes (18): read_jsonl(), write_jsonl(), chunk_rows(), export_training(), LicenseError, load_source(), summary(), cmd_collect() (+10 more)

### Community 73 - "layout.tsx"
Cohesion: 0.29
Nodes (6): body, display, metadata, RootLayout(), viewport, TopBar()

### Community 75 - "Étape 9 : vérification sur un vrai téléphone"
Cohesion: 0.40
Nodes (4): Parcours à suivre (cocher), Préparer, Résultat, Étape 9 : vérification sur un vrai téléphone

### Community 76 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1533 hybride-int8-10x256

### Community 77 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1542 hybride-int8-10x256-vecteurs-repares

## Knowledge Gaps
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `score_shop()` connect `test_recommendation.py` to `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)`, `PartCategory`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `User` (e.g. with `admin_import()` and `admin_merge()`) actually correct?**
  _`User` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._
- **Why does `Carte du code` connect `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` to `test_recommendation.py`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Should `pipeline.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11428571428571428 - nodes in this community are weakly interconnected._
- **Should `models.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10530612244897959 - nodes in this community are weakly interconnected._
- **Should `User` be split into smaller, more focused modules?**
  _Cohesion score 0.1126984126984127 - nodes in this community are weakly interconnected._