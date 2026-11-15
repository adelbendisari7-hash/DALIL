# Fiche source : NHTSA, plaintes des propriétaires (`nhtsa_complaints`)

| | |
| --- | --- |
| Producteur | U.S. National Highway Traffic Safety Administration, Office of Defects Investigation |
| Accès | API publique sans clé : `https://api.nhtsa.gov/complaints/complaintsByVehicle?make=&model=&modelYear=` |
| Licence | Domaine public (gouvernement des États-Unis), https://www.usa.gov/government-copyright |
| Attribution | U.S. National Highway Traffic Safety Administration |
| Langue | Anglais |
| Vérifiée le | 14/11/2026 |

**Contenu.** Récits de pannes écrits par les conducteurs (`summary`), composant déclaré (`components`), date, accident, incendie.

**Périmètre collecté.** Véhicules vendus aux États-Unis et proches du parc algérien (`data/pipeline/sources/nhtsa_vehicles.json`) : Hyundai Accent 2006-2017 (modèle du pilote), Kia Rio 2012-2017, Hyundai Elantra 2011-2016, Fiat 500 2012-2019, Volkswagen Golf 2010-2019 et Jetta 2011-2018. Environ 9 000 plaintes.

**Usage dans DALIL.** Corpus principal « symptôme décrit → pièce » pour l'étape 7 (`data/processed/train/nhtsa_complaints.jsonl`), après traduction en français ; base de connaissances.

**Étiquetage.** Pièce trouvée par mots-clés dans le récit, rapprochée de la famille déclarée par la NHTSA. Une panne type n'est attribuée que si le texte et le composant sont d'accord (`label_quality = keyword+component`).

**Limites.** Marché américain, orienté sécurité, rédigé en anglais ; ni Renault, ni Peugeot, ni Dacia. Étiquettes faibles : à n'utiliser que pour l'entraînement, jamais pour l'évaluation.

**Commande.** `python data/pipeline/run.py all --sources nhtsa_complaints` (réponses brutes en cache dans `data/raw/nhtsa/`).
