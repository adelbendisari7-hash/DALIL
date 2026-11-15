# DALIL : suivi du projet

> À lire au début de chaque session. À mettre à jour à la fin de chaque étape, et chaque fois qu'une décision est prise.
> Dernière mise à jour : 15/11/2026, fin de l'étape 7.

## 1. Où on en est

**Étape en cours : 8 (chaîne de diagnostic). Elle n'est pas commencée : le plan attend la validation de l'équipe.**

| Étape (section 11 du cahier) | État | Notes |
| --- | --- | --- |
| 1. Socle | Fait | Docker Compose (PostgreSQL + PostGIS + pgvector), intégration continue (`.github/workflows/ci.yml`), lanceur `DEMARRER-DALIL.bat` |
| 2. Schéma | Fait | Migration Alembic `0001`, communes d'Oran |
| 3. Référentiels | Fait | Marques et modèles, taxonomie des pièces, codes OBD en français |
| 4. Annuaire | Fait | Back-office, import CSV, saisie terrain. Script OpenStreetMap écrit (`data/scripts/osm_overpass.py`), **pas encore lancé** |
| 5. Recommandation | Fait | `score_shop`, 10 scénarios testés |
| 6. Données de diagnostic | Fait | 6 sources sous licence (`data/SOURCES.md`), traduction sur Kaggle, rapport `data/processed/report.md` |
| 7. Modèles | **Fait (15/11/2026)** | Variantes A, B, C, D mesurées ; résultats dans `ml/README.md` |
| 8. Chaîne de diagnostic | À faire | Plan : `docs/plan-etape-8.md`. Le critère de fin passe déjà sans modèle de langage |
| 9. Application | Base en place | Pages `diagnostic`, `magasins`, `pieces`, `connexion`, PWA, test e2e `frontend/e2e/parcours.spec.ts`. Critère non vérifié sur téléphone |
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

1. **Valider le plan de l'étape 8** (`docs/plan-etape-8.md`). Deux décisions attendues :
   - reporter la recherche hybride (vecteurs) après l'étape 9 ?
   - modèle de langage trop lent : raccourcir le message envoyé, ou garder A pour la démonstration et D pour le mémoire ?
2. **Réaliser l'étape 8** après validation :
   - repli automatique si le modèle de langage tarde ;
   - cache des réponses ;
   - indicateur de progression ;
   - tests avec un faux fournisseur.
3. **Web scraping et collecte de données** : discussion reportée par l'utilisateur, à reprendre après l'étape 8. Deux pistes déjà proposées :
   - lancer le script OpenStreetMap (magasins d'Oran) ;
   - rédiger des demandes d'autorisation aux forums francophones. Pas de collecte sans licence notée dans `data/SOURCES.md`.
4. **Jeu de test d'Oran** : faire annoter de vrais cas par des mécaniciens (modèle : `data/test/modele_annotation_oran.csv`), puis relancer `ml/evaluate.py` sur ce jeu.
5. **Sécurité** : révoquer le jeton Kaggle utilisé pendant l'étape 7 (kaggle.com > Settings > API), ou en créer un nouveau.

## 4. Pour reprendre le travail

- **Tests du backend** : `cd backend && .venv/Scripts/python -m pytest -q` (64 tests).
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
