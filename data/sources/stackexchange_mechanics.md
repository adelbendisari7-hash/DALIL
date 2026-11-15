# Fiche source : Stack Exchange, Motor Vehicle Maintenance & Repair (`stackexchange_mechanics`)

| | |
| --- | --- |
| Producteur | Communauté mechanics.stackexchange.com |
| Accès | Internet Archive, export du 31/12/2024 : `stackexchange_20241231/mechanics.stackexchange.com.7z` (68 Mo) |
| Licence | CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/ |
| Attribution | Par enregistrement : nom de l'auteur, lien vers la question, mention « traduit et abrégé » |
| Langue | Anglais |
| Vérifiée le | 14/11/2026 |

**Pourquoi cet export.** Les exports publiés depuis juin 2025 contiennent des données volontairement altérées (section 5 du cahier des charges).

**Contenu.** Questions avec réponse acceptée et score positif (environ 8 100), réponse acceptée, étiquettes.

**Étiquetage.** La pièce est cherchée d'abord dans la réponse acceptée (elle nomme la cause), puis dans les étiquettes, puis dans la question. Une question n'est « diagnostique » que si elle décrit un symptôme et n'est pas une procédure (« How to… ») : seules ces questions, environ 2 400, vont dans les exemples d'entraînement.

**Partage à l'identique.** Les textes dérivés (traductions) restent sous CC BY-SA 4.0. Toute republication de passages garde la licence et l'attribution.

**Commande.** `python data/pipeline/run.py all --sources stackexchange_mechanics`.
