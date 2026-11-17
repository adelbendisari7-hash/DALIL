# Plan : référentiel complet des véhicules d'Algérie et nouveaux jeux de données pour le diagnostic

Rédigé le 17/11/2026, à exécuter dans une prochaine session. Il s'appuie sur `docs/etude-marche-algerie.md` (chiffres de l'ONS) et sur les recherches de jeux de données de la section 3.

**Prompt à lancer :**

> Lis `docs/SUIVI.md` puis `docs/plan-referentiel-et-donnees.md`, et réalise les phases A à D dans l'ordre. Pour chaque phase, écris les tests, vérifie le critère de fin, mets à jour le suivi et commite. Arrête-toi et demande-moi avant tout ce que le plan marque « décision ».

## Décisions déjà prises par l'utilisateur (17/11/2026)

La prochaine session les applique sans les redemander.

1. **Suzuki et Lada : oui**, à ajouter au référentiel (Maruti 800, Alto, Swift, Celerio, Jimny ; Lada Niva), marqués `a_verifier`.
2. **Traduction : la meilleure qualité, même si c'est long.** Tout traduire, sans échantillon. Méthode :
   - avant de lancer, comparer sur l'échantillon de relecture de 200 textes (`data/processed/translations/relecture.csv`) le traducteur actuel (MarianMT opus-mt, rapide) et un traducteur plus fort sous licence libre, par exemple MADLAD-400-3B (Apache 2.0) ;
   - critère : moins de termes de pièces mal traduits (`glossary_misses`), relecture d'un échantillon ;
   - garder le meilleur, puis traduire tout le corpus sur Kaggle, sur plusieurs nuits s'il le faut (carnet 01, reprise automatique par le cache) ;
   - écarter NLLB-200, réservé à un usage non commercial (CC BY-NC).
3. **Base européenne des rappels (Safety Gate)** : pas de décision à prendre. Règle : lire ses conditions de réutilisation ; l'ajouter si elles l'autorisent, l'écarter sinon (avec la raison dans `data/SOURCES.md`). Apport modeste : des avis de rappel, pas des descriptions de pannes.
4. **Modèle de langage : viser l'efficacité.** Ré-affiner (C5) sur le jeu régénéré avec la recherche hybride et le corpus élargi, puis mesurer la chaîne avec et sans lui, sur les jeux dev et démo.
   - **Ne le réactiver par défaut que s'il améliore le top-1 sans dégrader le top-3 ni le refus des hors-sujet, et en restant sous 10 s.**
   - S'il est trop lent sur processeur, essayer d'abord : un message plus court (2 passages au lieu de 5), une réponse limitée au classement, la quantification Q4_K_M.
   - Sinon, le garder pour le mémoire uniquement.

## 0. Objectifs et critères de fin

| Objectif | Critère de fin vérifiable |
| --- | --- |
| A. Référentiel couvrant le parc algérien | Toutes les marques du tableau 7 de l'ONS (plus de 0,15 % du parc) présentes, ainsi que les modèles de la section 1 ; années depuis 1980 ; chaque variante porte sa source et `a_verifier` |
| B. Saisie d'un véhicule absent | Un utilisateur dont le véhicule manque peut le saisir ; la saisie est enregistrée et visible dans Indicateurs |
| C. Données d'entraînement élargies | Au moins 3 nouvelles sources sous licence dans `data/SOURCES.md` ; corpus d'entraînement multiplié par 3 ou plus (aujourd'hui 8 934 exemples) |
| D. Diagnostic tenant compte du véhicule et réentraîné | Jeux dev et démo : top-1 et top-3 au moins égaux à aujourd'hui (dev 90 / 96 %, démo 88 / 100 % en mode hybride) ; hors sujet 100 % refusé ; moins de 10 s |

Règles du projet qui s'appliquent :
- aucune donnée sans licence ;
- jamais d'invention : une variante non confirmée est marquée `a_verifier` ;
- le jeu de test d'Oran ne sert jamais à entraîner ;
- chaque script de données est rejouable et testé.

## 1. Phase A : référentiel des véhicules

### A1. Modèles à ajouter

Priorité d'après le parc ONS 2020 (tableau 7). Le **gras** marque ce qui manque aujourd'hui ; les modèles déjà présents sont entre parenthèses.

| Marque (part du parc) | Modèles à couvrir |
| --- | --- |
| Peugeot (17,4 %) | (206, 208, 301) **104, 204, 304, 404, 504, 505, 205, 305, 309, 405, 306, 406, 407, 307, 308, 206+, 207, 2008, 3008, 5008, 508** ; utilitaires **Partner, Bipper, Expert, Boxer, J5, J9** |
| Renault (17,0 %) | (Symbol, Clio, Kangoo) **R4, R5, R9, R11, R12, R18, R19, R21, R25, Clio 1 à 5 (générations distinctes), Mégane 1 à 4, Scénic, Laguna, Fluence, Captur, Talisman** ; utilitaires **Express, Trafic, Master** |
| Volkswagen (4,9 %) | (Golf, Polo, T-Roc) **Golf 1 à 8 (générations), Jetta, Passat, Caddy, Transporter, Tiguan, Touareg, Tharu, T-Cross** |
| Toyota (4,3 %) | (Hilux) **Corolla, Yaris, Starlet, Carina, RAV4, Land Cruiser, Prado, Hiace, Dyna** |
| Hyundai (4,3 %) | (Accent, i10) **Atos, Getz, Grand i10, i20, Elantra, Tucson, Creta, Santa Fe, H-1, H-100, HD (camions)** |
| Dacia (3,8 %) | (Logan, Sandero, Duster) **Logan MCV, Lodgy, Dokker** |
| Fiat (2,9 %) | (Tipo, 500, Doblò) **127, 128, Uno, Punto, Palio, Siena, Albea, Fiorino, Ducato, Grande Panda** |
| **Chevrolet (2,0 %)** | **Aveo, Spark, Optra, Lacetti, Sail, Cruze, Captiva** |
| **Citroën (1,8 %)** | **2CV, BX, ZX, Saxo, Xsara, C3, C4, C-Élysée, C15, Berlingo, Jumpy, Jumper** |
| **Mazda (1,4 %)** | **323, 626, 3, 6, B2500, BT-50** |
| **Mitsubishi (1,0 %, 4,9 % des transactions)** | **L200, Pajero, Lancer, Colt, Canter** |
| **Ford (0,95 %)** | **Fiesta, Focus, Escort, Transit, Ranger** |
| **Mercedes (0,95 %)** | **190, Classe C, Classe E, Vito, Sprinter** |
| **Seat (0,91 %)** | **Ibiza, León, Cordoba, Toledo, Arona** |
| **Daewoo (0,88 %)** | **Matiz, Lanos, Nubira, Cielo** |
| **Honda (0,87 %)** | **Civic, Accord, CR-V** |
| **Nissan (0,82 %)** | **Sunny, Almera, Micra, Qashqai, Navara, Pick-up, Patrol** |
| Kia (0,60 %) | (Picanto, Rio) **Cerato, Sportage, Sorento, Carens, K2700** |
| **Audi, BMW, Land Rover** | **A3, A4, A6 ; Série 3, Série 5 ; Defender, Discovery** |
| Opel (0,18 %) | (Corsa) **Astra, Vectra, Combo** |
| Skoda | (Octavia) **Fabia, Superb** |
| **Isuzu** | **D-Max, NKR, NPR (camions)** |
| **Suzuki, Lada** (dans « Autres », 25,5 %) | **Maruti 800, Alto, Swift, Celerio, Jimny ; Lada Niva** (ajout validé le 17/11/2026, `a_verifier`) |
| Marques chinoises (forte hausse 2023-2026) | (Geely Coolray, Chery Tiggo 4, MG5, Jetour X70, DFSK Glory 580) **Chery QQ, Tiggo 2, 3, 7, 8, Arrizo 5 ; Geely Emgrand, GX3 Pro ; JAC J7, S3, T6 ; Great Wall Wingle (pick-up) ; Haval H6 ; BAIC ; GAC GS3, GS4 ; Changan ; MG ZS, HS ; BYD ; DFSK K01 ; Jetour Dashing** |

Les utilitaires et les camions comptent : 18 % du parc sont des camionnettes. Il faut un champ `genre` (tourisme, utilitaire, camion) pour filtrer l'affichage.

### A2. Méthode (rejouable, sans rien inventer)

1. **Liste candidate depuis Wikidata (licence CC0).** Écrire `data/scripts/wikidata_models.py`. Il lance une requête SPARQL sur les modèles d'automobile de chaque marque :
   - classe Q3231690 « modèle d'automobile » et sous-classes ;
   - propriétés P176 (constructeur) et P571 / P2031 / P2032 (début et fin de production) ;
   - P279 / P155 / P156 pour les générations.

   Le script écrit `data/raw/wikidata_models.csv` (marque, modèle, génération, années, identifiant Q) et ajoute une ligne à `data/SOURCES.md`.
2. **Fusion relue.** Écrire `data/scripts/build_vehicles.py`, qui produit `data/seed/vehicles.json` à partir de trois choses : la liste A1 (ce qu'on garde), les années Wikidata, et les motorisations courantes en Algérie (A3). Chaque variante porte `source` (`wikidata:Qxxx`, `equipe`, `magasin:Gx`) et `a_verifier: true` tant qu'un magasin ne l'a pas confirmée. Les variantes déjà en base gardent leur identifiant : mise à jour en place, comme pour les fiches de pannes, pour ne pas casser les produits ni les compatibilités.
3. **Contrôles automatiques** (tests) :
   - noms de marque et de modèle uniques ;
   - années cohérentes (début avant fin, depuis 1960) ;
   - toutes les marques ONS de plus de 0,15 % présentes ;
   - aucune variante sans `source` ;
   - après un nouveau chargement, les identifiants des variantes existantes sont inchangés.

### A3. Motorisations

Ne lister que les motorisations courantes, celles que les magasins vendent. Par exemple :
- **Peugeot et Citroën** : essence TU (1.1, 1.4, 1.6), EW (1.8, 2.0), PureTech ; diesel XUD (1.9 D), DW (1.9 / 2.0 HDi), DV (1.4 / 1.6 HDi).
- **Renault et Dacia** : essence D7F 1.2, K7J / K7M 1.4 / 1.6, H4M 1.6 SCe ; diesel F8Q 1.9 D, K9K 1.5 dCi, F9Q 1.9 dCi.
- **Volkswagen** : 1.6 essence, 1.9 TDI, 2.0 TDI, 1.4 TSI.
- **Toyota** : 2.5 / 3.0 D-4D, 1.3 / 1.6 VVT-i.
- **Hyundai et Kia** : 1.1 / 1.2 Epsilon / Kappa, 1.4 / 1.6 Gamma, 1.5 / 1.6 CRDi.

Les autres marques : une motorisation générique « essence » ou « diesel » par génération, marquée `a_verifier`. Source de confirmation : la question « vos 10 modèles et motorisations les plus demandés », ajoutée à la fiche magasin de `docs/essais-oran.md`.

### A4. Interface

1. **Années.** La liste des années commence à 1980 ou plus tôt, toujours bornée au modèle choisi (déjà en place).
2. **Recherche par saisie.** Avec environ 300 modèles, les listes déroulantes deviennent longues : ajouter une recherche par saisie (« Clio 2 »).
3. **Véhicule absent.** Lien « Mon véhicule n'est pas dans la liste », avec marque, modèle, année et motorisation en texte libre.
   - Enregistré dans une nouvelle table `vehicle_requests`. Migration `0003`.
   - Le diagnostic fonctionne alors sans véhicule.
   - Compteur dans Indicateurs, pour savoir quoi ajouter ensuite.
4. **Indicateurs.** Ajouter « véhicules les plus diagnostiqués » (par marque et modèle) et « véhicules demandés absents ».
5. **Tests.**
   - e2e : choisir une Peugeot 405 de 1992, puis saisir un véhicule absent.
   - Backend : la nouvelle table et les indicateurs.

## 2. Phase B : collecte des nouvelles données

Pour chaque source :
- un module dans `data/pipeline/sources/` (skill de projet `ajouter-source-donnees`) ;
- une fiche dans `data/sources/<id>.md` ;
- une ligne dans `data/SOURCES.md` ;
- un test sans réseau.

| Priorité | Source | Licence | Ce qu'elle apporte | Travail |
| --- | --- | --- | --- | --- |
| 1 | **DVSA MOT, Royaume-Uni** (déjà branchée, 18 modèles) | Open Government Licence v3.0 | Taux d'échec au contrôle technique par modèle, année et famille de pièce. Le Royaume-Uni a la plupart des modèles européens et asiatiques d'Algérie : Peugeot, Renault, Citroën, Dacia, VW, Toyota, Hyundai, Kia, Chevrolet Aveo / Spark / Captiva, Mitsubishi L200, Nissan, Mazda, Fiat, Seat, Skoda, MG, Suzuki | Étendre `TARGETS` de `pipeline/sources/mot.py` à tous les modèles A1 vendus au Royaume-Uni (correspondances Opel = Vauxhall). Lire aussi les fichiers « failure item », qui donnent le détail des défauts, et les tables de libellés. Traduire les quelque 2 000 libellés standard de défauts une fois (`translate.py`). **Sortie** : `priors/mot_*.csv`, soit P(famille de pièce \| modèle, âge) |
| 2 | **NHTSA, plaintes, États-Unis** (déjà branchée, 6 modèles) | Domaine public | Récits de pannes en texte libre, étiquetés par composant. Modèles en commun avec l'Algérie : Toyota Corolla, Yaris, RAV4, Tacoma (proche du Hilux) ; Hyundai Accent, Elantra, Tucson, Santa Fe ; Kia Rio, Forte (Cerato), Sportage, Sorento ; Chevrolet Aveo, Spark, Cruze ; Mitsubishi Lancer, Outlander, Mirage ; Mazda 3, 6 ; VW Golf, Jetta, Passat, Tiguan ; Nissan Sentra (Sunny), Versa, Frontier (Navara) ; Fiat 500 ; Honda Civic, Accord ; Ford Focus, Fiesta, Ranger | Compléter `pipeline/sources/nhtsa_vehicles.json`. Viser **40 000 à 60 000 plaintes** (aujourd'hui 8 999). Traduction complète, avec le meilleur traducteur mesuré (décision 2) |
| 3 | **NHTSA vPIC** | Domaine public | Motorisations et années des modèles vendus aux États-Unis | Contrôle croisé des motorisations A3 pour les modèles communs |
| 4 | **Wikidata** | CC0 1.0 | Modèles, générations, années de production | Phase A2 |
| 5 | **RappelConso, France** (déjà branchée) | Licence Ouverte 2.0 | Rappels Peugeot, Renault, Citroën et Dacia en français | Vérifier que toutes les marques A1 sont prises (pas de filtre de modèle) |
| 6 | **Transport Canada, rappels** | Licence du gouvernement ouvert, Canada (attribution « Contains information licensed under the Open Government Licence – Canada ») | Rappels en anglais et en français (Canada bilingue) | Nouveau module `transport_canada`. Vérifier sur open.canada.ca la licence et la présence d'un texte français. Les plaintes canadiennes ne sont **pas** publiques |
| 7 | **EU Safety Gate**, catégorie véhicules à moteur | Documents de la Commission en CC BY 4.0 ; **conditions de la base à vérifier** | Rappels européens, dont modèles français et chinois | Règle de la décision 3 |
| 8 | **Zenodo, Automotive Faults Dataset** (2025) | CC BY 4.0 | Pannes, symptômes, procédures (61 ko, petit) | Lire le contenu ; si ce sont de vrais cas, l'ajouter aux fiches de référence |
| 9 | **Forums auto francophones** (forum Caradisiac, Auto-Évasion, forum-auto, fiches-auto) | Droit d'auteur des membres : **autorisation écrite nécessaire** | Le meilleur texte français symptôme → panne, sur Peugeot et Renault | Rédiger les demandes (projet universitaire, usage non commercial, anonymisation, citation). **Décision** : l'utilisateur envoie les demandes |
| 10 | **Données propres à DALIL** | Consentement de l'utilisateur, déjà recueilli | Diagnostics réels d'Oran avec la réponse « diagnostic juste ? » ; saisies « véhicule absent » | Script d'export anonymisé : texte, véhicule, réponse, sans téléphone. Ne garder pour l'entraînement que les cas confirmés. **Jamais** les cas du jeu de test d'Oran |
| 11 | **Reformulations synthétiques** des fiches DALIL, par un modèle de langage, en français et en darija en lettres latines | Propriétaire DALIL | Variété de formulations sur les modèles et pannes peu couverts | Marquées `synthetic: true`, pour l'entraînement seulement, jamais pour le test. Mesurer l'effet avant de les garder |

**Écartés, avec la raison** (à recopier dans `data/SOURCES.md`) :
- **Ouedkniss** : CGU, article 9, extraction interdite.
- **Google Maps** : CGU.
- **Reddit** : conditions de l'API pour l'entraînement.
- **Groupes Facebook** : vie privée et CGU.
- **CJJones/Vehicle_Diagnostics_LLM_Training_Sample sur Hugging Face** : synthétique et non commercial (CC BY-NC 4.0).
- **UTAC-OTC, contrôle technique français** : pas de données ouvertes par modèle (avis CADA 20165168).
- **ADAC Pannenstatistik** : licence de réutilisation inconnue. Possible plus tard comme simple référence citée, pas comme données d'entraînement.
- **Jeux de sons ou de capteurs (Kaggle)** : autre modalité, hors du périmètre de la V1.

## 3. Phase C : apprentissage

1. **Rejouer le pipeline** : `python data/pipeline/run.py all`, traduction des nouveaux textes sur Kaggle (carnet 01), puis chargement.
2. **Tenir compte du véhicule** (nouveauté). Les a priori P(famille de pièce \| modèle, âge) issus du MOT deviennent un 4ᵉ signal du mélange dans `pipeline.py`, à côté du classifieur, de la recherche et des codes OBD.
   - Poids réglé sur le jeu dev uniquement.
   - Exemple : une Peugeot 206 de 15 ans a plus de chances d'avoir des rotules et des silentblocs à changer que des plaquettes.
   - Tests sur un a priori factice.
3. **Réentraîner le classifieur** : `python ml/train_baseline.py --target part --corpus`, avec le corpus élargi. Comparer A seul et A avec a priori véhicule.
4. **Vecteurs de recherche** : recalculer sur Kaggle (carnet 05) pour les nouveaux passages ; la réparation automatique de `DenseIndex` ne couvre que les fiches DALIL.
5. **Modèle de langage** (décision 4) : régénérer `ml/build_llm_dataset.py` avec la recherche hybride et le corpus élargi, ré-affiner (carnets 03 et 04, environ 4 h sur Kaggle), mesurer, et ne réactiver que si la règle de la décision 4 est remplie.
6. **Mesurer** : `ml/evaluate.py` en mode mots-clés et hybride, sur les jeux dev et démo, puis sur le jeu d'Oran quand il existera. Critère D de la section 0. Résultats dans `ml/README.md`.

## 4. Phase D : documentation et clôture

- Mettre à jour :
  - `docs/etude-marche-algerie.md` (couverture atteinte) ;
  - `data/SOURCES.md` ;
  - `ml/README.md` ;
  - `docs/SUIVI.md` (état, décisions, journal) ;
  - le graphe (`graphify update .`).
- Ajouter à la fiche magasin de `docs/essais-oran.md` la question « vos 10 modèles et 10 pièces les plus demandés », qui servira à confirmer les `a_verifier`.
- Commit par phase.

## 5. Ordre et volume estimé

| Ordre | Travail | Durée indicative | Dépend de |
| --- | --- | --- | --- |
| 1 | A2 Wikidata, puis A1 à A3 référentiel et tests | 1 session | rien |
| 2 | A4 interface (recherche, véhicule absent, indicateurs) | une demi-session | 1 |
| 3 | B1 MOT étendu, B2 NHTSA étendu, B3 vPIC | 1 session, plus les téléchargements (MOT : plusieurs Go en flux) | 1 (noms de modèles) |
| 4 | Traduction sur Kaggle | 3 à 6 h de calcul (GPU, nuit possible) | 3 |
| 5 | B5 à B8 rappels et petits jeux | une demi-session | rien |
| 6 | C1 à C4 et C6 apprentissage et mesures | 1 session (+ carnet 05 sur Kaggle) | 3, 4 |
| 7 | B9 demandes aux forums, B10 export DALIL, B11 synthétique | au fil de l'eau | réponses et usage réel |

## 6. Sources consultées pour ce plan

- ONS, [Parc national automobile au 31/12/2020](https://www.ons.dz/IMG/pdf/i.parc_nat31_12_2020.pdf).
- Wikidata, [licence CC0](https://www.wikidata.org/wiki/Wikidata:Licensing) ; [exemple d'extraction de modèles d'automobiles](https://neworange.biolab.si/blog/how-to-get-data-from-wikidata/).
- DVSA, [Anonymised MOT tests and results](https://www.data.gov.uk/dataset/c63fca52-ae4c-4b75-bab5-8b4735e1a4c9/anonymised-mot-tests-and-results) ; [guide utilisateur v5.1](https://data.dft.gov.uk/anonymised-mot-test/test_data/mot-testing-data-user-guide-v5.1.odt) ; [portail DVSA](https://open.data.dvsa.gov.uk/mot-anonymised/index.html).
- Transport Canada, [Vehicle Recalls Database](https://open.canada.ca/data/en/dataset/1ec92326-47ef-4110-b7ca-959fab03f96d) ; [rappels des 60 derniers jours](https://open.canada.ca/data/en/dataset/1991fef6-9dfe-40e2-a0c6-19c60ddf4a02).
- Commission européenne, Safety Gate (licence des rapports : décision 2011/833/UE, CC BY 4.0) ; suivi tiers [car-recalls.eu](https://car-recalls.eu/2025-safety-gate-recalls-overall-table/).
- Zenodo, [Automotive Faults Dataset for Diagnostic and Maintenance Systems](https://zenodo.org/records/15626055) (CC BY 4.0).
- Hugging Face, [CJJones/Vehicle_Diagnostics_LLM_Training_Sample](https://huggingface.co/datasets/CJJones/Vehicle_Diagnostics_LLM_Training_Sample) (écarté : synthétique, CC BY-NC).
- Kaggle, [Car Diagnostics Dataset](https://www.kaggle.com/datasets/malakragaie/car-diagnostics-dataset) (sons, hors périmètre).
- CADA, [avis 20165168](https://cada.data.gouv.fr/20165168/) (données UTAC-OTC non ouvertes) ; UTAC, [bilan annuel 2020](https://www.utac-otc.com/Bilan%20Annuel/Historique/document_integral_VL_2020.pdf).
- ADAC, [Pannenstatistik 2020](https://assets.adac.de/image/upload/v1618933216/ADAC-eV/KOR/Text/PDF/Pannenstatistik_2020_m0cnee.pdf) (licence non vérifiée).
- Ouedkniss, [CGU, article 9](https://www.ouedkniss.com/terms?lang=fr).
