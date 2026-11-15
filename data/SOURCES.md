# Registre des sources de données

Règle du projet : **aucune donnée externe n'entre dans le dépôt ou la base sans une ligne ici**,
avec sa licence. `knowledge_chunks.license` est obligatoire en base.

| Source | Fichier / script | Licence | Statut | Remarques |
| --- | --- | --- | --- | --- |
| Fiches de pannes DALIL | `seed/faults.json` | Propriétaire DALIL | En base | Rédigées par l'équipe ; à relire par un mécanicien partenaire |
| Exemples d'amorçage du classifieur | `seed/diagnosis_examples_fr.jsonl` | Propriétaire DALIL | En base / entraînement | **Synthétiques**, rédigés pour valider le code. Ne servent pas à l'évaluation du mémoire |
| Cas de démonstration | `seed/demo_cases.json` | Propriétaire DALIL | Tests | Critère de l'étape 8 ; ne remplacent pas le jeu de test figé d'Oran |
| Codes OBD-II (amorce) | `seed/dtc_fr.json` | Propriétaire DALIL (définitions génériques SAE J2012 reformulées) | En base | 47 codes courants |
| Taxonomie des pièces | `seed/part_categories.json` | Propriétaire DALIL | En base | Synonymes à enrichir (darija en V2) |
| Référentiel véhicules | `seed/vehicles.json` | Propriétaire DALIL | En base | Années et moteurs approximatifs : à confirmer par les 20 magasins enquêtés |
| Communes de la wilaya d'Oran | `seed/geo_oran.json` | Données publiques | En base | Centres approximatifs ; codes internes (pas ONS) |
| Magasins de démonstration | `seed/demo_shops.json` | — | En base (`is_demo`) | **Fictifs**. Purge : `python -m app.seed --purge-demo` |
| OpenStreetMap (`shop=car_parts`, `car_repair`, `tyres`) | `scripts/osm_overpass.py` → `raw/osm_oran.csv` | ODbL — attribution « © contributeurs OpenStreetMap » | Script prêt | Couverture d'Oran à mesurer à la première requête |
| OBDex | `scripts/import_obdex.py` | CC0 | Script prêt | Traduction FR à produire et relire (200 échantillons) |
| NHTSA, plaintes (`nhtsa_complaints`) | `pipeline/sources/nhtsa.py` | Domaine public (US) | Collectée, à traduire | [Fiche](sources/nhtsa_complaints.md). Anglais, marché US ; 6 modèles proches du parc algérien |
| NHTSA, rappels (`nhtsa_recalls`) | `pipeline/sources/nhtsa.py` | Domaine public (US) | Collectée, à traduire | [Fiche](sources/nhtsa_recalls.md) |
| DVSA MOT, Royaume-Uni (`mot_uk`) | `pipeline/sources/mot.py` | Open Government Licence v3.0 | Collectée, en base | [Fiche](sources/mot_uk.md). Données codées : taux d'échec par modèle et famille de pièces |
| RappelConso (`rappelconso`) | `pipeline/sources/rappelconso.py` | Licence Ouverte v2.0 (Etalab) | Collectée, en base | [Fiche](sources/rappelconso.md). Rappels de sécurité en français |
| Stack Exchange Mechanics (`stackexchange_mechanics`) | `pipeline/sources/stackexchange.py` | CC BY-SA 4.0 | Collectée, à traduire | [Fiche](sources/stackexchange_mechanics.md). Export du 31/12/2024, antérieur à juin 2025 |
| CVFFAD, Chine (`cvffad`) | `pipeline/sources/cvffad.py` | CC BY 4.0 | Collectée, à traduire | [Fiche](sources/cvffad.md). **Synthétique** (textes générés, flottes de camions anonymisées) : ne couvre pas les marques chinoises du parc algérien |

Pipeline complet, rejouable : `python data/pipeline/run.py all` (voir `data/processed/report.md`).

## Sources exclues

- **Reddit** (r/AskAMechanic interdit l'usage pour l'IA).
- **Google Maps** : aide à la visite seulement, pas de copie en base.
- **Ouedkniss**, forums (Planète Renault…) : pas de collecte automatique sans accord écrit.
- **TecDoc** : licence commerciale, après levée de fonds.
