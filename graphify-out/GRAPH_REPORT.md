# Graph Report - DALIL  (2026-11-17)

## Corpus Check
- 157 files · ~106,386 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 26 file(s) not represented in the graph (top: (none) 6, .ipynb 6, .csv 3)

## Summary
- 1286 nodes · 3079 edges · 76 communities (65 shown, 11 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 270 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6d720100`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- llm.py
- pipeline.py
- test_api.py
- security.py
- environment
- public.py
- package.json
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- models.py
- t
- taxonomy_map.py
- test_recommendation.py
- mot.py
- api
- translate.py
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
- imports.py
- common.py
- diagnostic/[id]/page.tsx
- t
- Shop
- Ajouter une source de données à DALIL
- main.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- build_llm_dataset.py
- next.config.mjs
- sw.js
- report.md
- test_espace_magasin.py
- run_diagnosis
- test_models.py
- test_llm_chaine.py
- db.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- json
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
- seed.py
- kaggle_run.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Étape 8 : chaîne de diagnostic, plan proposé (à valider avant de coder)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- eval_with_llm.sh
- magasins/[id]/page.tsx
- run.py
- schemas.py
- layout.tsx
- RateLimiter
- Étape 9 : vérification sur un vrai téléphone
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 57 edges
2. `t()` - 45 edges
3. `run_diagnosis()` - 42 edges
4. `User` - 39 edges
5. `Shop` - 39 edges
6. `api()` - 35 edges
7. `Base` - 31 edges
8. `PartCategory` - 31 edges
9. `VehicleVariant` - 23 edges
10. `Product` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Carte du code` --references--> `score_shop()`  [INFERRED]
  CLAUDE.md → backend/app/services/recommendation.py
- `Conventions` --references--> `t()`  [INFERRED]
  CLAUDE.md → frontend/lib/i18n.ts
- `Étape 8 : recherche hybride et chaîne complète (16/11/2026)` --references--> `warmup()`  [INFERRED]
  ml/README.md → backend/app/main.py
- `1. Ce qui existe déjà (étapes 3 à 7)` --references--> `_CallBudget`  [INFERRED]
  docs/plan-etape-8.md → backend/app/services/diagnosis/llm.py
- `1. Ce qui existe déjà (étapes 3 à 7)` --references--> `rerank_with_llm()`  [INFERRED]
  docs/plan-etape-8.md → backend/app/services/diagnosis/llm.py

## Import Cycles
- None detected.

## Communities (76 total, 11 thin omitted)

### Community 0 - "llm.py"
Cohesion: 0.13
Nodes (9): AnthropicProvider, build_user_message(), _CallBudget, get_llm(), LLMProvider, OpenAICompatProvider, _parse_json(), rerank_with_llm() (+1 more)

### Community 1 - "pipeline.py"
Cohesion: 0.15
Nodes (12): detect_lang(), extract_dtc(), normalize(), strip_accents(), _normalized(), _part_view(), parts_to_faults(), _pick_questions() (+4 more)

### Community 2 - "test_api.py"
Cohesion: 0.11
Nodes (16): Brand, login(), cat_id(), test_admin_saisie_terrain_apparait_sur_la_carte(), test_contact_et_retour_modifient_le_score(), test_demande_diffusee(), test_diagnostic_et_session(), test_import_excel_500_lignes() (+8 more)

### Community 3 - "security.py"
Cohesion: 0.09
Nodes (20): get_db(), OtpCode, User, me(), me_delete(), me_patch(), otp_request(), otp_verify() (+12 more)

### Community 4 - "environment"
Cohesion: 0.05
Nodes (39): build, depends_on, environment, ports, volumes, NEXT_PUBLIC_API_URL, args, context (+31 more)

### Community 5 - "public.py"
Cohesion: 0.26
Nodes (13): DtcCode, DtcPart, VehicleVariant, brands(), categories(), communes(), diagnosis_get(), dtc() (+5 more)

### Community 6 - "package.json"
Cohesion: 0.06
Nodes (31): ADMIN_PHONE, makeCatalog(), OTP, PY_PATH, VENV, FakeRecognition, react-dom@^19.3.1, devDependencies (+23 more)

### Community 7 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.07
Nodes (27): Carte du code, Commandes, Conventions, DALIL — consignes pour Claude Code, 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes (+19 more)

### Community 8 - "models.py"
Cohesion: 0.17
Nodes (13): Base, AdminAction, ContactEvent, DiagnosisSession, Embedding, Feedback, PartRequest, Product (+5 more)

### Community 9 - "t"
Cohesion: 0.14
Nodes (10): Family, Hit, RefHit, Brand, Model, Variant, YEARS, Vehicle (+2 more)

### Community 10 - "taxonomy_map.py"
Cohesion: 0.16
Nodes (17): 4. Relier à la taxonomie, collect(), collect(), _extract(), _rows(), strip_html(), categories_en(), categories_fr() (+9 more)

### Community 11 - "test_recommendation.py"
Cohesion: 0.11
Nodes (31): category_lineage(), freshness(), haversine_km(), proximity(), rank(), recommend(), reliability(), score_shop() (+23 more)

### Community 12 - "mot.py"
Cohesion: 0.18
Nodes (10): download(), collect(), Context, aggregate(), _band(), collect(), _n(), _pct() (+2 more)

### Community 13 - "api"
Cohesion: 0.16
Nodes (16): Login(), send(), LoginPage(), Rec, ShopMap, Shops(), broadcast(), ShopsPage() (+8 more)

### Community 14 - "translate.py"
Cohesion: 0.17
Nodes (9): read_jsonl(), sha1(), cmd_translate(), prepare(), review_sample(), _translate_cvffad(), translate_file(), Translator (+1 more)

### Community 15 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.09
Nodes (22): A-amorcage / classifieur seul | demo_cases (0), A-amorcage / classifieur seul | dev_fr_synthetique (4), A-amorcage / D (chaîne complète) | demo_cases (0), A-amorcage / D (chaîne complète) | dev_fr_synthetique (3), A-corpus-panne / classifieur seul | demo_cases (1), A-corpus-panne / classifieur seul | dev_fr_synthetique (4), A-corpus-panne / D (chaîne complète) | demo_cases (1), A-corpus-panne / D (chaîne complète) | dev_fr_synthetique (3) (+14 more)

### Community 16 - "api.ts"
Cohesion: 0.21
Nodes (11): Metrics, Shop, Tab, addProduct(), API, ApiError, session, store (+3 more)

### Community 17 - "steps"
Cohesion: 0.12
Nodes (20): runs-on, steps, DALIL_DATABASE_URL, runs-on, steps, jobs, backend, frontend (+12 more)

### Community 18 - "retrieval.py"
Cohesion: 0.10
Nodes (5): Settings, get_embedder(), get_reranker(), _load(), Reranker

### Community 19 - "espace-magasin/page.tsx"
Cohesion: 0.13
Nodes (24): FieldForm(), submit(), Claimable, errMsg(), Family, Inbox, Product, Shop (+16 more)

### Community 20 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 21 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.11
Nodes (17): 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes, 14. Protection du projet et statut de startup, 15. Sources, 1. Vision et périmètre, 2. Acteurs et parcours (+9 more)

### Community 22 - "shops.py"
Cohesion: 0.14
Nodes (20): RequestResponse, catalog_template(), contact_event(), feedback(), _mark_observed(), _owned_shop(), part_request_create(), part_request_inbox() (+12 more)

### Community 23 - "test_pipeline.py"
Cohesion: 0.12
Nodes (18): chunk_rows(), LicenseError, _rec(), test_chaque_source_a_sa_fiche_et_sa_licence(), test_chargement_refuse_sans_licence(), test_correspondance_anglais(), test_decoupage_en_phrases(), test_export_entrainement_exclut_stats_rappels_et_procedures() (+10 more)

### Community 24 - "SOURCES.md"
Cohesion: 0.13
Nodes (8): Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`), Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`), Fiche source : NHTSA, plaintes des propriétaires (`nhtsa_complaints`), Fiche source : NHTSA, campagnes de rappel (`nhtsa_recalls`), Fiche source : RappelConso, rappels automobiles (`rappelconso`), Registre des sources de données, Sources exclues, Fiche source : Stack Exchange, Motor Vehicle Maintenance & Repair (`stackexchange_mechanics`)

### Community 25 - "ZipMemberStream"
Cohesion: 0.20
Nodes (3): ZipMemberStream, test_lecture_en_flux_d_un_zip(), test_reprise_apres_coupure_reseau()

### Community 26 - "imports.py"
Cohesion: 0.17
Nodes (12): PartCategory, ProductFitment, admin_refs_import(), resolve_category(), resolve_variants(), search_categories(), _float(), import_products() (+4 more)

### Community 27 - "common.py"
Cohesion: 0.26
Nodes (8): client(), get_json(), Record, collect_complaints(), collect_recalls(), _fetch(), _vehicle(), nhtsa_family()

### Community 28 - "diagnostic/[id]/page.tsx"
Cohesion: 0.22
Nodes (10): Cause, DiagnosticResult(), answer(), rate(), Part, PartLabel(), Question, Ref (+2 more)

### Community 29 - "t"
Cohesion: 0.21
Nodes (11): Admin(), act(), upload(), pct(), Home(), submit(), PartsPage(), VehiclePicker() (+3 more)

### Community 30 - "Shop"
Cohesion: 0.16
Nodes (17): Shop, admin_actions(), admin_import(), admin_reject(), admin_shop_create(), admin_shops(), admin_stale(), admin_verify() (+9 more)

### Community 31 - "Ajouter une source de données à DALIL"
Cohesion: 0.25
Nodes (7): 1. Vérifier avant d'écrire du code, 2. Déclarer la source, 3. Écrire le module de collecte, 5. Tester, charger, mesurer, Ajouter une source de données à DALIL, Ce qu'il ne faut pas faire, SourceSpec

### Community 33 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), B-enfr / classifieur seul | demo_cases (6), B-enfr / classifieur seul | dev_fr_synthetique (14), B-enfr / D (chaîne complète) | demo_cases (3), B-enfr / D (chaîne complète) | dev_fr_synthetique (10) (+2 more)

### Community 34 - "build_llm_dataset.py"
Cohesion: 0.33
Nodes (5): get_classifier(), load_examples(), build(), explanation(), french_examples()

### Community 38 - "test_espace_magasin.py"
Cohesion: 0.32
Nodes (3): _owner(), test_catalogue_d_une_fiche_non_validee_cache_au_public(), test_les_exemples_du_modele_s_importent_sans_erreur()

### Community 39 - "run_diagnosis"
Cohesion: 0.13
Nodes (14): warmup(), _defer(), diagnosis(), diagnosis_answers(), _refine(), _save(), DiagnosisInput, run_diagnosis() (+6 more)

### Community 40 - "test_models.py"
Cohesion: 0.06
Nodes (30): build_pipeline(), FaultClassifier, fiche_examples(), load_classifier(), OnnxEncoderClassifier, train_baseline(), _maps(), test_carnets_kaggle_a_jour_et_valides() (+22 more)

### Community 43 - "test_llm_chaine.py"
Cohesion: 0.17
Nodes (15): Fake, fake(), install(), _run(), test_cache_expire(), test_cache_une_question_identique_ne_coute_qu_un_appel(), test_cas_de_demonstration_en_mode_complet_avec_modele(), test_le_classifieur_seul_n_appelle_pas_le_modele() (+7 more)

### Community 44 - "db.py"
Cohesion: 0.13
Nodes (6): upgrade(), make_engine(), admin_headers(), client(), db(), _db()

### Community 45 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.22
Nodes (8): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), C (recherche + LM) | demo_cases (4), C (recherche + LM) | dev_fr_synthetique (13), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261114-1722 couverture

### Community 46 - "json"
Cohesion: 0.11
Nodes (16): test_banc_evaluation(), dump(), _as_list(), _first(), iter_records(), main(), make_translator(), fetch() (+8 more)

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
Cohesion: 0.13
Nodes (4): DenseIndex, Hit, HybridIndex, KeywordIndex

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

### Community 59 - "seed.py"
Cohesion: 0.23
Nodes (18): Commune, Fault, FaultPart, Model, PartReference, Wilaya, _load(), main() (+10 more)

### Community 60 - "kaggle_run.py"
Cohesion: 0.13
Nodes (16): Embedder, cmd_adapter(), cmd_dataset(), cmd_output(), cmd_push(), cmd_status(), _force_remove(), kaggle() (+8 more)

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
Nodes (14): Family, Named, Product, Shop, ShopMap, ShopPage(), MapShop, ORAN (+6 more)

### Community 69 - "run.py"
Cohesion: 0.26
Nodes (10): write_jsonl(), export_training(), load_source(), summary(), cmd_collect(), cmd_load(), cmd_report(), collectors() (+2 more)

### Community 70 - "schemas.py"
Cohesion: 0.18
Nodes (12): AnswersRequest, ContactEventIn, DiagnosisRequest, FeedbackIn, _iso(), MePatch, OtpRequest, OtpVerify (+4 more)

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
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `score_shop()` connect `test_recommendation.py` to `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)`?**
  _High betweenness centrality (0.216) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `run_diagnosis()` (e.g. with `DtcCode` and `DtcPart`) actually correct?**
  _`run_diagnosis()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._
- **Why does `Carte du code` connect `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` to `test_recommendation.py`?**
  _High betweenness centrality (0.211) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `User` (e.g. with `admin_import()` and `admin_merge()`) actually correct?**
  _`User` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Should `pipeline.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14624505928853754 - nodes in this community are weakly interconnected._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11494252873563218 - nodes in this community are weakly interconnected._