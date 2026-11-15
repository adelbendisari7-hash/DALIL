# Fiche source : Chinese Vehicle Fleet Fault Association Dataset (`cvffad`)

| | |
| --- | --- |
| Producteur | Zheng Y.-J., Mendeley Data, version 1, doi:10.17632/r98g7g6k5t.1 (publié en juin 2026) |
| Accès | API publique Mendeley Data, fichiers `fault_events.csv` et `knowledge_graph_triples.csv` |
| Licence | CC BY 4.0, http://creativecommons.org/licenses/by/4.0 |
| Attribution | Zheng Y.-J., Chinese Vehicle Fleet Fault Association Dataset, Mendeley Data, v1, doi:10.17632/r98g7g6k5t.1 |
| Langue | Chinois |
| Vérifiée le | 14/11/2026 (licence lue dans les métadonnées Mendeley) |

**Ce que la source contient vraiment.** 29 431 événements de panne et 565 triplets d'un graphe de connaissances (symptômes, causes, réparations) pour 35 types de pannes. Les textes d'événements sont **générés par gabarit** (`source = generated`) et portent sur des **flottes de camions, cars et utilitaires de marques anonymisées** (MANUF_xx).

**Conséquence.** La source ne couvre pas les marques chinoises vendues en Algérie (Geely, Chery…), contrairement à ce qu'espérait la section 5. On n'en garde qu'une fiche par type de panne (32 dans le périmètre ; airbag, audio et vitres exclus), marquée `synthetic = true`, jamais utilisée pour l'évaluation.

**Traduction.** Noms des 35 types de pannes traduits et rattachés à la taxonomie à la main (`data/pipeline/sources/cvffad_fr.json`) ; symptômes, causes et réparations traduits par modèle ouvert (chinois vers anglais vers français).

**Piste pour les marques chinoises.** Elle reste ouverte : catalogues des magasins d'Oran, cas réels des mécaniciens partenaires.

**Commande.** `python data/pipeline/run.py all --sources cvffad`.
