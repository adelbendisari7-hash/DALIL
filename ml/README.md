# Modèles (étape 7)

| Variante (section 6.2) | État | Où |
| --- | --- | --- |
| A. TF-IDF + régression logistique | **Faite** : `train_baseline.py`, cible panne type ou famille de pièce (`--target part`), corpus traduit en option (`--corpus`) | Portable |
| B. Encodeur multilingue affiné (mmBERT, XLM-R, DziriBERT) | Carnet prêt : `kaggle/02_encodeur_fr.ipynb et 02_encodeur_enfr.ipynb`, export ONNX chargé par la chaîne (`OnnxEncoderClassifier`) | Kaggle, puis portable |
| C. Recherche + modèle de langage | Prête dans la chaîne (`mode=retrieval`) | Portable |
| D. Chaîne complète | Prête (`mode=full`) ; modèle de langage **affiné le 15/11/2026** (Qwen3-4B-Instruct-2507 + LoRA) : `kaggle/03_lora_llm.ipynb` (entraînement), `kaggle/04_fusion_gguf.ipynb` (évaluation, fusion, GGUF), servi par llama.cpp | Kaggle, puis portable |

Mode d'emploi Kaggle et mise en service : [`kaggle/README.md`](kaggle/README.md).

## Mesurer

```bash
python ml/evaluate.py --model A=ml/artifacts/baseline_tfidf_lr.joblib --modes classifier,retrieval,full
```

Mesures sur la famille de pièce : top-1, top-3, taux d'abstention (« je ne sais pas » sur une vraie panne),
taux de refus des entrées hors sujet, temps de réponse. Chaque passage écrit `results/<date>.md` (avec la liste
des erreurs) et ajoute une ligne à `results/historique.csv`.

## Premiers résultats (14/11/2026, jeux synthétiques, sans modèle de langage)

Ces chiffres **valident le code et guident les réglages** ; ils ne mesurent pas la qualité réelle. Le seul
chiffre à présenter dans le mémoire viendra du jeu de test figé d'Oran (`data/test/README.md`).

| Variante | Jeu | Top-1 | Top-3 | Abstention | Hors sujet refusé |
| --- | --- | ---: | ---: | ---: | ---: |
| A, classifieur seul | dev synthétique (50 + 5) | 88 % | 92 % | 6 % | 100 % |
| C, recherche seule (sans modèle de langage) | dev synthétique | 78 % | 88 % | 4 % | 80 % |
| D, chaîne complète (sans modèle de langage) | dev synthétique | 88 % | 94 % | 2 % | 100 % |
| D, chaîne complète | 20 cas de démonstration | 94 % | 100 % | 0 % | 100 % |

Détail : `results/20261114-1235-banc-etape7.md`.

## Variante D : modèle de langage affiné par LoRA (15/11/2026)

Qwen3-4B-Instruct-2507 chargé en 4 bits (nf4), adaptateurs LoRA r=16 sur toutes les projections (33 M paramètres
entraînés, 0,8 %), 1 passe sur 2 691 exemples, GPU T4 de Kaggle : 3 h 20. Perte d'entraînement 2,37 -> 1,15.
Adaptateur : `ml/artifacts/lora_adapter/` (hors dépôt, publié sur Kaggle comme jeu privé `dalil-lora-adapter`).

Validation (79 exemples tenus à l'écart, mêmes messages qu'en production : texte, passages, 6 candidats classés par
le modèle A) :

| Mesure | LoRA | Repère : 1er candidat (= modèle A seul) |
| --- | ---: | ---: |
| JSON valide | 79/79 (100 %) | |
| Aucune panne hors des candidats | 79/79 (100 %) | |
| Panne correcte en tête (top-1) | 50/79 (63 %) | 28/79 (35 %) |
| Panne correcte dans les 3 premières (top-3) | 69/79 (87 %) | |

Détail des réponses : `kaggle/_outputs/04_fusion_gguf/*-evaluation.json`. Erreur la plus fréquente : « batterie
faible » proposée à la place du démarreur ou de l'alternateur (symptômes de démarrage communs).

**Dans la chaîne, sur le portable** (15/11/2026, Q4_K_M servi par llama.cpp b12421 sur processeur, 12 fils ;
`ml/evaluate.py --modes retrieval,full`, détail : `results/20261115-1924-lora-q4.md`) :

| Variante | Jeu | Top-1 | Top-3 | Abstention | Hors sujet refusé | Temps moyen / p95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| C, recherche seule, sans modèle de langage | dev (50 + 5) | 74 % | 78 % | 10 % | 60 % | 0,08 s |
| C, recherche + modèle affiné | dev | 76 % | 78 % | 10 % | 60 % | 24 s / 46 s |
| C, recherche seule, sans modèle de langage | 20 cas de démo | 59 % | 77 % | 6 % | 100 % | 0,08 s |
| C, recherche + modèle affiné | 20 cas de démo | **82 %** | 88 % | 6 % | 100 % | 20 s / 36 s |
| D, chaîne complète, sans modèle de langage | dev | 86 % | 94 % | 6 % | 100 % | 0,09 s |
| D, chaîne complète + modèle affiné | dev | 86 % | 94 % | 6 % | 100 % | 21 s / 35 s |
| D, chaîne complète, sans modèle de langage | 20 cas de démo | 94 % | 100 % | 0 % | 100 % | 0,09 s |
| D, chaîne complète + modèle affiné | 20 cas de démo | 88 % | 100 % | 0 % | 100 % | 20 s / 27 s |

Lecture :
- **Sans classifieur (C), le modèle affiné apporte beaucoup** : +23 points de top-1 sur les cas de démo. Il sait
  choisir la bonne panne parmi les candidats que la recherche lui donne.
- **Avec le classifieur (D), il n'apporte rien sur ces jeux** (une erreur de plus sur 17 cas de démo). Ces jeux ont été
  écrits par l'équipe dans le vocabulaire des exemples d'amorçage : le classifieur A y est déjà à 86-94 %, il reste peu
  à gagner. Le jeu de test d'Oran, écrit par des automobilistes, dira si le modèle aide sur des textes réels.
- **Temps de réponse : 20 s en moyenne, 35 à 46 s au 95e centile**, contre 0,1 s sans modèle de langage. L'exigence
  de la section 10 (moins de 10 s) n'est pas tenue sur ce portable. Le temps se partage à parts égales entre la lecture
  du message (1 000 à 1 500 jetons à ~40 jetons/s) et l'écriture de la réponse (~180 jetons à 5-7 jetons/s). Pistes,
  à trancher à l'étape 8 : message plus court (moins de passages), réponse plus courte, ou modèle de langage réservé
  au mémoire et chaîne sans modèle de langage pour la démonstration.

**Prudence** : les étiquettes de validation viennent de la correspondance par mots-clés de l'étape 6 (textes NHTSA et
Stack Exchange traduits), pas d'un mécanicien. Le chiffre à présenter reste celui du jeu de test d'Oran, chaîne
complète, mesuré par `evaluate.py` une fois le GGUF servi par llama.cpp sur le portable.

## Ce que le banc a déjà appris (matière pour le mémoire)

- **Ajouter des sources affaiblit la détection du hors-sujet.** Après le chargement des 1 800 rappels RappelConso,
  « comment changer le mot de passe de mon compte » passait pour une panne (mots communs avec les fiches de rappel).
  Correction : le domaine se juge sur les fiches de référence seulement (`DOMAIN_SOURCES`), seuil réglé sur le jeu dev.
- **Une recherche qui trouve peu ne doit pas peser lourd.** Normaliser la recherche donnait 100 % à un seul passage
  lointain. Le poids de la recherche suit maintenant la similarité du meilleur passage (`RET_FULL_SIM`).
- **Limite de la variante A** : la similarité par fragments de caractères ne sépare pas proprement une vraie panne
  (similarité 0,135) d'une phrase hors sujet au vocabulaire automobile (« le prix du carburant », 0,181). C'est
  l'argument pour les vecteurs multilingues (Qwen3-Embedding, BGE-M3) et l'encodeur affiné de la variante B.

## Données d'entraînement

| Source | Exemples (texte → pièce) | État |
| --- | ---: | --- |
| Amorçage synthétique (`data/seed/diagnosis_examples_fr.jsonl`) + fiches | 173 + 147 | En français |
| Corpus de l'étape 6 (`data/processed/train/`) | 8 934 (NHTSA, Stack Exchange, CVFFAD) | En anglais et chinois : à traduire sur Kaggle |
| Jeu d'affinage du modèle de langage (`build_llm_dataset.py`) | 156 + 17 aujourd'hui, ~3 000 après traduction | Format identique aux appels de production |
- **Affiner un modèle de 4 milliards de paramètres sur un GPU T4 gratuit (leçons de la nuit du 14 au 15/11/2026).**
  Le T4 ne gère pas le bfloat16, que TRL active par défaut et réimpose aux adaptateurs : il faut demander fp16 et
  remettre les adaptateurs en float32 *après* la construction du `SFTTrainer`. Kaggle fournit deux T4 : le modèle
  réparti sur les deux attend sans cesse, et `SFTTrainer` refuse `DataParallel` ; on n'en montre qu'un
  (`CUDA_VISIBLE_DEVICES=0`). Sans ces réglages, 5 h de calcul sans une étape terminée ; avec, 3 h 20 pour la passe
  complète. Le carnet 03 a aussi un budget de temps (arrêt propre à 3 h 30, adaptateur sauvegardé), et le carnet 04
  reprend un adaptateur déjà entraîné pour ne pas tout refaire si la conversion échoue.
- **Évaluer en mode génération.** Juste après l'entraînement (gradient checkpointing actif, donc sans cache, et
  réponses limitées à 300 jetons), 50 s par réponse et 0 JSON valide sur 36. Sur le même adaptateur rechargé en mode
  `eval()`, avec cache et 512 jetons : 30 s par réponse sur T4 en 4 bits, 79/79 JSON valides. Les deux changements
  ont été faits ensemble ; on ne sait pas lequel des deux explique le 0/36.
