# Fiche source : RappelConso, rappels automobiles (`rappelconso`)

| | |
| --- | --- |
| Producteur | DGCCRF, plateforme RappelConso |
| Accès | data.economie.gouv.fr, jeu `rappelconso-v2-gtin-espaces`, rubrique « automobiles, motos, scooters » (export JSON complet) |
| Licence | Licence Ouverte v2.0 (Etalab), https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf |
| Attribution | DGCCRF, RappelConso (data.economie.gouv.fr) |
| Langue | Français |
| Vérifiée le | 14/11/2026 (licence lue dans les métadonnées du catalogue) |

**Contenu.** Environ 1 800 fiches : marque, modèles, motif du rappel, risques, lien vers la fiche officielle.

**Usage dans DALIL.** Base de connaissances, indexée immédiatement car déjà en français. Pas d'exemples d'entraînement : ce sont des rappels, pas des symptômes.

**Étiquetage.** Synonymes français de la taxonomie et familles (frein, carburant, direction…). Ceintures, airbags, sièges et serrures restent sans famille : ils sont hors taxonomie.

**Limites.** Défauts de sécurité seulement ; motos incluses ; certaines fiches sont des traductions automatiques de rappels étrangers (« extrémités de tige de voie » pour rotules de direction).

**Commande.** `python data/pipeline/run.py all --sources rappelconso`.
