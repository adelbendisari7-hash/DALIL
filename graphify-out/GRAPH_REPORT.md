# Graph Report - DALIL  (2026-11-15)

## Corpus Check
- 134 files · ~92,437 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 29 file(s) not represented in the graph (top: (none) 6, .ipynb 5, .jsonl 4)

## Summary
- 1082 nodes · 2620 edges · 60 communities (51 shown, 9 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 230 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- models.py
- pipeline.py
- test_api.py
- security.py
- environment
- public.py
- package.json
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- shops.py
- t
- taxonomy_map.py
- test_recommendation.py
- mot.py
- react
- run.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- api.ts
- steps
- kaggle_run.py
- espace-magasin/page.tsx
- compilerOptions
- DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)
- api
- test_pipeline.py
- SOURCES.md
- ZipMemberStream
- json
- common.py
- diagnostic/[id]/page.tsx
- admin/page.tsx
- stackexchange.py
- Ajouter une source de données à DALIL
- train_baseline.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- evaluate.py
- next.config.mjs
- sw.js
- report.md
- Étape 7 sur Kaggle : traduction et entraînement
- classifier.py
- test_models.py
- models.py
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- json
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- conftest.py
- KeywordIndex
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Jeux de test
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)
- test_demo_cases.py

## God Nodes (most connected - your core abstractions)
1. `t()` - 45 edges
2. `User` - 38 edges
3. `Shop` - 38 edges
4. `api()` - 35 edges
5. `get_settings()` - 31 edges
6. `Base` - 31 edges
7. `PartCategory` - 27 edges
8. `run_diagnosis()` - 22 edges
9. `VehicleVariant` - 22 edges
10. `Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Carte du code` --references--> `score_shop()`  [INFERRED]
  CLAUDE.md → backend/app/services/recommendation.py
- `Conventions` --references--> `t()`  [INFERRED]
  CLAUDE.md → frontend/lib/i18n.ts
- `Modèles (étape 7)` --references--> `OnnxEncoderClassifier`  [INFERRED]
  ml/README.md → backend/app/services/diagnosis/classifier.py
- `3. Écrire le module de collecte` --references--> `collectors()`  [INFERRED]
  .claude/skills/ajouter-source-donnees/SKILL.md → data/pipeline/run.py
- `3. Écrire le module de collecte` --references--> `Record`  [INFERRED]
  .claude/skills/ajouter-source-donnees/SKILL.md → data/pipeline/common.py

## Import Cycles
- None detected.

## Communities (60 total, 9 thin omitted)

### Community 0 - "models.py"
Cohesion: 0.20
Nodes (21): Base, Commune, DtcCode, DtcPart, Fault, FaultPart, KnowledgeChunk, PartReference (+13 more)

### Community 1 - "pipeline.py"
Cohesion: 0.07
Nodes (29): resolve_variants(), search_categories(), get_classifier(), AnthropicProvider, build_user_message(), _CallBudget, get_llm(), LLMProvider (+21 more)

### Community 2 - "test_api.py"
Cohesion: 0.11
Nodes (17): Brand, Model, login(), cat_id(), test_admin_saisie_terrain_apparait_sur_la_carte(), test_contact_et_retour_modifient_le_score(), test_demande_diffusee(), test_diagnostic_et_session() (+9 more)

### Community 3 - "security.py"
Cohesion: 0.06
Nodes (21): get_settings(), Settings, get_db(), health(), OtpCode, me(), me_delete(), me_patch() (+13 more)

### Community 4 - "environment"
Cohesion: 0.05
Nodes (39): build, depends_on, environment, ports, volumes, NEXT_PUBLIC_API_URL, args, context (+31 more)

### Community 5 - "public.py"
Cohesion: 0.25
Nodes (15): DiagnosisSession, VehicleVariant, brands(), categories(), communes(), diagnosis(), diagnosis_answers(), diagnosis_get() (+7 more)

### Community 6 - "package.json"
Cohesion: 0.08
Nodes (30): ShopMap(), dependencies, leaflet@^1.9.4, next@^15.5.29, react@^19.3.1, react-dom@^19.3.1, devDependencies, @playwright/test@^1.65.1 (+22 more)

### Community 7 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.07
Nodes (27): Carte du code, Commandes, Conventions, DALIL — consignes pour Claude Code, 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes (+19 more)

### Community 8 - "shops.py"
Cohesion: 0.06
Nodes (68): ContactEvent, Feedback, PartCategory, PartRequest, Product, RequestResponse, Shop, ShopBrand (+60 more)

### Community 9 - "t"
Cohesion: 0.12
Nodes (17): Home(), submit(), Family, Hit, PartsPage(), RefHit, Brand, Model (+9 more)

### Community 10 - "taxonomy_map.py"
Cohesion: 0.21
Nodes (14): 4. Relier à la taxonomie, collect(), categories_en(), categories_fr(), family_fr(), _match(), _norm(), reconcile() (+6 more)

### Community 11 - "test_recommendation.py"
Cohesion: 0.19
Nodes (21): freshness(), haversine_km(), proximity(), rank(), reliability(), score_shop(), ScoredShop, ShopSignals (+13 more)

### Community 12 - "mot.py"
Cohesion: 0.21
Nodes (10): Record, collect(), Context, aggregate(), _band(), collect(), _n(), _pct() (+2 more)

### Community 13 - "react"
Cohesion: 0.13
Nodes (17): Family, Named, Product, Shop, ShopMap, ShopPage(), Rec, ShopMap (+9 more)

### Community 14 - "run.py"
Cohesion: 0.36
Nodes (8): load_source(), summary(), cmd_collect(), cmd_load(), cmd_report(), cmd_translate(), main(), path_for()

### Community 15 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.09
Nodes (22): A-amorcage / classifieur seul | demo_cases (0), A-amorcage / classifieur seul | dev_fr_synthetique (4), A-amorcage / D (chaîne complète) | demo_cases (0), A-amorcage / D (chaîne complète) | dev_fr_synthetique (3), A-corpus-panne / classifieur seul | demo_cases (1), A-corpus-panne / classifieur seul | dev_fr_synthetique (4), A-corpus-panne / D (chaîne complète) | demo_cases (1), A-corpus-panne / D (chaîne complète) | dev_fr_synthetique (3) (+14 more)

### Community 16 - "api.ts"
Cohesion: 0.14
Nodes (13): Login(), send(), LoginPage(), body, display, metadata, RootLayout(), viewport (+5 more)

### Community 17 - "steps"
Cohesion: 0.12
Nodes (20): runs-on, steps, DALIL_DATABASE_URL, runs-on, steps, jobs, backend, frontend (+12 more)

### Community 18 - "kaggle_run.py"
Cohesion: 0.25
Nodes (10): cmd_adapter(), cmd_dataset(), cmd_output(), cmd_push(), cmd_status(), _force_remove(), kaggle(), main() (+2 more)

### Community 19 - "espace-magasin/page.tsx"
Cohesion: 0.16
Nodes (15): FieldForm(), submit(), Claimable, Family, Inbox, Product, Shop, cleanShop() (+7 more)

### Community 20 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 21 - "DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)"
Cohesion: 0.11
Nodes (17): 10. Exigences non fonctionnelles, 11. Plan de réalisation pour Claude Code, 12. Idées complémentaires, 13. Risques et questions ouvertes, 14. Protection du projet et statut de startup, 15. Sources, 1. Vision et périmètre, 2. Acteurs et parcours (+9 more)

### Community 22 - "api"
Cohesion: 0.23
Nodes (16): errMsg(), ShopAdmin(), addProduct(), importFile(), respond(), saveProfile(), ShopSpace(), becomeOwner() (+8 more)

### Community 23 - "test_pipeline.py"
Cohesion: 0.09
Nodes (23): read_jsonl(), write_jsonl(), chunk_rows(), dump(), export_training(), LicenseError, _rec(), test_chargement_refuse_sans_licence() (+15 more)

### Community 24 - "SOURCES.md"
Cohesion: 0.13
Nodes (8): Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`), Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`), Fiche source : NHTSA, plaintes des propriétaires (`nhtsa_complaints`), Fiche source : NHTSA, campagnes de rappel (`nhtsa_recalls`), Fiche source : RappelConso, rappels automobiles (`rappelconso`), Registre des sources de données, Sources exclues, Fiche source : Stack Exchange, Motor Vehicle Maintenance & Repair (`stackexchange_mechanics`)

### Community 25 - "ZipMemberStream"
Cohesion: 0.20
Nodes (3): ZipMemberStream, test_lecture_en_flux_d_un_zip(), test_reprise_apres_coupure_reseau()

### Community 26 - "json"
Cohesion: 0.21
Nodes (6): load_examples(), build(), explanation(), french_examples(), main(), notebook()

### Community 27 - "common.py"
Cohesion: 0.21
Nodes (10): client(), get_json(), sha1(), collectors(), collect_complaints(), collect_recalls(), _fetch(), _vehicle() (+2 more)

### Community 28 - "diagnostic/[id]/page.tsx"
Cohesion: 0.22
Nodes (10): Cause, DiagnosticResult(), answer(), rate(), Part, PartLabel(), Question, Ref (+2 more)

### Community 29 - "admin/page.tsx"
Cohesion: 0.25
Nodes (8): Admin(), act(), upload(), Metrics, pct(), Shop, Tab, API

### Community 30 - "stackexchange.py"
Cohesion: 0.20
Nodes (8): download(), collect(), _extract(), _rows(), strip_html(), fault_for(), primary_part_to_fault(), test_panne_type_seulement_si_sans_ambiguite()

### Community 31 - "Ajouter une source de données à DALIL"
Cohesion: 0.17
Nodes (7): 1. Vérifier avant d'écrire du code, 2. Déclarer la source, 3. Écrire le module de collecte, 5. Tester, charger, mesurer, Ajouter une source de données à DALIL, Ce qu'il ne faut pas faire, SourceSpec

### Community 32 - "train_baseline.py"
Cohesion: 0.26
Nodes (6): fiche_examples(), corpus_examples(), evaluate(), fault_to_part(), main(), relabel()

### Community 33 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), B-enfr / classifieur seul | demo_cases (6), B-enfr / classifieur seul | dev_fr_synthetique (14), B-enfr / D (chaîne complète) | demo_cases (3), B-enfr / D (chaîne complète) | dev_fr_synthetique (10) (+2 more)

### Community 34 - "evaluate.py"
Cohesion: 0.31
Nodes (5): test_banc_evaluation(), load_cases(), main(), ranked_parts(), run()

### Community 39 - "Étape 7 sur Kaggle : traduction et entraînement"
Cohesion: 0.14
Nodes (12): Faire tourner les modèles sur le portable, Mesurer (portable), Mettre un modèle en service, Ordre conseillé, Préparer le jeu de données Kaggle « dalil-pipeline », Étape 7 sur Kaggle : traduction et entraînement, Ce que le banc a déjà appris (matière pour le mémoire), Données d'entraînement (+4 more)

### Community 40 - "classifier.py"
Cohesion: 0.12
Nodes (7): build_pipeline(), FaultClassifier, load_classifier(), OnnxEncoderClassifier, train_baseline(), test_chaine_avec_classifieur_de_pieces(), test_chargement_avec_cible()

### Community 43 - "test_models.py"
Cohesion: 0.25
Nodes (4): _maps(), test_carnets_kaggle_a_jour_et_valides(), test_jeu_d_affinage(), test_pieces_vers_pannes()

### Community 44 - "models.py"
Cohesion: 0.11
Nodes (5): upgrade(), make_engine(), AdminAction, Embedding, utcnow()

### Community 45 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.22
Nodes (8): A / classifieur seul | demo_cases (0), A / classifieur seul | dev_fr_synthetique (4), A / D (chaîne complète) | demo_cases (0), A / D (chaîne complète) | dev_fr_synthetique (3), C (recherche + LM) | demo_cases (4), C (recherche + LM) | dev_fr_synthetique (13), Erreurs (pièce attendue absente du top-3, ou hors sujet accepté), Résultats 20261114-1722 couverture

### Community 46 - "json"
Cohesion: 0.27
Nodes (7): _as_list(), _first(), iter_records(), main(), make_translator(), fetch(), main()

### Community 47 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.15
Nodes (12): A-panne / classifieur seul | demo_cases (0), A-panne / classifieur seul | dev_fr_synthetique (4), A-panne / D (chaîne complète) | demo_cases (0), A-panne / D (chaîne complète) | dev_fr_synthetique (3), A-piece / classifieur seul | demo_cases (0), A-piece / classifieur seul | dev_fr_synthetique (5), A-piece / D (chaîne complète) | demo_cases (0), A-piece / D (chaîne complète) | dev_fr_synthetique (3) (+4 more)

### Community 48 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A-panne / classifieur seul | demo_cases (0), A-panne / classifieur seul | dev_fr_synthetique (5), A-panne / D (chaîne complète) | demo_cases (0), A-panne / D (chaîne complète) | dev_fr_synthetique (5), A-piece / classifieur seul | demo_cases (0), A-piece / classifieur seul | dev_fr_synthetique (6), A-piece / D (chaîne complète) | demo_cases (0), A-piece / D (chaîne complète) | dev_fr_synthetique (5) (+2 more)

### Community 49 - "Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)"
Cohesion: 0.18
Nodes (10): A-panne / classifieur seul | demo_cases (0), A-panne / classifieur seul | dev_fr_synthetique (4), A-piece / classifieur seul | demo_cases (0), A-piece / classifieur seul | dev_fr_synthetique (5), A-piece / D (chaîne complète) | demo_cases (0), A-piece / D (chaîne complète) | dev_fr_synthetique (3), C (recherche + LM) | demo_cases (1), C (recherche + LM) | dev_fr_synthetique (7) (+2 more)

### Community 50 - "conftest.py"
Cohesion: 0.36
Nodes (4): admin_headers(), client(), db(), _db()

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

### Community 58 - "test_demo_cases.py"
Cohesion: 0.47
Nodes (3): _variant(), DiagnosisInput, test_demo_case()

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `score_shop()` connect `test_recommendation.py` to `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)`?**
  _High betweenness centrality (0.221) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `User` (e.g. with `admin_import()` and `admin_merge()`) actually correct?**
  _`User` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Should `pipeline.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06883116883116883 - nodes in this community are weakly interconnected._
- **Why does `Carte du code` connect `DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)` to `test_recommendation.py`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `Shop` (e.g. with `admin_merge()` and `admin_metrics()`) actually correct?**
  _`Shop` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10685483870967742 - nodes in this community are weakly interconnected._
- **Should `security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06019871420222092 - nodes in this community are weakly interconnected._