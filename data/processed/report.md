# Rapport du pipeline de données (étape 6)

Généré le 2026-11-24 08:18 UTC par `python data/pipeline/run.py report`.

| Source | Licence | Enregistrements | Reliés à une famille | À une sous-famille | À une panne type | Traduits / en français |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| NHTSA – plaintes des propriétaires (ODI Complaints) | Domaine public (gouvernement des États-Unis) | 8999 | 6878 (76 %) | 3012 (33 %) | 1210 (13 %) | 8999 (100 %) |
| NHTSA – campagnes de rappel | Domaine public (gouvernement des États-Unis) | 65 | 43 (66 %) | 31 (47 %) | 0 (0 %) | 65 (100 %) |
| RappelConso – rappels automobiles (DGCCRF) | Licence Ouverte v2.0 (Etalab) | 1827 | 1113 (60 %) | 612 (33 %) | 0 (0 %) | 1827 (100 %) |
| DVSA – contrôle technique britannique (MOT anonymisé) | Open Government Licence v3.0 | 18 | 18 (100 %) | 18 (100 %) | 0 (0 %) | 18 (100 %) |
| Stack Exchange – Motor Vehicle Maintenance & Repair (export 2024-12-31) | CC BY-SA 4.0 | 8102 | 5604 (69 %) | 5604 (69 %) | 1590 (19 %) | 8102 (100 %) |
| Chinese Vehicle Fleet Fault Association Dataset (Mendeley Data, v1) (synthétique) | CC BY 4.0 | 32 | 32 (100 %) | 28 (87 %) | 17 (53 %) | 32 (100 %) |
| Forum L'Argus – Panne auto, mécanique et entretien (collecte de l'équipe) | Accord de L'Argus (DALIL_LARGUS_AUTORISATION) | 99720 | 76510 (76 %) | 71368 (71 %) | 866 (0 %) | 99720 (100 %) |

Les étiquettes sont obtenues par mots-clés (voir `data/pipeline/taxonomy_map.py`) : elles servent à l'entraînement, jamais à l'évaluation, qui se fait sur le jeu de test d'Oran annoté par des mécaniciens.
