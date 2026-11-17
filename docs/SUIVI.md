# DALIL : suivi du projet

> À lire au début de chaque session. À mettre à jour à la fin de chaque étape, et chaque fois qu'une décision est prise.
> Dernière mise à jour : 17/11/2026, fin de l'étape 9.

## 1. Où on en est

**Étape 9 (application) terminée le 17/11/2026. Prochaine : étape 10 (espace magasin).**

| Étape (section 11 du cahier) | État | Notes |
| --- | --- | --- |
| 1. Socle | Fait | Docker Compose (PostgreSQL + PostGIS + pgvector), intégration continue (`.github/workflows/ci.yml`), lanceur `DEMARRER-DALIL.bat` |
| 2. Schéma | Fait | Migration Alembic `0001`, communes d'Oran |
| 3. Référentiels | Fait | Marques et modèles, taxonomie des pièces, codes OBD en français |
| 4. Annuaire | Fait | Back-office, import CSV, saisie terrain. Script OpenStreetMap écrit (`data/scripts/osm_overpass.py`), **pas encore lancé** |
| 5. Recommandation | Fait | `score_shop`, 10 scénarios testés |
| 6. Données de diagnostic | Fait | 6 sources sous licence (`data/SOURCES.md`), traduction sur Kaggle, rapport `data/processed/report.md` |
| 7. Modèles | **Fait (15/11/2026)** | Variantes A, B, C, D mesurées ; résultats dans `ml/README.md` |
| 8. Chaîne de diagnostic | **Fait (16/11/2026)** | Recherche hybride, modèle affiné derrière une interface, cache, repli, affinage en arrière-plan avec sondage. 104 tests. Résultats : `ml/README.md` (section Étape 8) |
| 9. Application | **Fait (17/11/2026)** | 7 tests e2e sur téléphone simulé (`cd frontend && npx playwright test`) : parcours automobiliste, mécanicien, hors sujet, dictée, installable, 360 px. Essai réel sur le PC validé par l'utilisateur. Site ouvrable depuis un téléphone du même Wi-Fi ; fiche d'essai sur vrai téléphone : `docs/test-telephone.md` (recommandée avant les essais d'Oran) |
| 10. Espace magasin | Base en place | Inscription, revendication, catalogue, import (`routers/shops.py`). Critère « 20 produits publiés » non vérifié |
| 11. Retours et tests | Base en place | Retours et indicateurs (`/feedback`, `/admin/metrics`). Essais avec mécaniciens et magasins d'Oran : à organiser |
| 12. Mise en ligne | Pas commencé | Seulement sur décision de l'équipe |

**Emplacement du projet : `C:\Users\Adel\Desktop\DALIL`** (hors OneDrive depuis le 15/11/2026 ; l'ancien dossier `OneDrive\Desktop\DALIL` est vide).

**Git : premier commit `ff8c735` le 15/11/2026** (étapes 1 à 7, preuve datée de la section 14), branche `master`, pas de dépôt distant.

## 2. Résultats à retenir (étape 7)

Résultats sur les jeux écrits par l'équipe, qui sont biaisés en faveur du modèle A. Le chiffre du mémoire viendra du jeu de test d'Oran (`data/test/`).

| Variante | 20 cas de démo, top-1 | Temps par diagnostic |
| --- | ---: | ---: |
| A, TF-IDF seul (en production) | 94 % | 0,1 s |
| B, mmBERT affiné | 59 % | 0,2 s |
| C, recherche + modèle de langage affiné | 82 % (59 % sans le modèle de langage) | 20 s |
| D, chaîne complète + modèle de langage affiné | 88 % | 20 s (jusqu'à 46 s) |

- **Modèle de langage affiné** : Qwen3-4B-Instruct-2507 + LoRA. Sur la validation : JSON valide 100 %, top-1 63 % (contre 35 % pour le modèle A), top-3 87 %.
- **Fichiers** (hors git) : `ml/artifacts/dalil-qwen3-4b-instruct-2507-q4_k_m.gguf` (2,5 Go) et `-q8_0.gguf` (4,3 Go), adaptateur dans `ml/artifacts/lora_adapter/`.
- **Problème ouvert** : 20 à 46 s par diagnostic sur le processeur du portable, alors que le cahier exige moins de 10 s.

## 3. Prochaines actions, dans l'ordre

1. **Étape 10 (espace magasin)** : vérifier le critère « un magasin test publie 20 produits » (inscription, revendication, catalogue, import Excel), et ajouter le test qui manque.
2. **Web scraping et collecte de données** : discussion reportée par l'utilisateur, à reprendre après l'étape 8. Deux pistes déjà proposées :
   - lancer le script OpenStreetMap (magasins d'Oran) ;
   - rédiger des demandes d'autorisation aux forums francophones. Pas de collecte sans licence notée dans `data/SOURCES.md`.
3. **Jeu de test d'Oran** : faire annoter de vrais cas par des mécaniciens (modèle : `data/test/modele_annotation_oran.csv`), puis relancer `ml/evaluate.py` sur ce jeu.
4. **Sécurité** : révoquer le jeton Kaggle utilisé pendant l'étape 7 (kaggle.com > Settings > API), ou en créer un nouveau.
5. **Étape 11 (retours et tests)** : test « un retour “pièce trouvée” modifie le score » ; essais avec des mécaniciens et des magasins d'Oran, puis compte rendu.
6. **Étape 12 (mise en ligne)** : seulement sur décision de l'équipe (hébergement, https, sauvegardes, surveillance, guide des magasins, déclaration à l'ANPDP).

## Décisions prises

| Date | Décision | Raison |
| --- | --- | --- |
| 17/11/2026 | **Modèle de langage affiné désactivé par défaut** (`USE_LLM=0` dans `DEMARRER-DALIL.bat`, `DALIL_LLM_PROVIDER=none` dans le code). Gardé en option pour les mesures du mémoire (`USE_LLM=1`) | Il ne gagne pas en précision (démo 88 -> 77 %, dev 92 -> 88 %) et prend ~1 min par diagnostic, alors que le cahier exige moins de 10 s. Pour le réactiver un jour : ré-affiner avec un jeu construit par la recherche hybride (`ml/build_llm_dataset.py`), puis remesurer |
| 17/11/2026 | Reclassement accéléré : int8, 10 passages x 256 jetons (`backend/app/config.py`) | 20 passages en float32 prenaient 15 à 24 s par diagnostic sur le portable ; maintenant 3,5 à 5 s, pour 2 points de moins sur le jeu dev (92 -> 90 %), démo inchangée (88 %), hors sujet toujours 100 % refusé |
| 16/11/2026 | Recherche hybride (vecteurs + reclassement) activée par le lanceur | Voir `ml/README.md`, section Étape 8 |

## 4. Pour reprendre le travail

- **Tests du backend** : `cd backend && .venv/Scripts/python -m pytest -q` (108 tests).
- **Tests du site sur téléphone simulé** : `cd frontend && npx playwright test` (7 tests ; si DALIL tourne déjà, `E2E_API_PORT=8100 E2E_WEB_PORT=3100 npx playwright test`).
- **Ouvrir le site sur un téléphone** : `DEMARRER-DALIL.bat` affiche l'adresse Wi-Fi du PC (fiche : `docs/test-telephone.md`).
- **Tests du pipeline de données** : `cd backend && .venv/Scripts/python -m pytest -q ../data/pipeline/tests`.
- **Servir le modèle affiné** :
  - lancer `tools/llama.cpp/llama-server.exe -m ml/artifacts/dalil-qwen3-4b-instruct-2507-q4_k_m.gguf --port 8080 -c 4096` ;
  - puis définir `DALIL_LLM_PROVIDER=openai_compat` et `DALIL_LLM_BASE_URL=http://127.0.0.1:8080/v1` ;
  - et, pour une mesure, `DALIL_LLM_TIMEOUT=300`.
- **Mesurer les variantes** : `python ml/evaluate.py --model A=ml/artifacts/baseline_tfidf_lr.joblib --modes classifier,retrieval,full` (résultats dans `ml/results/`).
- **Kaggle** : `ml/kaggle/README.md`. Points à connaître :
  - outil : `ml/kaggle/.venv` ;
  - compte : `adelbendisari` ;
  - limite : 2 sessions GPU en même temps ;
  - journaux visibles seulement à la fin d'une exécution (en direct dans l'onglet *Logs* du site).

## 5. Contraintes connues

- **L'assistant ne peut pas télécharger ni installer de programme** (llama.cpp, paquets binaires) : le système de permissions le refuse. C'est l'utilisateur qui télécharge, l'assistant installe à partir du fichier téléchargé.
- **Sur les GPU T4 de Kaggle** (leçons détaillées dans `ml/README.md`) :
  - pas de bfloat16 ;
  - un seul GPU visible ;
  - les gros fichiers temporaires vont dans `/tmp`.
- Le PC doit rester allumé, sans mise en veille, pour suivre un calcul Kaggle la nuit.

## 6. Journal

| Date | Fait |
| --- | --- |
| 14/11/2026 | Étapes 1 à 6. Début de l'étape 7 : variantes A et B, traduction des corpus sur Kaggle |
| 14-15/11/2026 (nuit) | Affinage LoRA sur Kaggle : 4 échecs corrigés (bfloat16, deux GPU, torchao, disque plein) ; adaptateur entraîné en 3 h 20 |
| 15/11/2026 | Carnet `04_fusion_gguf`, modèles GGUF rapatriés, llama.cpp installé, mesure de C et D sur le portable, graphe mis à jour. **Étape 7 terminée.** Plan de l'étape 8 rédigé. Fichier de suivi créé. Projet déplacé hors OneDrive ; premier commit `ff8c735` |
| 16/11/2026 (nuit) | Étape 8 : recherche hybride (vecteurs Kaggle 05 + reclassement), garde-fou vectoriel, cache, repli, affinage en arrière-plan. Mesure finale q8_0 + hybride : le modèle de langage dégrade légèrement (voir `ml/README.md`). 104 tests. Commit de l'étape 8 |
| 17/11/2026 | Étape 9 : configuration Playwright réparée sous Windows, tests ajoutés (dictée, navigateur sans dictée, 360 px). Relais de l'API par le site (`next.config.mjs`) pour ouvrir le site depuis un téléphone, adresse Wi-Fi affichée par le lanceur, fiche `docs/test-telephone.md`. 104 tests backend et 7 e2e passent |
| 17/11/2026 | Décision : modèle de langage désactivé par défaut dans le lanceur (option `USE_LLM=1`) |
| 17/11/2026 | Premier essai réel du site sur le PC : « Le serveur ne répond pas ». Trois défauts corrigés : (1) reclassement trop lent (15-24 s, faussement mesuré à 18 ms le 16/11) -> int8 et 10 passages, 3,5-5 s ; (2) le seed renumérotait les 88 fiches à chaque démarrage, leurs vecteurs étaient perdus et le garde-fou hors sujet muet -> seed en place + recalcul automatique des vecteurs manquants ; (3) diagnostics simultanés au démarrage -> préchargement des modèles et verrou. 108 tests backend, 31 tests pipeline |
| 17/11/2026 | Essai réel validé par l'utilisateur. Tests e2e lançables à côté de l'application (ports et dossier `.next-e2e` à part). **Étape 9 terminée**, graphe mis à jour, commit |
