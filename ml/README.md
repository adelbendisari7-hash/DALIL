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

## Étape 8 : recherche hybride et chaîne complète (16/11/2026)

Recherche hybride = mots-clés + vecteurs Qwen3-Embedding-0.6B, fusionnés par rangs réciproques, puis passages
reclassés par bge-reranker-v2-m3 (20 le 16/11 ; 10 en int8 depuis le 17/11). Garde-fou « est-ce une panne ? » sur la ressemblance vectorielle avec les fiches
(seuil 0,487 ; pannes >= 0,492, hors-sujet <= 0,482 : marge mince, réglée sur des jeux écrits par l'équipe).
Détails : `results/20261116-0000-hybride-garde-vecteurs.md`, `results/20261116-0054-lora-q8-hybride.md`.

| Chaîne complète (D) | Jeu | Top-1 | Top-3 | Hors sujet refusé | Temps moyen |
| --- | --- | ---: | ---: | ---: | ---: |
| Mots-clés, sans modèle de langage | dev | 86 % | 94 % | 100 % | 0,09 s |
| Hybride, sans modèle de langage (20 passages, float32) | dev | **92 %** | **98 %** | 100 % | ~20 s (voir correction) |
| **Hybride, reclassement int8, 10 passages x 256 jetons (réglage retenu le 17/11)** | dev | 90 % | 96 % | 100 % | **4,9 s (p95 6,7 s)** |
| Hybride + modèle affiné q8_0 | dev | 88 % | 96 % | 100 % | 63 s |
| Mots-clés, sans modèle de langage | démo (17) | 94 % | 100 % | 100 % | 0,09 s |
| Hybride, sans modèle de langage (20 passages, float32) | démo | 88 % | 100 % | 100 % | ~20 s (voir correction) |
| **Hybride, reclassement int8, 10 x 256 (réglage retenu)** | démo | 88 % | 100 % | 100 % | **3,5 s (p95 4,7 s)** |
| Hybride + modèle affiné q8_0 | démo | 77 % | 94 % | 100 % | 56 s |

Lecture honnête :
- La recherche hybride améliore le jeu dev (+6 points de top-1) et garde 100 % de refus des hors-sujets.
- **Le modèle affiné q8_0 *dégrade* la chaîne sur ces jeux** (92 -> 88 % dev, 88 -> 77 % démo) et coûte ~1 minute
  par diagnostic sur le portable (processeur seul). Le classifieur y est déjà très bon ; le modèle de langage
  réordonne parfois à tort. Écart faible (1 à 2 cas) mais constant dans le même sens.
- Le modèle a été entraîné avec des passages issus de la recherche par mots-clés ; la recherche hybride lui en donne
  d'autres (décalage de distribution). Piste : régénérer le jeu d'entraînement avec la recherche hybride.
- Décision du 17/11/2026 : **modèle de langage désactivé par défaut** (`USE_LLM=1` dans `DEMARRER-DALIL.bat` pour le
  réactiver le temps d'une mesure) : il ne gagne pas en précision et ne tient pas les 10 s. Le chiffre à présenter
  reste celui du jeu de test d'Oran.

**Correction du 17/11/2026 (deux défauts trouvés en essayant le site sur le portable).**
- *Temps de réponse.* Les « 16-18 ms » du 16/11 étaient faux : mesurés sur des questions déjà en cache. Le
  reclassement de 20 passages x 512 jetons en float32 prend en réalité 15 à 24 s par question nouvelle sur le
  processeur du portable. Réglage retenu (`rerank_pool=10`, `rerank_max_len=256`, `rerank_int8=True` dans
  `backend/app/config.py`) : 2,9 s pour le reclassement, 3,5 à 4,9 s par diagnostic, pour 2 points de moins sur le
  jeu dev (`results/20261117-1542-hybride-int8-10x256-vecteurs-repares.md`).
- *Vecteurs des fiches perdus.* `python -m app.seed`, relancé à chaque démarrage par le lanceur, supprimait et recréait
  les 88 fiches de l'équipe : nouveaux identifiants, et leurs vecteurs (rangés par identifiant) ne les retrouvaient
  plus. Effet : le garde-fou vectoriel ne répondait plus, et « le prix du carburant a encore augmenté » passait pour
  une panne. Corrigé de deux façons : le seed met à jour les fiches en place (identifiants stables), et la recherche
  recalcule elle-même les vecteurs des fiches qui en manquent (`DenseIndex.ensure_reference`, ~20 s une seule fois).
- *Démarrage.* Les modèles sont chargés dès le démarrage de l'API (`app.main.warmup`, ~1 min en arrière-plan), et la
  partie recherche et classifieur est protégée par un verrou : sans lui, deux diagnostics simultanés pendant la
  construction des index échouaient (`NotFittedError`, 12 fois sur 15 dans `tests/test_concurrence.py`).

## Qualité des réponses sur des textes écrits comme à Oran (18/11/2026)

Les jeux dev et démo sont en français propre ; les automobilistes d'Oran écrivent avec des fautes, en style SMS, en
darija (lettres latines ou arabes). Deux jeux synthétiques mesurent cet écart (`data/test/README.md`) : l'audit (48 cas,
a servi à régler) et le contrôle (20 cas écrits avant les corrections, jamais utilisés pour les écrire).

| Bonne pièce dans les 3 premières (top-3), mode hybride | Avant | Lexique darija | + 2 fiches, 255 exemples, règle hors sujet |
| --- | ---: | ---: | ---: |
| Audit (réglage) | 56 % | 78 % | **89 %** |
| Contrôle (jamais vu) | 38 % | 94 % | **100 %** |
| Dev (français propre) | 96 % | 96 % | **98 %** |
| Démo | 100 % | 100 % | **100 %** |
| « Je ne sais pas » à tort (audit) | 42 % | 20 % | **7 %** |
| Hors sujet refusé (tous les jeux) | 67 à 100 % | 75 à 100 % | **100 %** |

Ce qui a été changé :
1. **Lexique darija → français** (`diagnosis/darija.py`, section 6.1 du cahier, étape 1). Tournures négatives (« ma tdemarich »),
   verbes de symptômes (« ysakhen », « ysoni », « tfargh »), arabe avec article et préfixes (« الموتور يسخن »). Toute la chaîne
   reçoit du français ; la page de résultat affiche « Nous avons compris : … ».
2. **Deux fiches de pannes manquantes** : ampoule ou feu grillé, ralenti instable ou calage au ralenti.
3. **255 nouveaux exemples d'entraînement** (173 -> 428, au moins 9 par panne) ; validation croisée du classifieur :
   top-1 59 % -> 72 %.
4. **Règle hors sujet** : prix, achat, vente, permis, salutations, sans symptôme ni pièce citée -> « je ne sais pas »
   (« combien coûte le gasoil » passait pour une panne).

Prudence : audit, contrôle et lexique ont le même auteur ; le chiffre du mémoire reste celui du jeu de test d'Oran.
Restent mal traités : « fumée noire et ça consomme », « ça s'éteint tout seul en route », « tak tak en tournant le volant »
(rotules au lieu de cardans), et l'arabe au-delà du vocabulaire courant.

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

## L'Argus et le classifieur à deux niveaux (24/11/2026)

**Relecture de 200 étiquettes** de L'Argus, par Claude, sans voir le niveau de confiance (`ml/relecture_etiquettes.py`,
`results/20261124-0900-relecture-largus_forum.md`). La pièce exacte n'est juste que dans 28 % des cas ; la famille l'est
dans 75 à 89 % des cas quand elle concorde avec la catégorie du forum.

**Première tentative, rejetée.** Les étiquettes de famille ont été ajoutées au classifieur de pièces (21 643 exemples).
Le modèle a reculé : démo 94 -> 77 %, refus du hors-sujet 100 -> 80 % (`results/20261124-0823-largus-famille.md`).

**Deux niveaux, retenu.** Un modèle de familles est entraîné sur L'Argus et sur l'amorçage (`ml/train_family_reranker.py`,
93 % sur la validation de L'Argus). Il reclasse les pannes du modèle en service : score = p(panne) x p(famille) ^ alpha.
Alpha a été réglé sur dev, démo et audit, puis vérifié sur le contrôle :

| Chaîne complète, top-1 | Mots-clés : en service | Mots-clés : alpha 0,25 | Hybride : en service | Hybride : alpha 0,25 |
| --- | ---: | ---: | ---: | ---: |
| Dev | 90 % | 90 % | 92 % | 92 % |
| Démo | 94 % | 94 % | 94 % | 94 % |
| Audit d'Oran | 82 % | 84 % | 82 % | 87 % |
| Contrôle (jamais vu) | 88 % | 94 % | 88 % | 94 % |
| Hors-sujet refusé | 100 % | 100 % | 100 % | 100 % |

Alpha 0,5 gagne sur dev (94 %) mais perd sur l'audit ; alpha 1 et 2 perdent sur la démo et le hors-sujet. Gains modestes
(1 à 2 cas par jeu) mais tous dans le même sens. Le fichier (`ml/artifacts/famille_rerank_a0.25.joblib`, 31 Mo) reste
hors git, parce que son vocabulaire est tiré des textes de L'Argus ; `DEMARRER-DALIL.bat` l'utilise s'il est présent.

## Sur de vrais textes de conducteurs : le jeu de test L'Argus (26/11/2026)

104 cas réels, à cause confirmée, jamais utilisés pour entraîner ni régler (`data/test/README.md`) :

| Chaîne complète | Modèle de référence seul | Deux niveaux, alpha 0,25 (en service) |
| --- | ---: | ---: |
| Mots-clés : top-1 / top-3 | 34 / 48 % | 36 / 55 % |
| Hybride : top-1 / top-3 | 28 / 47 % | **34 / 57 %** |
| « Je ne sais pas » à tort (hybride) | 27 % | **9 %** |
| Temps moyen (hybride, sans cache) | 8,8 s | (même chaîne) |

Lecture :
- **Sur de vrais textes, DALIL est bien moins bon que sur les jeux de l'équipe** (environ 55 % contre 90 % et plus pour la
  bonne pièce dans les 3 premières). C'est le biais que l'on soupçonnait : les jeux de l'équipe ont le même auteur que les
  exemples d'entraînement. Le jeu d'Oran reste la mesure de référence pour le mémoire.
- Le classifieur à deux niveaux confirme son gain sur ces textes indépendants (+10 points de top-3 en hybride, trois fois
  moins d'abstentions à tort).
- Les vrais textes sont plus longs : 8,8 s par diagnostic en hybride, proche de la limite de 10 s.
- **Tenir compte du véhicule** (fréquence des familles de pannes par modèle, tirée de L'Argus, lissée) a été simulé hors
  ligne avant d'être développé : au mieux deux cas de plus sur 104 en top-1, rien en top-3. Piste abandonnée.

### Fiches de pannes supplémentaires : essai non retenu (26/11/2026)

12 des 45 erreurs sur les vrais cas venaient de pièces qui ne sont la pièce principale d'aucune panne type. Dix fiches ont
été écrites, avec 10 exemples chacune, puis mesurées sur un **jeu de contrôle** de 43 vrais cas tiré avant toute correction :

| Chaîne complète, top-1 / top-3 | Avant | Avec les 10 fiches |
| --- | --- | --- |
| Jeu L'Argus étudié (104) | 36 / 57 % | 35 / 61 % |
| **Contrôle L'Argus (43)** | 37 / 58 % | 37 / 54 % |
| Audit d'Oran / contrôle d'Oran | 87 / 91 %, 94 / 100 % | 82 / 89 %, 88 / 100 % |

Le gain n'existe que sur le jeu qui a servi à écrire les fiches : c'est un sur-ajustement, que seul le jeu de contrôle
permettait de voir. Les fiches restent en brouillon (`data/seed/brouillons/`) ; il leur faudra de vrais exemples.

