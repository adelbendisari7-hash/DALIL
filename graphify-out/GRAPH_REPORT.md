# Graph Report - DALIL  (2026-11-17)

## Corpus Check
- 155 files · ~105,191 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 26 file(s) not represented in the graph (top: (none) 6, .ipynb 6, .csv 3)

## Summary
- 1265 nodes · 3029 edges · 78 communities (65 shown, 13 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 267 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `de266e3d`
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
- stackexchange.py
- Ajouter une source de données à DALIL
- train_baseline.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- evaluate.py
- next.config.mjs
- sw.js
- report.md
- main.py
- classifier.py
- test_llm_chaine.py
- models.py
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
- hybrid
- seed.py
- load_vectors.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Étape 8 : chaîne de diagnostic, plan proposé (à valider avant de coder)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Embedding
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
1. `get_settings()` - 54 edges
2. `t()` - 45 edges
3. `run_diagnosis()` - 42 edges
4. `User` - 38 edges
5. `Shop` - 38 edges
6. `api()` - 35 edges
7. `Base` - 31 edges
8. `PartCategory` - 29 edges
9. `VehicleVariant` - 23 edges
10. `Product` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Carte du code` --references--> `score_shop()`  [INFERRED]
  CLAUDE.md → backend/app/services/recommendation.py
- `Conventions` --references--> `t()`  [INFERRED]
  CLAUDE.md → frontend/lib/i18n.ts
- `Étape 8 : recherche hybride et chaîne complète (16/11/2026)` --references--> `warmup()`  [INFERRED]
  ml/README.md → backend/app/main.py
- `Modèles (étape 7)` --references--> `OnnxEncoderClassifier`  [INFERRED]
  ml/README.md → backend/app/services/diagnosis/classifier.py
- `1. Ce qui existe déjà (étapes 3 à 7)` --references--> `_CallBudget`  [INFERRED]
  docs/plan-etape-8.md → backend/app/services/diagnosis/llm.py

## Import Cycles
- None detected.

## Communities (78 total, 13 thin omitted)

### Community 0 - "llm.py"
Cohesion: 0.14
Nodes (8): AnthropicProvider, _CallBudget, get_llm(), LLMProvider, OpenAICompatProvider, _parse_json(), rerank_with_llm(), _ResponseCache

### Community 1 - "pipeline.py"
Cohesion: 0.21
Nodes (12): DtcCode, Fault, detect_lang(), extract_dtc(), _normalized(), _part_view(), parts_to_faults(), _pick_questions() (+4 more)

### Community 2 - "test_api.py"
Cohesion: 0.06
Nodes (28): admin_headers(), client(), db(), _db(), login(), cat_id(), test_admin_saisie_terrain_apparait_sur_la_carte(), test_contact_et_retour_modifient_le_score() (+20 more)

### Community 3 - "security.py"
Cohesion: 0.09
Nodes (17): get_db(), OtpCode, me(), me_delete(), me_patch(), otp_request(), otp_verify(), _user_out() (+9 more)

### Community 4 - "environment"
Cohesion: 0.05
Nodes (39): build, depends_on, environment, ports, volumes, NEXT_PUBLIC_API_URL, args, context (+31 more)

### Community 5 - "public.py"
Cohesion: 0.19
Nodes (17): DiagnosisSession, VehicleVariant, brands(), categories(), communes(), _defer(), diagnosis(), diagnosis_answers() (+9 more)

### Community 6 - "package.json"
Cohesion: 0.07
Nodes (27): FakeRecognition, react-dom@^19.3.1, devDependencies, @playwright/test@^1.65.1, @types/leaflet@^1.9.22, @types/node@^26.6.6, @types/react@^19.3.0, @types/react-dom@^19.3.0 (+19 more)

### Community 7 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.07
Nodes (27): Carte du code, Commandes, Conventions, DALIL — consignes pour Claude Code, 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes (+19 more)

### Community 8 - "models.py"
Cohesion: 0.11
Nodes (25): Base, AdminAction, Brand, Commune, ContactEvent, Feedback, PartReference, PartRequest (+17 more)

### Community 9 - "t"
Cohesion: 0.14
Nodes (10): Family, Hit, RefHit, Brand, Model, Variant, YEARS, Vehicle (+2 more)

### Community 10 - "taxonomy_map.py"
Cohesion: 0.20
Nodes (15): 4. Relier à la taxonomie, collect(), categories_en(), categories_fr(), family_fr(), family_of(), _match(), _norm() (+7 more)

### Community 11 - "test_recommendation.py"
Cohesion: 0.10
Nodes (31): category_lineage(), freshness(), haversine_km(), proximity(), rank(), recommend(), reliability(), score_shop() (+23 more)

### Community 12 - "mot.py"
Cohesion: 0.19
Nodes (12): 3. Écrire le module de collecte, download(), Record, collectors(), collect(), Context, aggregate(), _band() (+4 more)

### Community 13 - "api"
Cohesion: 0.16
Nodes (16): Login(), send(), LoginPage(), Rec, ShopMap, Shops(), broadcast(), ShopsPage() (+8 more)

### Community 14 - "translate.py"
Cohesion: 0.16
Nodes (10): test_decoupage_en_phrases(), test_postedition_impose_le_lexique(), test_texte_en_capitales_remis_en_casse_normale(), postedit(), prepare(), split_sentences(), _translate_cvffad(), translate_file() (+2 more)

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
Cohesion: 0.17
Nodes (6): get_settings(), Settings, get_embedder(), get_reranker(), _load(), Reranker

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
Cohesion: 0.15
Nodes (30): PartCategory, RequestResponse, Shop, User, contact_event(), feedback(), _mark_observed(), _owned_shop() (+22 more)

### Community 23 - "test_pipeline.py"
Cohesion: 0.19
Nodes (12): read_jsonl(), write_jsonl(), chunk_rows(), export_training(), LicenseError, load_source(), _rec(), test_chargement_refuse_sans_licence() (+4 more)

### Community 24 - "SOURCES.md"
Cohesion: 0.13
Nodes (8): Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`), Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`), Fiche source : NHTSA, plaintes des propriétaires (`nhtsa_complaints`), Fiche source : NHTSA, campagnes de rappel (`nhtsa_recalls`), Fiche source : RappelConso, rappels automobiles (`rappelconso`), Registre des sources de données, Sources exclues, Fiche source : Stack Exchange, Motor Vehicle Maintenance & Repair (`stackexchange_mechanics`)

### Community 25 - "ZipMemberStream"
Cohesion: 0.20
Nodes (3): ZipMemberStream, test_lecture_en_flux_d_un_zip(), test_reprise_apres_coupure_reseau()

### Community 26 - "imports.py"
Cohesion: 0.15
Nodes (14): Model, ProductFitment, resolve_category(), resolve_variants(), search_categories(), normalize(), strip_accents(), text_is_dangerous() (+6 more)

### Community 27 - "common.py"
Cohesion: 0.22
Nodes (9): client(), get_json(), sha1(), collect_complaints(), collect_recalls(), _fetch(), _vehicle(), nhtsa_family() (+1 more)

### Community 28 - "diagnostic/[id]/page.tsx"
Cohesion: 0.22
Nodes (10): Cause, DiagnosticResult(), answer(), rate(), Part, PartLabel(), Question, Ref (+2 more)

### Community 29 - "t"
Cohesion: 0.21
Nodes (11): Admin(), act(), upload(), pct(), Home(), submit(), PartsPage(), VehiclePicker() (+3 more)

### Community 30 - "stackexchange.py"
Cohesion: 0.23
Nodes (7): collect(), _extract(), _rows(), strip_html(), fault_for(), primary_part_to_fault(), test_panne_type_seulement_si_sans_ambiguite()

### Community 31 - "Ajouter une source de données à DALIL"
Cohesion: 0.20
Nodes (6): 1. Vérifier avant d'écrire du code, 2. Déclarer la source, 5. Tester, charger, mesurer, Ajouter une source de données à DALIL, Ce qu'il ne faut pas faire, SourceSpec

### Community 32 - "train_baseline.py"
Cohesion: 0.26
Nodes (6): fiche_examples(), corpus_examples(), evaluate(), fault_to_part(), main(), relabel()

### Community 33 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), B-enfr / classifieur seul | demo_cases (6), B-enfr / classifieur seul | dev_fr_synthetique (14), B-enfr / D (chaîne complète) | demo_cases (3), B-enfr / D (chaîne complète) | dev_fr_synthetique (10) (+2 more)

### Community 34 - "evaluate.py"
Cohesion: 0.22
Nodes (7): test_banc_evaluation(), fetch(), main(), load_cases(), main(), ranked_parts(), run()

### Community 39 - "main.py"
Cohesion: 0.14
Nodes (6): health(), start_warmup(), warmup(), _diagnose(), test_diagnostics_simultanes_pendant_la_reconstruction_des_index(), test_prechargement_sans_erreur()

### Community 40 - "classifier.py"
Cohesion: 0.11
Nodes (13): build_pipeline(), FaultClassifier, get_classifier(), load_classifier(), load_examples(), OnnxEncoderClassifier, train_baseline(), _maps() (+5 more)

### Community 43 - "test_llm_chaine.py"
Cohesion: 0.17
Nodes (16): _variant(), Fake, fake(), install(), _run(), test_cache_expire(), test_cache_une_question_identique_ne_coute_qu_un_appel(), test_cas_de_demonstration_en_mode_complet_avec_modele() (+8 more)

### Community 45 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.22
Nodes (8): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), C (recherche + LM) | demo_cases (4), C (recherche + LM) | dev_fr_synthetique (13), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261114-1722 couverture

### Community 46 - "json"
Cohesion: 0.13
Nodes (13): build_user_message(), dump(), _as_list(), _first(), iter_records(), main(), make_translator(), build() (+5 more)

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
Nodes (14): KnowledgeChunk, DiagnosisInput, get_index(), test_demo_case(), _diag(), test_diagnostic_en_mode_hybride(), test_garde_fou_vectoriel_absent_en_mode_mots_cles(), test_garde_fou_vectoriel_du_domaine() (+6 more)

### Community 51 - "DenseIndex"
Cohesion: 0.07
Nodes (17): DenseIndex, Hit, HybridIndex, KeywordIndex, Faire tourner les modèles sur le portable, Mesurer (portable), Mettre un modèle en service, Ordre conseillé (+9 more)

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

### Community 58 - "hybrid"
Cohesion: 0.21
Nodes (5): FakeEmbedder, FakeReranker, hybrid(), encode_query(), _vec()

### Community 59 - "seed.py"
Cohesion: 0.29
Nodes (13): DtcPart, FaultPart, Wilaya, _load(), main(), purge_demo(), run(), seed_categories() (+5 more)

### Community 60 - "load_vectors.py"
Cohesion: 0.25
Nodes (6): Embedder, check_ids(), check_queries(), fill_db(), install(), main()

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
Cohesion: 0.40
Nodes (8): summary(), cmd_collect(), cmd_load(), cmd_report(), cmd_translate(), main(), path_for(), review_sample()

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
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `score_shop()` connect `test_recommendation.py` to `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)`?**
  _High betweenness centrality (0.217) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `run_diagnosis()` (e.g. with `DtcCode` and `DtcPart`) actually correct?**
  _`run_diagnosis()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13852813852813853 - nodes in this community are weakly interconnected._
- **Why does `Carte du code` connect `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` to `test_recommendation.py`?**
  _High betweenness centrality (0.211) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `User` (e.g. with `admin_import()` and `admin_merge()`) actually correct?**
  _`User` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.061367621274108705 - nodes in this community are weakly interconnected._
- **Should `security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09230769230769231 - nodes in this community are weakly interconnected._