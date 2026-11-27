# Forum Techniconnexion : résolution des problèmes techniques (`techniconnexion`)

| | |
| --- | --- |
| Producteur | Membres du forum Techniconnexion (techniconnexion.com, hébergé par Forumactif) ; administrateurs « Tech-admin » |
| Accès | Collecte de l'équipe (script hors dépôt, `Desktop/WebScraping/scraper.py`) vers des fichiers JSONL (`ml_ready/dataset_full.jsonl`, `posts_with_metadata.jsonl`) ; lus en **lecture seule** par `pipeline/sources/techniconnexion.py` |
| Licence | **Accord des administrateurs de Techniconnexion (DALIL_TECHNICONNEXION_AUTORISATION)** : pas de licence ouverte. Le site n'a ni conditions d'utilisation ni mentions légales ; la charte dit seulement « Tout message publié demeure sous la responsabilité de son auteur ». Son `robots.txt` déclare `Content-Signal: ai-train=no, search=yes, ai-input=no` et bloque les robots d'IA (vérifié le 27/11/2026). Le module refuse de lire la collecte tant que la variable ne décrit pas l'accord obtenu |
| Licence (URL) | https://www.techniconnexion.com/t582-la-charte-du-forum-a-lire-obligatoirement (charte ; accord écrit à joindre) |
| Attribution | « Forum Techniconnexion (techniconnexion.com) » et lien vers chaque discussion (`url` de l'enregistrement) |
| Langue | Français |
| Date de vérification | 27/11/2026 : **accord oral (téléphone) déclaré par l'utilisateur**, qui précise ensuite que les administrateurs autorisent l'usage par des modèles d'IA, alors que le site affiche `ai-train=no` ; **confirmation écrite à obtenir et archiver**. Données hors git ; envoyées anonymisées dans le jeu Kaggle **privé** `dalil-camembert` le 27/11/2026, à la demande de l'utilisateur |

## Contenu

- 30 421 discussions et 276 179 messages (collecte terminée le 27/11/2026), 19 318 auteurs, surtout de 2006 à 2015.
- Sections par groupe de marques et par domaine (Moteur 48 %, Électricité 29 %, Trains roulants 12 %, Intérieur, Carrosserie, Divers).
- Marques : BMW et Mini 32 %, Peugeot et Citroën 15 %, groupe VW 14 %, Renault et Dacia 13 %, Ford 8 %.
- Pour chaque discussion : modèle déclaré (connu dans 93 % des cas), moteur, carburant (Diesel 73 % quand il est connu), année (43 % manquante), codes défaut.
- Pour chaque message : texte et HTML, auteur, rang de l'auteur sur le forum (Nouveau, Petit mécano, Mécano, Tech-d'honneur, Tech-admin…).
- 576 sujets « problèmes résolus et fiches pratiques » : ce ne sont que des index (des listes de liens vers les discussions réglées). Ils désignent 2 740 discussions rangées comme résolues par un modérateur.

## Usage dans DALIL

- **Entraînement** (`kind = qa`), comme L'Argus : le texte est la question du conducteur (titre et premier message), sans la solution.
- **L'étiquette** est la famille de pièce, par ordre de confiance (`label_quality`) :
  1. `solution` : message de l'auteur qui donne la cause (« c'était bien… », « résolu », « j'ai changé… ») ;
  2. `auteur` : dernier message de l'auteur, sans tournure de solution ;
  3. `reponses` : pièce la plus citée dans les réponses, celles des techniciens confirmés du forum comptant double ;
  4. `question` : pièce citée dans la question.
- Le suffixe « +domaine » indique un accord avec la section du forum (Moteur, Électricité, Trains roulants…). Une panne type n'est attribuée que pour `solution+domaine` dans une discussion résolue.
- **Vrais exemples** : les causes affirmées sont extraites (`ml/extraire_causes_largus.py --source techniconnexion`) puis vérifiées une à une, comme pour L'Argus.

## Réduction du bruit

- **Citations retirées** : le texte de chaque message est relu dans son HTML, sans les blocs `<blockquote>`. 22 000 messages citent un autre message ; sans cela, l'hypothèse d'un autre passerait pour la cause trouvée.
- **Mentions du forum retirées** : fichiers joints, « Vous n'avez pas la permission de télécharger… », « Téléchargé n fois », « Dernière édition par… », « Sujet répertorié ici ».
- **Formules de clôture des modérateurs** : « merci pour le retour d'infos, sujet répertorié » (34 % du champ `solution_text` de la collecte dans les sujets résolus). Elles ne servent jamais d'étiquette, seulement d'indice de résolution (`meta.repertorie`).
- **Sujets qui ne sont pas des pannes** (`diagnostic = False`, hors entraînement) : index des sections « résolus », tutos, fiches pratiques, listes, périodicités, revues techniques, achats et avis, et questions de procédure (« comment démonter… », « dépose… ») qui ne décrivent aucun symptôme.

## Anonymisation

- Les pseudonymes ne sortent jamais du module. Ceux de tous les participants d'une discussion sont remplacés par « [membre] » dans les textes.
- Effacés des textes : adresses e-mail, liens, numéros de téléphone, plaques d'immatriculation et mentions « @ ».

## Limites

- **Licence** : voir plus haut. Jamais publiées ; jeu Kaggle privé seulement. L'écrit des administrateurs reste à archiver.
- **BMW est surreprésenté** (un tiers des discussions) par rapport au parc d'Oran.
- **Le parc est européen et ancien** : les modèles chinois vendus en Algérie sont absents. Pas de darija.
- **Les sections sont larges** : « Moteur » couvre l'alimentation, l'allumage, la distribution… Elles confirment une famille sans en imposer une.
- **Champs de la collecte peu fiables** : `expert_replied` toujours faux ; marque parfois mal remplie sur les sujets généraux. Le module utilise le rang des auteurs à la place.

## Commande

```bash
DALIL_TECHNICONNEXION_AUTORISATION="orale, AAAA-MM-JJ" python data/pipeline/run.py collect --sources techniconnexion --techniconnexion-dir <chemin>/ml_ready
```
