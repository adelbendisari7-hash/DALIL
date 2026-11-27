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
| OpenStreetMap (`shop=car_parts`, `car_repair`, `tyres`) | `scripts/osm_overpass.py` → `raw/osm_oran.csv` | ODbL — attribution « © contributeurs OpenStreetMap » | Collecté le 17/11/2026 ; vérifié identique et importé le 18/11/2026 en 62 brouillons (`python -m app.import_osm`), liste de visite `data/terrain/liste_visite_osm.xlsx` | Wilaya d'Oran : 62 lieux (23 magasins de pièces, 33 garages, 6 pneus), 11 avec téléphone. Liste de visite, pas un annuaire. Redistribuer la base des magasins imposerait l'ODbL à sa partie OSM |
| OpenStreetMap, recherche d'adresse (Nominatim) | `backend/app/services/shop_onboarding.py` (`GET /geo/geocode`, comptes connectés) | ODbL — attribution « © contributeurs OpenStreetMap » ; règles d'usage de Nominatim respectées (une requête par seconde au plus, identifiant d'application, résultats gardés en mémoire) | Depuis le 27/11/2026 (inscription des magasins) | Seule l'adresse tapée par un magasin est envoyée, limitée à la wilaya d'Oran ; aucune donnée sur l'utilisateur. Rien n'est stocké hors de la fiche du magasin (position choisie par lui) |
| ONS, parc national automobile au 31/12/2020 et immatriculations du 2e semestre 2019 | `market/ons_parc_2020.json` | Publication statistique publique de l'ONS, reprise avec citation de la source | Recopié le 17/11/2026 | Chiffres agrégés seulement (marques, âge, énergie, wilaya d'Oran). Sert à prioriser le référentiel véhicules : `docs/etude-marche-algerie.md` |
| Forum Techniconnexion (`techniconnexion`) | `pipeline/sources/techniconnexion.py` ← fichiers JSONL de la collecte de l'équipe (hors dépôt) | Accord des administrateurs de Techniconnexion (DALIL_TECHNICONNEXION_AUTORISATION) : **accord déclaré par l'utilisateur le 27/11/2026 (usage par des modèles d'IA compris), écrit à obtenir** ; aucune licence, `robots.txt` « ai-train=no » ; jeu Kaggle privé | Collecte terminée (30 421 discussions, 276 179 messages) ; lue le 27/11/2026 | [Fiche](sources/techniconnexion.md). Citations, mentions du forum et sujets hors panne retirés ; auteurs anonymisés ; données hors git |
| Forum L'Argus, pannes (`largus_forum`) | `pipeline/sources/largus.py` ← base SQLite de la collecte de l'équipe (hors dépôt) | Accord de L'Argus (DALIL_LARGUS_AUTORISATION) : **accord déclaré par l'utilisateur le 24/11/2026, confirmation écrite à archiver** ; pas de licence ouverte | Collecte terminée (99 779 discussions, 400 801 messages) ; module corrigé sur la vraie base et lu le 24/11/2026 | [Fiche](sources/largus_forum.md). Auteurs anonymisés ; texte = question seule ; étiquette par la solution, les réponses ou la question (`label_quality`) |
| Ouedkniss (annonces de vente de voitures) | collecte de l'utilisateur, hors dépôt : `Desktop/WebScraping/output/` ; anonymisée par `scripts/anonymiser_ouedkniss.py` → `output/ouedkniss_anonymise/` | CGU, article 9 : extraction soumise à « autorisation, écrite, préalable ». **Autorisation déclarée par l'utilisateur le 18/11/2026 (accord oral) ; confirmation écrite à obtenir et à archiver** | Collectée le 18/11/2026 (246 617 annonces), anonymisée | Champs vendeur retirés (identifiant, pseudonyme, lien, photo), identifiant d'annonce remplacé par une empreinte, 394 numéros, 3 e-mails, 24 liens, 14 comptes masqués dans les textes. Usage : **statistiques agrégées seulement** (référentiel véhicules), jamais d'annonce individuelle dans DALIL. Fichiers bruts à supprimer par l'utilisateur |
| OBDex | `scripts/import_obdex.py` | CC0 | Script prêt | Traduction FR à produire et relire (200 échantillons) |
| NHTSA, plaintes (`nhtsa_complaints`) | `pipeline/sources/nhtsa.py` | Domaine public (US) | Collectée, à traduire | [Fiche](sources/nhtsa_complaints.md). Anglais, marché US ; 6 modèles proches du parc algérien |
| NHTSA, rappels (`nhtsa_recalls`) | `pipeline/sources/nhtsa.py` | Domaine public (US) | Collectée, à traduire | [Fiche](sources/nhtsa_recalls.md) |
| DVSA MOT, Royaume-Uni (`mot_uk`) | `pipeline/sources/mot.py` | Open Government Licence v3.0 | Collectée, en base | [Fiche](sources/mot_uk.md). Données codées : taux d'échec par modèle et famille de pièces |
| RappelConso (`rappelconso`) | `pipeline/sources/rappelconso.py` | Licence Ouverte v2.0 (Etalab) | Collectée, en base | [Fiche](sources/rappelconso.md). Rappels de sécurité en français ; depuis le 28/11/2026, aussi montrés au client pour le modèle de ses voitures (« rappel possible », source citée, lien vers la fiche officielle) |
| Stack Exchange Mechanics (`stackexchange_mechanics`) | `pipeline/sources/stackexchange.py` | CC BY-SA 4.0 | Collectée, à traduire | [Fiche](sources/stackexchange_mechanics.md). Export du 31/12/2024, antérieur à juin 2025 |
| CVFFAD, Chine (`cvffad`) | `pipeline/sources/cvffad.py` | CC BY 4.0 | Collectée, à traduire | [Fiche](sources/cvffad.md). **Synthétique** (textes générés, flottes de camions anonymisées) : ne couvre pas les marques chinoises du parc algérien |

Pipeline complet, rejouable : `python data/pipeline/run.py all` (voir `data/processed/report.md`).

## Sources exclues

- **Reddit** (r/AskAMechanic interdit l'usage pour l'IA).
- **Google Maps** : aide à la visite seulement, pas de copie en base.
- **Ouedkniss**, forums (Planète Renault…) : pas de collecte automatique sans accord écrit.
- **TecDoc** : licence commerciale, après levée de fonds.
