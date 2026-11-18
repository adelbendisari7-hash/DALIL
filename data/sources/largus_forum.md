# Forum L'Argus : « Panne auto, mécanique et entretien » (`largus_forum`)

| | |
| --- | --- |
| Producteur | Membres du forum auto de L'Argus (largus.fr), éditeur L'Argus |
| Accès | Collecte de l'équipe (script hors dépôt, `Desktop/WebScraping/largus_forum_scraper.py`) vers une base SQLite (tables `brands`, `models`, `topics`, `messages`) ; lue en **lecture seule** par `pipeline/sources/largus.py` |
| Licence | **Accord de L'Argus (DALIL_LARGUS_AUTORISATION)** : pas de licence ouverte. Les messages appartiennent à leurs auteurs, et les conditions du site s'appliquent. Le module refuse de lire la base tant que la variable `DALIL_LARGUS_AUTORISATION` ne décrit pas l'accord obtenu |
| Licence (URL) | https://www.largus.fr/forum-auto/panne-auto-mecanique-et-entretien/ (conditions du site à joindre avec l'accord) |
| Attribution | « Forum auto L'Argus (largus.fr) » et lien vers chaque discussion (`url` de l'enregistrement) |
| Langue | Français |
| Date de vérification | 18/11/2026 : module écrit et testé sur une base fictive ; collecte en cours, accord à confirmer par écrit |

## Contenu

- Une discussion par panne, classée par marque, par modèle et par catégorie de symptôme : Freinage, Embrayage, Démarrage, Voyants, Climatisation…
- Pour chaque discussion : modèle déclaré avec année et motorisation, titre, description du problème, statut « résolu » et résumé de la solution.
- Pour chaque message : le contenu, le numéro du message et son auteur.
- Volume annoncé par la collecte : 93 marques et plus de 1 500 modèles. Estimation : 90 000 à 115 000 discussions, à vérifier à la fin de la collecte.

## Usage dans DALIL

- **Entraînement** (`kind = qa`).
  - **Le texte** est la question du conducteur : titre et description, sans la solution. C'est ce qu'écrira un utilisateur.
  - **L'étiquette** est la famille de pièce, tirée par ordre de confiance (`label_quality`) :
    1. `solution` : de la solution confirmée, ou du dernier message de l'auteur d'une discussion résolue ;
    2. `reponses` : de la pièce la plus citée dans les réponses ;
    3. `question` : de la question elle-même.
  - Le suffixe « +component » indique un accord avec la catégorie du forum.
  - Une panne type n'est attribuée que pour `solution+component`.
- **Base de connaissances** : la question, avec le résumé de la solution dans `meta.solution`.

## Anonymisation

- Le nom de l'auteur ne sort jamais du module : il sert seulement à reconnaître les messages de l'auteur de la question.
- Effacés des textes : adresses e-mail, liens, numéros de téléphone et mentions « @ ».
- On garde le lien de la discussion, pour l'attribution.

## Limites

- **Peu de discussions sont marquées « résolues »** : 2 sur 23 dans le premier échantillon. Les étiquettes `reponses` et `question` sont plus faibles. L'entraînement doit pouvoir les pondérer ou les écarter, et la mesure le dira.
- **Le parc est français** : les modèles récents chinois, très présents en Algérie, sont peu ou pas représentés.
- **Certaines catégories sont hors taxonomie** (« Lève-vitre », « Essuie-glace »). Elles restent sans étiquette.

## Commande

```bash
DALIL_LARGUS_AUTORISATION="écrite, AAAA-MM-JJ" python data/pipeline/run.py collect --sources largus_forum --largus-db <chemin>/largus_pannes.db
python data/pipeline/run.py load --sources largus_forum
```
