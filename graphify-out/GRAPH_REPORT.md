# Graph Report - DALIL  (2026-11-18)

## Corpus Check
- 195 files · ~127,077 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 28 file(s) not represented in the graph (top: (none) 6, .ipynb 6, .jsonl 4)

## Summary
- 1465 nodes · 3350 edges · 112 communities (88 shown, 24 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 260 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f1b98005`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- llm.py
- run_diagnosis
- public.py
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
- test_pipeline.py
- oran_csv_to_jsonl.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- api.ts
- steps
- retrieval.py
- espace-magasin/page.tsx
- compilerOptions
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- shops.py
- taxonomy_map.py
- SOURCES.md
- ZipMemberStream
- main.py
- security.py
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
- test_models.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- magasins/page.tsx
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- hybrid
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
- models.py
- eval_with_llm.sh
- magasins/[id]/page.tsx
- run.py
- layout.tsx
- pipeline.py
- Étape 9 : vérification sur un vrai téléphone
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- kaggle_run.py
- json
- conftest.py
- train_baseline.py
- stackexchange.py
- argparse
- test_espace_magasin.py
- Plan : référentiel complet des véhicules d'Algérie et nouveaux jeux de données pour le diagnostic
- evaluate.py
- sources/__init__.py
- .ensure_reference
- Le marché automobile algérien : ce qu'il implique pour DALIL
- Modèles (étape 7)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- KnowledgeChunk
- KeywordIndex
- HybridIndex
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 59 edges
2. `t()` - 50 edges
3. `run_diagnosis()` - 46 edges
4. `User` - 39 edges
5. `Shop` - 38 edges
6. `api()` - 38 edges
7. `Base` - 31 edges
8. `PartCategory` - 30 edges
9. `DiagnosisInput` - 26 edges
10. `VehicleVariant` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Carte du code` --references--> `score_shop()`  [INFERRED]
  CLAUDE.md → backend/app/services/recommendation.py
- `Conventions` --references--> `t()`  [INFERRED]
  CLAUDE.md → frontend/lib/i18n.ts
- `1. Où on en est` --references--> `score_shop()`  [INFERRED]
  docs/SUIVI.md → backend/app/services/recommendation.py
- `Décisions déjà prises par l'utilisateur (17/11/2026)` --references--> `glossary_misses()`  [INFERRED]
  docs/plan-referentiel-et-donnees.md → data/pipeline/translate.py
- `3. Phase C : apprentissage` --references--> `DenseIndex`  [INFERRED]
  docs/plan-referentiel-et-donnees.md → backend/app/services/diagnosis/retrieval.py

## Import Cycles
- None detected.

## Communities (112 total, 24 thin omitted)

### Community 0 - "llm.py"
Cohesion: 0.13
Nodes (9): AnthropicProvider, build_user_message(), _CallBudget, get_llm(), LLMProvider, OpenAICompatProvider, _parse_json(), rerank_with_llm() (+1 more)

### Community 1 - "run_diagnosis"
Cohesion: 0.13
Nodes (19): DiagnosisInput, informative_words(), _pick_questions(), question_bank(), _references(), run_diagnosis(), test_arabe_incompris_message_clair(), test_diagnostic_en_darija() (+11 more)

### Community 2 - "public.py"
Cohesion: 0.19
Nodes (16): DiagnosisSession, brands(), categories(), communes(), _defer(), diagnosis(), diagnosis_answers(), diagnosis_get() (+8 more)

### Community 3 - "User"
Cohesion: 0.10
Nodes (23): OtpCode, me(), me_delete(), me_patch(), otp_request(), otp_verify(), _user_out(), AnswersRequest (+15 more)

### Community 4 - "environment"
Cohesion: 0.05
Nodes (39): build, depends_on, environment, ports, volumes, NEXT_PUBLIC_API_URL, args, context (+31 more)

### Community 5 - "imports.py"
Cohesion: 0.16
Nodes (14): PartCategory, ShopBrand, ShopCategory, _set_links(), resolve_category(), resolve_variants(), _float(), import_products() (+6 more)

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
Cohesion: 0.11
Nodes (19): NotFound(), Home(), submit(), Family, Hit, PartsPage(), RefHit, Brand (+11 more)

### Community 10 - "models.py"
Cohesion: 0.16
Nodes (17): AdminAction, ContactEvent, Feedback, Product, User, admin_actions(), admin_import(), admin_merge() (+9 more)

### Community 11 - "test_recommendation.py"
Cohesion: 0.12
Nodes (29): freshness(), haversine_km(), proximity(), rank(), reliability(), score_shop(), ScoredShop, ShopSignals (+21 more)

### Community 12 - "mot.py"
Cohesion: 0.19
Nodes (14): 3. Écrire le module de collecte, download(), Record, collectors(), collect(), Context, aggregate(), _band() (+6 more)

### Community 13 - "test_pipeline.py"
Cohesion: 0.10
Nodes (21): sha1(), chunk_rows(), LicenseError, _rec(), test_chaque_source_a_sa_fiche_et_sa_licence(), test_chargement_refuse_sans_licence(), test_correspondance_anglais(), test_decoupage_en_phrases() (+13 more)

### Community 14 - "oran_csv_to_jsonl.py"
Cohesion: 0.16
Nodes (10): test_conversion_des_fiches(), test_lignes_invalides_refusees_avec_la_raison(), test_modele_fourni_ne_contient_que_l_exemple(), test_vehicule_inconnu_garde_sans_vehicule_et_signale(), convert(), _fuzzy(), main(), _slugs() (+2 more)

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
Cohesion: 0.10
Nodes (14): get_settings(), Settings, Embedder, get_embedder(), get_reranker(), _load(), Reranker, get_index() (+6 more)

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
Nodes (28): PartRequest, RequestResponse, Shop, catalog_template(), contact_event(), feedback(), _mark_observed(), _owned_shop() (+20 more)

### Community 23 - "taxonomy_map.py"
Cohesion: 0.25
Nodes (14): 4. Relier à la taxonomie, collect_complaints(), collect_recalls(), _vehicle(), categories_en(), categories_fr(), family_fr(), _match() (+6 more)

### Community 24 - "SOURCES.md"
Cohesion: 0.13
Nodes (8): Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`), Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`), Fiche source : NHTSA, plaintes des propriétaires (`nhtsa_complaints`), Fiche source : NHTSA, campagnes de rappel (`nhtsa_recalls`), Fiche source : RappelConso, rappels automobiles (`rappelconso`), Registre des sources de données, Sources exclues, Fiche source : Stack Exchange, Motor Vehicle Maintenance & Repair (`stackexchange_mechanics`)

### Community 25 - "ZipMemberStream"
Cohesion: 0.20
Nodes (3): ZipMemberStream, test_lecture_en_flux_d_un_zip(), test_reprise_apres_coupure_reseau()

### Community 26 - "main.py"
Cohesion: 0.15
Nodes (6): health(), start_warmup(), warmup(), _diagnose(), test_diagnostics_simultanes_pendant_la_reconstruction_des_index(), test_prechargement_sans_erreur()

### Community 27 - "security.py"
Cohesion: 0.08
Nodes (9): get_db(), make_engine(), client_hash(), ConsoleSms, current_user(), current_user_optional(), RateLimiter, require_role() (+1 more)

### Community 28 - "diagnostic/[id]/page.tsx"
Cohesion: 0.22
Nodes (10): Cause, DiagnosticResult(), answer(), rate(), Part, PartLabel(), Question, Ref (+2 more)

### Community 29 - "api"
Cohesion: 0.18
Nodes (15): Admin(), act(), upload(), pct(), Account(), remove(), Login(), send() (+7 more)

### Community 31 - "seed.py"
Cohesion: 0.21
Nodes (22): Base, Commune, DtcCode, DtcPart, Fault, FaultPart, Model, ProductFitment (+14 more)

### Community 32 - "Modèles (étape 7)"
Cohesion: 0.25
Nodes (6): Faire tourner les modèles sur le portable, Mesurer (portable), Mettre un modèle en service, Ordre conseillé, Préparer le jeu de données Kaggle « dalil-pipeline », Étape 7 sur Kaggle : traduction et entraînement

### Community 33 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), B-enfr / classifieur seul | demo_cases (6), B-enfr / classifieur seul | dev_fr_synthetique (14), B-enfr / D (chaîne complète) | demo_cases (3), B-enfr / D (chaîne complète) | dev_fr_synthetique (10) (+2 more)

### Community 34 - "common.py"
Cohesion: 0.31
Nodes (3): client(), get_json(), _fetch()

### Community 38 - "Étape 11 : essais à Oran (protocole et compte rendu)"
Cohesion: 0.18
Nodes (10): 1. Ce que les essais doivent mesurer, 2. Avant les essais, 3. Déroulé, 4. Fiches de relevé, 5. Questionnaire (1 à 5, de « pas du tout » à « tout à fait »), 6. Modèle de compte rendu, A. Mécaniciens : constituer le jeu de test (le plus important), B. Magasins (environ 15 min chacun, sur leur propre téléphone) (+2 more)

### Community 40 - "classifier.py"
Cohesion: 0.13
Nodes (7): build_pipeline(), FaultClassifier, load_classifier(), OnnxEncoderClassifier, train_baseline(), test_chaine_avec_classifieur_de_pieces(), test_chargement_avec_cible()

### Community 43 - "test_llm_chaine.py"
Cohesion: 0.21
Nodes (14): Fake, fake(), install(), _run(), test_cache_expire(), test_cache_une_question_identique_ne_coute_qu_un_appel(), test_le_classifieur_seul_n_appelle_pas_le_modele(), test_mode_differe_le_modele_en_panne_ne_laisse_pas_pending() (+6 more)

### Community 44 - "test_models.py"
Cohesion: 0.16
Nodes (6): upgrade(), upgrade(), _maps(), test_carnets_kaggle_a_jour_et_valides(), test_jeu_d_affinage(), test_pieces_vers_pannes()

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

### Community 50 - "hybrid"
Cohesion: 0.21
Nodes (5): FakeEmbedder, FakeReranker, hybrid(), encode_query(), _vec()

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
Cohesion: 0.11
Nodes (21): Brand, login(), cat_id(), test_admin_saisie_terrain_apparait_sur_la_carte(), test_contact_et_retour_modifient_le_score(), test_demande_diffusee(), test_diagnostic_et_session(), test_import_excel_500_lignes() (+13 more)

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

### Community 66 - "models.py"
Cohesion: 0.18
Nodes (4): Embedding, PartReference, utcnow(), test_references_jamais_generees()

### Community 68 - "magasins/[id]/page.tsx"
Cohesion: 0.14
Nodes (13): Family, Named, Product, Shop, ShopMap, MapShop, ORAN, ShopMap() (+5 more)

### Community 69 - "run.py"
Cohesion: 0.16
Nodes (15): read_jsonl(), write_jsonl(), export_training(), load_source(), summary(), cmd_collect(), cmd_load(), cmd_report() (+7 more)

### Community 73 - "layout.tsx"
Cohesion: 0.29
Nodes (6): body, display, metadata, RootLayout(), viewport, TopBar()

### Community 74 - "pipeline.py"
Cohesion: 0.12
Nodes (17): search_categories(), _ar_word(), _french_like_hits(), _norm_ar(), _replace_phrases(), to_french(), extract_dtc(), normalize() (+9 more)

### Community 75 - "Étape 9 : vérification sur un vrai téléphone"
Cohesion: 0.40
Nodes (4): Parcours à suivre (cocher), Préparer, Résultat, Étape 9 : vérification sur un vrai téléphone

### Community 76 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1533 hybride-int8-10x256

### Community 77 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.40
Nodes (4): A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (2), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261117-1542 hybride-int8-10x256-vecteurs-repares

### Community 86 - "kaggle_run.py"
Cohesion: 0.27
Nodes (10): cmd_adapter(), cmd_dataset(), cmd_output(), cmd_push(), cmd_status(), _force_remove(), kaggle(), main() (+2 more)

### Community 87 - "json"
Cohesion: 0.23
Nodes (7): get_classifier(), load_examples(), dump(), build(), explanation(), french_examples(), export()

### Community 88 - "conftest.py"
Cohesion: 0.19
Nodes (4): admin_headers(), client(), db(), _db()

### Community 89 - "train_baseline.py"
Cohesion: 0.26
Nodes (6): fiche_examples(), corpus_examples(), evaluate(), fault_to_part(), main(), relabel()

### Community 90 - "stackexchange.py"
Cohesion: 0.23
Nodes (7): collect(), _extract(), _rows(), strip_html(), fault_for(), primary_part_to_fault(), test_panne_type_seulement_si_sans_ambiguite()

### Community 91 - "argparse"
Cohesion: 0.27
Nodes (7): _as_list(), _first(), iter_records(), main(), make_translator(), fetch(), main()

### Community 92 - "test_espace_magasin.py"
Cohesion: 0.21
Nodes (5): new_otp(), _owner(), test_catalogue_d_une_fiche_non_validee_cache_au_public(), test_code_fixe_des_tests_seulement_avec_les_sms_de_console(), test_les_exemples_du_modele_s_importent_sans_erreur()

### Community 93 - "Plan : référentiel complet des véhicules d'Algérie et nouveaux jeux de données pour le diagnostic"
Cohesion: 0.17
Nodes (11): 0. Objectifs et critères de fin, 1. Phase A : référentiel des véhicules, 2. Phase B : collecte des nouvelles données, 4. Phase D : documentation et clôture, 5. Ordre et volume estimé, 6. Sources consultées pour ce plan, A1. Modèles à ajouter, A2. Méthode (rejouable, sans rien inventer) (+3 more)

### Community 94 - "evaluate.py"
Cohesion: 0.27
Nodes (5): test_banc_evaluation(), load_cases(), main(), ranked_parts(), run()

### Community 95 - "sources/__init__.py"
Cohesion: 0.18
Nodes (6): 1. Vérifier avant d'écrire du code, 2. Déclarer la source, 5. Tester, charger, mesurer, Ajouter une source de données à DALIL, Ce qu'il ne faut pas faire, SourceSpec

### Community 97 - "Le marché automobile algérien : ce qu'il implique pour DALIL"
Cohesion: 0.25
Nodes (7): 1. Le parc : vieux, français, et de plus en plus diesel à la revente, 2. Oran, 3. Ce qui se vend aujourd'hui (2023-2026), 4. Écarts avec le référentiel actuel de DALIL (`data/seed/vehicles.json`), 5. Recommandations pour le site, Le marché automobile algérien : ce qu'il implique pour DALIL, Sources

### Community 98 - "Modèles (étape 7)"
Cohesion: 0.29
Nodes (7): Ce que le banc a déjà appris (matière pour le mémoire), Données d'entraînement, Mesurer, Modèles (étape 7), Premiers résultats (14/11/2026, jeux synthétiques, sans modèle de langage), Qualité des réponses sur des textes écrits comme à Oran (18/11/2026), Variante D : modèle de langage affiné par LoRA (15/11/2026)

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

### Community 105 - "KnowledgeChunk"
Cohesion: 0.33
Nodes (3): KnowledgeChunk, test_rechargement_des_referentiels_garde_les_identifiants(), test_vecteurs_des_fiches_manquants_recalcules()

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
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `score_shop()` connect `test_recommendation.py` to `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)`?**
  _High betweenness centrality (0.216) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `User` (e.g. with `admin_import()` and `admin_merge()`) actually correct?**
  _`User` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12681159420289856 - nodes in this community are weakly interconnected._
- **Why does `Carte du code` connect `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` to `test_recommendation.py`?**
  _High betweenness centrality (0.194) - this node is a cross-community bridge._
- **Should `run_diagnosis` be split into smaller, more focused modules?**
  _Cohesion score 0.13118279569892474 - nodes in this community are weakly interconnected._
- **Should `User` be split into smaller, more focused modules?**
  _Cohesion score 0.10099573257467995 - nodes in this community are weakly interconnected._
- **Should `environment` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._