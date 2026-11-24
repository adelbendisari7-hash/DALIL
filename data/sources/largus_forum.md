# Forum L'Argus : « Panne auto, mécanique et entretien » (`largus_forum`)

| | |
| --- | --- |
| Producteur | Membres du forum auto de L'Argus (largus.fr), éditeur L'Argus |
| Accès | Collecte de l'équipe (script hors dépôt, `Desktop/WebScraping/largus_forum_scraper.py`) vers une base SQLite (tables `brands`, `models`, `topics`, `messages`) ; lue en **lecture seule** par `pipeline/sources/largus.py` |
| Licence | **Accord de L'Argus (DALIL_LARGUS_AUTORISATION)** : pas de licence ouverte. Les messages appartiennent à leurs auteurs, et les conditions du site s'appliquent. Le module refuse de lire la base tant que la variable `DALIL_LARGUS_AUTORISATION` ne décrit pas l'accord obtenu |
| Licence (URL) | https://www.largus.fr/forum-auto/panne-auto-mecanique-et-entretien/ (conditions du site à joindre avec l'accord) |
| Attribution | « Forum auto L'Argus (largus.fr) » et lien vers chaque discussion (`url` de l'enregistrement) |
| Langue | Français |
| Date de vérification | 24/11/2026 : collecte terminée, module corrigé sur la vraie base ; accord déclaré par l'utilisateur le 24/11/2026, confirmation écrite à archiver |

## Contenu

- Une discussion par panne, classée par marque, par modèle et par catégorie de symptôme : Freinage, Embrayage, Démarrage, Voyants, Climatisation…
- Pour chaque discussion : modèle déclaré avec année et motorisation, titre, description du problème, statut « résolu » et résumé de la solution.
- Pour chaque message : le contenu, le numéro du message et son auteur.
- Volume réel (24/11/2026) : 99 779 discussions, 400 801 messages (le message #1 recopie la description), 28 marques et 872 modèles. Renault, Citroën et Peugeot font 42 % des discussions ; Dacia 351 seulement.
- 80 % des discussions datent de 2005 à 2015 (médiane : 2010). Description : 420 caractères en médiane.

## Usage dans DALIL

- **Entraînement** (`kind = qa`).
  - **Le texte** est la question du conducteur : titre et description, sans la solution. C'est ce qu'écrira un utilisateur.
  - **L'étiquette** est la famille de pièce, tirée par ordre de confiance (`label_quality`) :
    1. `solution` : du résumé de solution, ou du message de l'auteur qui donne la cause (« c'était bien… », « résolu », « j'ai changé… »), que la discussion soit marquée résolue ou non ;
    2. `auteur` : du dernier message de l'auteur, sans tournure de solution ;
    3. `reponses` : de la pièce la plus citée dans les réponses ;
    4. `question` : de la question elle-même.
  - Le suffixe « +component » indique un accord avec la catégorie du forum.
  - Une panne type n'est attribuée que pour `solution+component`.
- **Base de connaissances** : la question, avec le résumé de la solution dans `meta.solution`.

## Anonymisation

- Le nom de l'auteur ne sort jamais du module : il sert seulement à reconnaître les messages de l'auteur de la question.
- Effacés des textes : adresses e-mail, liens, numéros de téléphone et mentions « @ ».
- On garde le lien de la discussion, pour l'attribution.

## Limites

- **Presque aucune discussion n'est marquée « résolue »** : 196 sur 99 779 (0,2 %), et 193 résumés de solution. Mais l'auteur revient dans 44 % des discussions et donne souvent la cause : c'est la source principale des étiquettes sûres. Les niveaux `auteur`, `reponses` et `question` sont plus faibles. Une relecture de 200 étiquettes (`ml/relecture_etiquettes.py`) fixe ce qu'on garde et avec quel poids.
- **Catégories** : 51 catégories propres couvrent 74 % des discussions ; ailleurs, le champ contient le titre recopié depuis l'adresse et n'est pas utilisé. Les sujets « Avis et fiabilité », « Entretien », « Autoradio », « GPS », « Alarme », « Carrosserie », « Actualité » ne décrivent pas une panne : hors de l'entraînement.
- **Le parc est français et ancien** : les modèles les plus vendus en Algérie aujourd'hui (Geely Coolray, Livan X3 Pro, MG5, Kia KX1, VW T-Roc) sont absents ; environ 63 % des annonces Ouedkniss portent sur un modèle présent dans L'Argus (comparaison approximative des noms).
- **Pas de darija** : ces données améliorent le français, pas l'écriture d'Oran.
- **Certaines catégories sont hors taxonomie** (« Lève-vitre », « Essuie-glace »). Elles restent sans étiquette.

## Commande

```bash
DALIL_LARGUS_AUTORISATION="écrite, AAAA-MM-JJ" python data/pipeline/run.py collect --sources largus_forum --largus-db <chemin>/largus_pannes.db
python data/pipeline/run.py load --sources largus_forum
```
