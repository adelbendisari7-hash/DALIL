# Étape 7 sur Kaggle : traduction et entraînement

Le portable n'a pas de carte graphique : les calculs lourds tournent sur le GPU gratuit de Kaggle
(quota hebdomadaire affiché dans le compte, souvent autour de 30 heures). Trois carnets, à lancer dans l'ordre.
Ils sont générés par `python ml/kaggle/make_notebooks.py` : modifier ce script, pas les `.ipynb`.

| Carnet | Rôle | Durée indicative (T4) | Sortie à rapatrier |
| --- | --- | --- | --- |
| `01_traduction.ipynb` | Traduit en français les corpus de l'étape 6 et prépare l'échantillon de relecture | 1 à 2 h | `dalil_processed.zip` → `data/processed/` |
| `02_encodeur_fr.ipynb et 02_encodeur_enfr.ipynb` | Variante B : mmBERT (ou XLM-R, DziriBERT) affiné, exporté en ONNX | 20 à 60 min par configuration | `<modèle>_<config>_onnx.zip` → `ml/artifacts/<modèle>_<config>/` |
| `03_lora_llm.ipynb` | Variante D : Qwen3-4B (ou Gemma 3 4B) affiné par LoRA, exporté en GGUF | 3 h 30 au plus (budget de temps) | `dalil-…-q4_k_m.gguf` → `ml/artifacts/` |
| `04_fusion_gguf.ipynb` | Reprise sans réentraîner : évaluation, fusion et GGUF à partir de l'adaptateur (`kaggle_run.py adapter`) | 25 min (+ 40 min si `RUN_EVAL`) | `dalil-…-q4_k_m.gguf` et `-q8_0.gguf` → `ml/artifacts/` |
| `05_vecteurs.ipynb` | Étape 8 : vecteurs Qwen3-Embedding-0.6B des passages de la base de connaissances et modèles de recherche (Qwen3-Embedding, bge-reranker-v2-m3). Entrée : `python ml/export_kb_chunks.py` puis `kaggle_run.py dataset` | 15 min | `chunk_vectors.npy`, `chunk_ids.json`, deux zip → `python ml/load_vectors.py` les installe dans `ml/artifacts/` |

## Entraîner avec L'Argus (variante A contre CamemBERT)

Les deux variantes lisent le **même** jeu d'entraînement, `data/processed/train_set/`, fabriqué par
`ml/build_training_set.py`. Ce script :
- retire tout texte présent dans un jeu de test ;
- donne à chaque exemple un poids selon la confiance de son étiquette ;
- garde par défaut les étiquettes sûres seulement, avec les exemples d'amorçage comptés cinq fois (réglage mesuré le 18/11/2026).

1. **Charger L'Argus**, seulement avec l'accord écrit :
   `DALIL_LARGUS_AUTORISATION="écrite, AAAA-MM-JJ" python data/pipeline/run.py collect --sources largus_forum --largus-db <chemin>`,
   puis `python data/pipeline/run.py load --sources largus_forum`. Relire 100 étiquettes au hasard dans
   `data/processed/train/largus_forum.jsonl`.
2. **Construire le jeu commun** : `python ml/build_training_set.py`. Pour tester d'autres réglages, ajouter
   `--quality moyen`, `--seed-weight 1` ou `--max-per-label 3000`. Lire `stats.json`.
3. **Variante A**, sur le portable (environ 2 min) : `python ml/train_baseline.py --set`, ce qui produit `ml/artifacts/baseline_tfidf_lr_set.joblib`.
4. **Variante B**, CamemBERT sur Kaggle :
   - publier une nouvelle version du jeu de données, avec `python ml/kaggle/kaggle_run.py dataset` ;
   - lancer le carnet, avec `python ml/kaggle/kaggle_run.py push 02_encodeur_camembert` ;
   - au bout de 30 à 90 min selon le volume, récupérer le résultat, avec `python ml/kaggle/kaggle_run.py output 02_encodeur_camembert` ;
   - dézipper dans `ml/artifacts/camembert-base_set/`.

   Pour essayer CamemBERTa-v2, changer `MODEL_ID` dans `make_notebooks.py`.
5. **Mesurer** :
   ```bash
   python ml/evaluate.py --model A-actuel=ml/artifacts/baseline_tfidf_lr.joblib        --model A-largus=ml/artifacts/baseline_tfidf_lr_set.joblib --model B-camembert=ml/artifacts/camembert-base_set        --modes classifier,full --test data/test/dev_fr_synthetique.jsonl --test data/seed/demo_cases.json        --test data/test/audit_ecriture_oran.jsonl --test data/test/audit_ecriture_oran_controle.jsonl --tag largus
   ```
   Les réglages se choisissent sur `dev`, `demo` et `audit` ; `audit_ecriture_oran_controle` n'est regardé qu'à la fin.
   Un nouveau modèle ne remplace le modèle en service que s'il fait mieux sans rien perdre ailleurs.

Les données de L'Argus, même anonymisées, montent sur Kaggle dans le jeu de données **privé**. L'accord de L'Argus
doit couvrir cet usage.

## CamemBERT sur les forums nettoyés (27/11/2026)

Deux carnets, sur le jeu privé **`dalil-camembert`** (L'Argus + Techniconnexion anonymisés, accords déclarés par
l'utilisateur, écrits à archiver ; jamais `data/test_prive/`, le script le refuse) :

1. `python ml/kaggle/build_camembert_sets.py` fabrique `data/processed/camembert/` :
   - `pieces` : amorçage + vrais exemples vérifiés des deux forums (916 exemples, étiquette = pièce) ;
   - `familles` : étiquettes « fort » des deux forums, questions de procédure retirées (`--diagnostic-seul`),
     amorçage x5 et vrais exemples (17 602 exemples, étiquette = famille). Textes des jeux de test exclus.
2. `python ml/kaggle/kaggle_run.py dataset-camembert` publie le jeu privé.
3. `python ml/kaggle/kaggle_run.py push 02_camembert_familles` (3 époques, ~25 min) et
   `push 02_camembert_pieces` (40 époques, ~20 min) ; `output <carnet>` puis dézipper dans
   `ml/artifacts/camembert-base_familles/` et `ml/artifacts/camembert-base_pieces/` (ONNX, 443 Mo chacun).
4. Assembler les deux niveaux : `python ml/assembler_deux_niveaux.py --base <base.joblib ou dossier ONNX de pièces>
   --familles ml/artifacts/camembert-base_familles --alphas 0.15,0.25,0.5 --out-dir ml/artifacts/exp/camembert`.
   Le `.joblib` garde le chemin du dossier ONNX relatif à lui-même : les déplacer ensemble.

Résultats et décision : `ml/README.md`, section « Techniconnexion et CamemBERT ».

## Préparer le jeu de données Kaggle « dalil-pipeline »

Sur le portable :

```bash
python data/pipeline/run.py collect     # si data/processed/ n'est pas à jour
python ml/build_llm_dataset.py          # à relancer après la traduction (le jeu passe de ~170 à ~3 000 exemples)
```

Puis créer sur kaggle.com un jeu de données **privé** nommé `dalil-pipeline`, contenant `backend/`, `data/pipeline/`,
`data/seed/`, `data/test/` et `data/processed/` (sans `data/raw/`, `.venv/`, `node_modules/`, `frontend/`).
À chaque mise à jour des données : « New version » du jeu de données.

## Ordre conseillé

1. `01_traduction` → rapatrier `data/processed/` → `python data/pipeline/run.py load` → **relire**
   `data/processed/translations/relecture.csv` (200 traductions ; corriger `POSTEDIT` si un nom de pièce est faux).
2. Sur le portable : `python ml/train_baseline.py --target part --corpus` (variante A avec le corpus traduit),
   puis `python ml/build_llm_dataset.py` ; nouvelle version du jeu Kaggle.
3. `02_encodeur_classifieur` deux fois : `CONFIG = "fr"` puis `CONFIG = "en+fr"` (traduire ou transférer, section 6.3).
4. `03_lora_llm`. Si l'entraînement réussit mais que la suite échoue, récupérer l'adaptateur (`kaggle kernels output`, dossier `adapter/`) dans `ml/artifacts/lora_adapter/`, puis `kaggle_run.py adapter` et `kaggle_run.py push 04_fusion_gguf`.
5. `05_vecteurs` (après `export_kb_chunks.py` et une nouvelle version du jeu de données), puis `python ml/kaggle/kaggle_run.py output 05_vecteurs` et `python ml/load_vectors.py`. À refaire si la base de connaissances est rechargée (les identifiants des passages changent).
6. Mesurer toutes les variantes sur le portable avec `ml/evaluate.py` (ci-dessous). Recherche hybride : `DALIL_RETRIEVAL_MODE=hybrid`. Avec le modèle de langage affiné : `bash ml/eval_with_llm.sh <fichier.gguf> <étiquette> full`.

## Faire tourner les modèles sur le portable

Deux installations, à faire par vous (elles touchent au système ou exécutent un programme téléchargé) :

1. **Microsoft Visual C++ Redistributable** (x64), installeur officiel :
   https://aka.ms/vs/17/release/vc_redist.x64.exe. Sans lui, `onnxruntime` et `torch` ne se chargent pas sous Windows.
   Ensuite : `backend/.venv/Scripts/pip install onnxruntime tokenizers`.
2. **llama.cpp** pour servir le modèle de langage affiné : archive `llama-<version>-bin-win-cpu-x64.zip` de
   https://github.com/ggml-org/llama.cpp/releases, à décompresser dans `tools/llama.cpp/` (dossier ignoré par git). Puis :

```bash
tools/llama.cpp/llama-server.exe -m ml/artifacts/dalil-qwen3-4b-instruct-2507-q4_k_m.gguf --port 8080 -c 4096
```

et dans `.env` : `DALIL_LLM_PROVIDER=openai_compat`, `DALIL_LLM_BASE_URL=http://localhost:8080/v1`.

`q4_k_m` (~2,5 Go) est le plus rapide sur processeur ; `q8_0` (~4,3 Go) est un peu plus fidèle et plus lent. Le message envoyé au modèle fait environ 1 500 jetons : mesurer le temps de réponse avant la démonstration (exigence : diagnostic en moins de 10 s).

## Mesurer (portable)

```bash
python ml/evaluate.py --model A=ml/artifacts/baseline_tfidf_lr.joblib \
                      --model B-fr=ml/artifacts/mmBERT-base_fr --model B-enfr=ml/artifacts/mmBERT-base_en-fr \
                      --modes classifier,retrieval,full --tag comparaison
```

Le modèle de langage utilisé par les variantes C et D est celui de la configuration (`DALIL_LLM_PROVIDER`) :
lancer la même commande avec `openai_compat` (modèle affiné), puis une seule fois avec `anthropic` (modèle payant,
point de comparaison seulement, section 6.8). Les résultats s'accumulent dans `ml/results/historique.csv`.

**Le jour où le jeu de test d'Oran existe**, ajouter `--test data/test/oran_test.jsonl` : c'est le seul chiffre
à présenter comme résultat dans le mémoire.

## Mettre un modèle en service

Régler `DALIL_CLASSIFIER_PATH` (fichier `.joblib` ou dossier ONNX) et `DALIL_MODEL_VERSION` dans `.env`.
Chaque diagnostic enregistre la version du modèle (`diagnosis_sessions.model_version`).
