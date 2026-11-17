# Le marché automobile algérien : ce qu'il implique pour DALIL

Étude documentaire du 17/11/2026. Elle sert à décider quels véhicules et quelles pièces DALIL doit couvrir en priorité. Les chiffres viennent de sources publiques citées en fin de document. Les chiffres officiels sont recopiés dans `data/market/ons_parc_2020.json`.

**Méthode.**
- Statistiques officielles de l'ONS (parc au 31/12/2020, le dernier bulletin détaillé publié), presse économique algérienne, communiqués des constructeurs.
- Les annonces d'Ouedkniss n'ont **pas** été extraites : l'article 9 de leurs CGU l'interdit sans autorisation écrite (voir `data/SOURCES.md`).
- **Limite principale :** l'ONS publie les chiffres par marque, pas par modèle. Le classement par modèle reste à établir en magasin (section 5).

## 1. Le parc : vieux, français, et de plus en plus diesel à la revente

| Constat (ONS, fin 2020) | Chiffre | Conséquence pour DALIL |
| --- | --- | --- |
| Véhicules en circulation | 7 731 664, dont 4 972 920 voitures de tourisme et 1 411 037 camionnettes | Les camionnettes (18 %) ne sont pas un marché marginal |
| **Voitures de 20 ans et plus** | **2 391 655, soit 48 % des voitures** | La moitié du parc date d'avant 2000. Le référentiel commence aujourd'hui en 1998, et la plupart des modèles en 2005 : **il manque la moitié du parc** |
| Peugeot et Renault | 17,4 % et 17,0 % du parc | Un véhicule sur trois est un Peugeot ou un Renault : ces deux marques doivent être les mieux couvertes |
| Volkswagen, Toyota, Hyundai, Dacia | 4,9 %, 4,3 %, 4,3 %, 3,8 % | Deuxième cercle |
| Fiat, Chevrolet, Citroën, Mazda | 2,9 %, 2,0 %, 1,8 %, 1,4 % | **Chevrolet, Citroën et Mazda sont absents** du référentiel |
| Toyota et Mazda : surtout des utilitaires | Toyota : 139 525 camionnettes ; Mazda : 94 108 | Pick-up et fourgons (Hilux, Hiace, Mazda B2500/BT-50) |
| Énergie du parc de tourisme | 77 % essence | |
| **Énergie des voitures revendues en 2020** | **70 % diesel** (510 633 sur 727 605) | Le marché de l'occasion est diesel : injecteurs, filtre à gazole, bougies de préchauffage, vanne EGR, turbo |

**Le marché de l'occasion.** Les « transactions » de l'ONS (immatriculations et réimmatriculations) mesurent les véhicules qui changent de main.
- **En 2020** : Renault 17,3 %, Peugeot 11,1 %, Hyundai 6,3 %, Volkswagen 4,4 %, Dacia 4,4 %, Toyota 3,8 %, Kia 3,4 %, Chevrolet 2,5 %, Seat 2,1 %, marques chinoises 2,0 %.
- **Au second semestre 2019** : Mitsubishi arrivait 4ᵉ (4,9 %), presque à égalité avec Hyundai.

## 2. Oran

- **357 120 véhicules, 3ᵉ wilaya du pays (4,6 %)**, après Alger (23,3 %) et Blida (5,5 %).
- Dont 267 058 voitures de tourisme, 50 660 camionnettes et 15 531 camions.
- 75 % des véhicules roulent à l'essence.
- **Usine Fiat de Tafraoui (Stellantis), dans la wilaya.** Inaugurée en décembre 2023, elle a passé les 50 000 véhicules. Elle a assemblé la 500 Hybrid (arrêtée depuis), assemble le Doblò depuis juin 2024, et prépare la Grande Panda. Les Fiat récentes d'Oran vont arriver en âge d'entretien : demande à prévoir en filtres, freins et embrayage pour le Doblò.

## 3. Ce qui se vend aujourd'hui (2023-2026)

- Les importations de véhicules neufs ont repris en mars 2023. Le ministère a délivré 27 agréments.
- **Fiat est le premier vendeur.** Le Doblò est le modèle le plus vendu en 2024, d'après une source secondaire.
- **Les marques chinoises montent très vite.**
  - Les marques les plus citées : Geely (Coolray), Chery (Tiggo 4), MG (MG5), JAC, DFSK, Jetour, GAC.
  - Selon les douanes, 143 012 véhicules de marques chinoises ont été importés au premier semestre 2026, soit 235 % de plus en un an.
  - Ces véhicules sont récents. Ils demanderont surtout de l'entretien courant, plus tard des pièces d'usure. Les pièces sont moins disponibles et plus difficiles à identifier : c'est là que la référence exacte (étape 8, section 6.7) apporte le plus.
- **Pièces détachées** (presse, chiffres souvent anciens) :
  - pénuries fréquentes, surtout pour les marques allemandes et asiatiques, faute de réseau après-vente ;
  - beaucoup de contrefaçon : jusqu'à la moitié des pièces importées selon une estimation ;
  - les pièces citées comme les plus importées sont les amortisseurs, les boîtes de vitesses, les radiateurs, les câbles de frein et les roues ;
  - les plus contrefaites sont les joints de culasse, les biellettes et les triangles.
  - Pour DALIL, la distinction « origine / adaptable », déjà dans le catalogue, est un vrai service à mettre en avant.

## 4. Écarts avec le référentiel actuel de DALIL (`data/seed/vehicles.json`)

| Marque (part du parc) | Ce que DALIL couvre | Modèles courants à ajouter en priorité (à confirmer en magasin) |
| --- | --- | --- |
| Peugeot (17,4 %) | 206, 208, 301 | 205, 405, 406, 307, 308, 207, 2008, 3008 ; utilitaires Partner, Expert, Boxer ; anciennes 404, 504, 505 |
| Renault (17,0 %) | Symbol, Clio, Kangoo | Clio 1 et 2 (« Clio Campus »), R4, R19, Mégane, Scénic ; utilitaires Express, Trafic, Master |
| Volkswagen (4,9 %) | Golf, Polo, T-Roc | Golf 2, 3 et 4, Passat, Caddy, Touareg ; modèles importés de Chine (Tharu, T-Cross) |
| Toyota (4,3 %) | Hilux | Corolla, Yaris, Hiace, Land Cruiser, Prado |
| Hyundai (4,3 %) | Accent, i10 | Atos, Elantra, i20, Tucson, Creta, Santa Fe ; utilitaire H-100 |
| Dacia (3,8 %) | Logan, Sandero, Duster | Couverture correcte |
| Fiat (2,9 %) | Tipo, 500, Doblò | Uno, Punto, Palio, Siena (parc ancien) ; Grande Panda (Tafraoui) |
| **Chevrolet (2,0 %)** | **aucun** | Aveo, Spark, Optra, Sail |
| **Citroën (1,8 %)** | **aucun** | C3, C4, Xsara, C-Élysée, Berlingo |
| **Mazda (1,4 %, surtout utilitaires)** | **aucun** | B2500, BT-50, 323 |
| **Mitsubishi (1,0 % du parc, 4,9 % des transactions fin 2019)** | **aucun** | L200, Pajero, Lancer |
| Kia (0,6 % du parc, 3,4 % des transactions) | Picanto, Rio | Sportage, Cerato |
| Seat, Nissan, Mercedes, Daewoo, Honda (0,8 à 0,9 % chacune) | Seat : aucun | Seat Ibiza et León ; Nissan Sunny et Navara ; Daewoo Matiz ; Mercedes Sprinter |
| Marques chinoises (en forte hausse) | Geely Coolray, Chery Tiggo 4, MG5, Jetour X70, DFSK Glory 580 | Chery Tiggo 2, 7 et 8 ; Geely GX3 Pro et Emgrand ; JAC ; GAC |

## 5. Recommandations pour le site

1. **Étendre le référentiel**, dans l'ordre des parts du parc et des transactions :
   - d'abord Peugeot et Renault anciennes et utilitaires ;
   - puis Chevrolet, Citroën, Mazda et Mitsubishi, aujourd'hui absentes ;
   - puis les modèles chinois récents.
   - Ouvrir la liste des années jusqu'aux années 1980. Années et motorisations à faire confirmer par les magasins enquêtés : la règle déjà notée dans `data/SOURCES.md` s'applique.
2. **Prévoir « Mon véhicule n'est pas dans la liste »** (marque et modèle en texte libre, enregistrés) : avec la moitié du parc de plus de 20 ans, la liste ne sera jamais complète, et ces saisies diront quoi ajouter ensuite.
3. **Renforcer le diesel** dans les fiches de pannes et la taxonomie (préchauffage, injection, EGR, turbo), puisque 70 % des voitures revendues sont diesel.
4. **Couvrir les utilitaires** (Partner, Kangoo, Hiace, H-100, pick-up L200 et B2500) : 18 % du parc, et une clientèle professionnelle qui achète souvent.
5. **Mesurer la demande réelle avec DALIL lui-même.** L'indicateur « véhicules et pièces les plus recherchés » existe déjà en partie (pièces les plus contactées, page Indicateurs). Y ajouter les véhicules les plus diagnostiqués. Ce sera la seule mesure par modèle propre à Oran, sans dépendre d'aucune plateforme.
6. **En magasin, pendant les essais** (`docs/essais-oran.md`), demander à chaque vendeur ses 10 modèles et ses 10 pièces les plus demandés. C'est la façon légitime de remplacer les chiffres par modèle que l'ONS ne publie pas.

## Sources

- ONS, [Parc national automobile au 31/12/2020](https://www.ons.dz/IMG/pdf/i.parc_nat31_12_2020.pdf), Données statistiques n° 996, mai 2023.
- ONS, [Immatriculations et réimmatriculations du 2ᵉ semestre 2019 selon la marque](https://www.ons.dz/IMG/pdf/e.marc_s2_19.pdf).
- Trésor (France), [fiche économique sur l'Algérie](https://www.tresor.economie.gouv.fr/PagesInternationales/Pages/c0f80aa9-c916-43c1-ad74-3e84b03f201a/files/efb4a6d3-cfb1-41c6-85f5-547cb2eb90c4) (parc 2018 par marque).
- Algérie360, [Quelle est la voiture la plus vendue en Algérie en 2024 ?](https://www.algerie360.com/quelle-est-la-voiture-la-plus-vendue-en-algerie-en-2024/).
- Algérie-Eco, [Plus de 96 000 véhicules importés en 2025](https://algerie-eco.com/?p=235727) ; [L'Algérie parmi les principaux importateurs de véhicules chinois](https://algerie-eco.com/2026/08/12/automobile-lalgerie-parmi-les-principaux-importateurs-de-vehicules-chinois/).
- Observ'Algérie, [143 000 voitures chinoises importées en six mois](https://observalgerie.com/2026/08/12/economie/algerie-143-000-voitures-chinoises-importees-en-six-mois-une-hausse-de-235/).
- Maghreb Émergent, [quotas d'importation par marque](https://maghrebemergent.news/fr/importation-automobile-quels-seront-les-quotas-attribues-pour-chaque-marque-en-algerie/).
- Motorsactu, [l'usine Fiat de Tafraoui franchit le cap des 50 000 véhicules](https://motorsactu.com/stellantis-algerie-lusine-fiat-de-tafraoui-franchit-le-cap-des-50-000-vehicules/) ; Stellantis, [un an après son lancement, l'usine Fiat de Tafraoui](https://www.media.stellantis.com/me-fr/corporate/press/un-an-apres-son-lancement-l-usine-fiat-de-tafraoui-poursuit-son-developpement).
- Algérie360, [Pièces détachées importées : 30 000 tonnes contrefaites](https://www.algerie360.com/pieces-detachees-importees30-000-tonnes-sont-contrefaites/) ; [Pièces détachées en Algérie : pénurie, flambée des prix, importations](https://www.algerie360.com/pieces-detachees-en-algerie-penurie-flambee-des-prix-importations-ce-qui-change-en-2025/) ; Echorouk, [pièces contrefaites](https://www.echoroukonline.com/commercialisation-de-30-000-tonnes-de-pieces-detachees-contrefaites).
- Ouedkniss, [conditions générales d'utilisation, article 9](https://www.ouedkniss.com/terms?lang=fr) (raison de l'exclusion).
