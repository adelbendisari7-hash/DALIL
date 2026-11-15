# Fiche source : NHTSA, campagnes de rappel (`nhtsa_recalls`)

| | |
| --- | --- |
| Producteur | U.S. National Highway Traffic Safety Administration |
| Accès | API publique : `https://api.nhtsa.gov/recalls/recallsByVehicle?make=&model=&modelYear=` |
| Licence | Domaine public (gouvernement des États-Unis), https://www.usa.gov/government-copyright |
| Attribution | U.S. National Highway Traffic Safety Administration |
| Langue | Anglais |
| Vérifiée le | 14/11/2026 |

**Contenu.** Résumé, conséquence et remède de chaque campagne, composant touché. Mêmes véhicules que `nhtsa_complaints` ; une campagne couvrant plusieurs années n'est gardée qu'une fois.

**Usage dans DALIL.** Base de connaissances (défauts connus par modèle). Pas d'exemples d'entraînement : un rappel ne décrit pas un symptôme vécu par un conducteur.

**Limites.** Défauts de sécurité seulement. L'API répond 400 quand un véhicule n'a aucun rappel : traité comme une liste vide.

**Commande.** `python data/pipeline/run.py all --sources nhtsa_recalls`.
