# Registre des sources de données

Règle du projet : **aucune donnée externe n'entre dans le dépôt ou la base sans une ligne ici**,
avec sa licence. `knowledge_chunks.license` est obligatoire en base.

| Source | Fichier / script | Licence | Statut | Remarques |
| --- | --- | --- | --- | --- |
| Fiches de pannes DALIL | `seed/faults.json` | Propriétaire DALIL | En base | Rédigées par l'équipe ; à relire par un mécanicien partenaire |
| Exemples d'amorçage du classifieur | `seed/diagnosis_examples_fr.jsonl` | Propriétaire DALIL | En base / entraînement | **Synthétiques**, rédigés pour valider le code (428 depuis le 18/11/2026, au moins 9 par panne, registres variés). Ne servent pas à l'évaluation du mémoire |
| Lexique darija → français | `backend/app/services/diagnosis/darija.py` | Propriétaire DALIL | En production | Rédigé par l'équipe le 18/11/2026 (lettres latines et arabes). **À faire relire et enrichir par des locuteurs d'Oran** |
| Cas de démonstration | `seed/demo_cases.json` | Propriétaire DALIL | Tests | Critère de l'étape 8 ; ne remplacent pas le jeu de test figé d'Oran |
| Codes OBD-II (amorce) | `seed/dtc_fr.json` | Propriétaire DALIL (définitions génériques SAE J2012 reformulées) | En base | 47 codes courants |
| Taxonomie des pièces | `seed/part_categories.json` | Propriétaire DALIL | En base | Synonymes à enrichir (darija en V2) |
| Référentiel véhicules | `seed/vehicles.json` (construit par `scripts/build_vehicles.py`) | Propriétaire DALIL | En base | 44 marques, 260 modèles, 467 motorisations depuis le 18/11/2026 : modèles initiaux de l'équipe, modèles d'au moins 100 annonces Ouedkniss (motorisations et années observées dans les annonces), utilitaires et modèles anciens de l'ONS. Entrées `a_verifier` à confirmer par les magasins enquêtés |
| Statistiques de marché Ouedkniss | `market/ouedkniss_modeles.json` (`scripts/ouedkniss_stats.py`) | Agrégats d'une collecte sous autorisation déclarée (voir la ligne Ouedkniss) | Dépôt | Nombre d'annonces par modèle (Algérie, Oran), années, motorisations citées. Aucune annonce individuelle |
| Communes de la wilaya d'Oran | `seed/geo_oran.json` | Données publiques | En base | Centres approximatifs ; codes internes (pas ONS) |
| Magasins de démonstration | `seed/demo_shops.json` | — | En base (`is_demo`) | **Fictifs**. Purge : `python -m app.seed --purge-demo` |
| OpenStreetMap (`shop=car_parts`, `car_repair`, `tyres`) | `scripts/osm_overpass.py` → `raw/osm_oran.csv` | ODbL — attribution « © contributeurs OpenStreetMap » | Collecté le 17/11/2026 (non importé) | Wilaya d'Oran : 62 lieux (23 magasins de pièces, 33 garages, 6 pneus), 11 avec téléphone. Liste de visite, pas un annuaire. Redistribuer la base des magasins imposerait l'ODbL à sa partie OSM |
| ONS, parc national automobile au 31/12/2020 et immatriculations du 2e semestre 2019 | `market/ons_parc_2020.json` | Publication statistique publique de l'ONS, reprise avec citation de la source | Recopié le 17/11/2026 | Chiffres agrégés seulement (marques, âge, énergie, wilaya d'Oran). Sert à prioriser le référentiel véhicules : `docs/etude-marche-algerie.md` |
| Forum L'Argus, pannes (`largus_forum`) | `pipeline/sources/largus.py` ← base SQLite de la collecte de l'équipe (hors dépôt) | Accord de L'Argus (DALIL_LARGUS_AUTORISATION) : **à confirmer par écrit** ; pas de licence ouverte | Module prêt et testé ; collecte en cours (fin prévue vers le 20/11/2026) | [Fiche](sources/largus_forum.md). Auteurs anonymisés ; texte = question seule ; étiquette par la solution, les réponses ou la question (`label_quality`) |
| Ouedkniss (annonces de vente de voitures) | collecte de l'utilisateur, hors dépôt : `Desktop/WebScraping/output/` ; anonymisée par `scripts/anonymiser_ouedkniss.py` → `output/ouedkniss_anonymise/` | CGU, article 9 : extraction soumise à « autorisation, écrite, préalable ». **Autorisation déclarée par l'utilisateur le 18/11/2026 (accord oral) ; confirmation écrite à obtenir et à archiver** | Collectée le 18/11/2026 (246 617 annonces), anonymisée | Champs vendeur retirés (identifiant, pseudonyme, lien, photo), identifiant d'annonce remplacé par une empreinte, 394 numéros, 3 e-mails, 24 liens, 14 comptes masqués dans les textes. Usage : **statistiques agrégées seulement** (référentiel véhicules), jamais d'annonce individuelle dans DALIL. Fichiers bruts à supprimer par l'utilisateur |
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
