# DALIL — cahier des charges de la plateforme de diagnostic auto et de localisation de pièces détachées (Oran)

Nov 13, 2026 · @Adel

Le produit répond à une question : « ma voiture a ce problème, quelle pièce me faut-il et quel magasin d'Oran la vend ? ». Il enchaîne un diagnostic assisté par IA, l'identification de la pièce compatible et la recommandation des magasins qui la vendent probablement.

## Décisions arrêtées

Réponses de l'équipe du 14 novembre 2026. Elles priment sur le reste du document en cas d'écart.

| Sujet | Décision |
| --- | --- |
| Nom | DALIL, nom provisoire |
| Cadre | PFE en binôme, sujet accepté par l'encadrante ; code et terrain faits à deux |
| Dispositif | PFE inscrit dans « un diplôme, une startup » (arrêté 1275) |
| Échéance | Soutenance fin mai ou juin 2027 ; examens les trois premières semaines de janvier |
| Suite | Projet de startup, à protéger puis à commercialiser |
| Modèle | Le jury attend un modèle entraîné par l'équipe. Le modèle affiné est le cœur du système ; un modèle payant ne sert que de point de comparaison |
| Matériel | Développement sur un portable sans carte graphique (Core Ultra 7, 16 Go) ; entraînement sur GPU gratuit en ligne ; PC avec RTX 3050 en secours |
| Budget | Le plus bas possible ; carte de paiement internationale disponible |
| Mise en ligne | Tests en local d'abord ; mise en ligne à la fin, sur décision de l'équipe |
| Zone | Ville d'Oran ; magasins visités sans ciblage au début ; 20 magasins ou plus avant la soutenance |
| Mécaniciens | 2 ou 3 partenaires espérés, aucun contact pour l'instant |
| Marques | Toutes les marques répandues en Algérie, y compris les modèles des années 2010 |
| Langue | Français seulement pour la première version |
| Voix | Dans le PFE |
| Supports | Site web d'abord, application mobile ensuite |
| Comptes magasins | Dans le PFE |
| Pièce | Référence exacte visée ; pilote sur Logan, Symbol, Accent, 301 et Picanto |
| Données | Sources de toutes langues, traduites ensuite en français |

## 1. Vision et périmètre

**Problème.** À Oran, trouver une pièce détachée se fait par téléphone et de boutique en boutique. Les magasins sont spécialisés par marque ou par famille de pièces, mais cette information n'est écrite nulle part.

**Solution.** Une application web mobile en trois briques :

1. **Diagnostic** : l'utilisateur décrit la panne (texte, puis voix) et peut ajouter un code OBD-II ; l'outil propose des causes classées et la pièce à remplacer.
2. **Annuaire qualifié des magasins** : chaque magasin est décrit par les marques et les familles de pièces qu'il vend, puis par son catalogue réel.
3. **Recommandation** : pour une pièce et un véhicule donnés, l'outil classe les magasins par probabilité de l'avoir, distance et fiabilité.

**Déploiement en deux temps.** Au départ, l'équipe collecte elle-même les données des magasins d'Oran. Ensuite, les magasins créent leur compte et publient leurs produits ; la plateforme s'alimente seule.

**Périmètre géographique.** Ville d'Oran pour le lancement. Le modèle de données porte dès le départ la wilaya et la commune, pour s'étendre au reste de l'Algérie sans refonte.

**Hors périmètre du MVP.** Paiement en ligne, livraison, application mobile native (elle suit le site), arabe et darija, diagnostic par photo ou par son.

## 2. Acteurs et parcours

Quatre rôles, avec des droits distincts dans l'application.

| Rôle | Ce qu'il veut | Ce qu'il fait dans l'outil |
| --- | --- | --- |
| Automobiliste | Comprendre la panne et savoir où acheter la pièce | Décrit le problème, choisit son véhicule, reçoit causes, pièce et magasins ; appelle ou écrit au magasin |
| Mécanicien / garage | Trouver vite la pièce pour le véhicule d'un client | Recherche directe par pièce, référence ou véhicule ; enregistre ses véhicules en cours ; confirme ou corrige le diagnostic |
| Magasin de pièces | Être trouvé par les clients qui cherchent ce qu'il vend | Crée sa fiche, déclare marques et familles de pièces, publie son catalogue, répond aux demandes |
| Administrateur | Garder des données fiables | Saisit les magasins collectés sur le terrain, valide les inscriptions, modère, suit les indicateurs |

**Parcours principal (automobiliste)**

1. Il choisit son véhicule : marque, modèle, année, motorisation (ou VIN).
2. Il décrit le problème en français, par écrit ou à la voix, et ajoute un code OBD-II s'il en a un.
3. L'outil pose une à trois questions de précision (quand, où, quel bruit).
4. Il reçoit jusqu'à trois causes classées, chacune avec la pièce concernée et un niveau de confiance.
5. Il choisit une pièce ; l'outil affiche les magasins classés, sur une carte et en liste.
6. Il contacte le magasin (appel ou WhatsApp) ; plus tard, l'outil lui demande s'il a trouvé la pièce.

**Parcours direct (mécanicien)** : il saute le diagnostic et cherche « plaquettes de frein avant, Renault Symbol 2015 » ; l'étape 5 s'applique telle quelle.

**Parcours magasin** : inscription avec numéro de téléphone, position sur la carte, marques et familles de pièces cochées en moins de trois minutes ; le catalogue détaillé vient ensuite.

## 3. Fonctionnalités par version

Le MVP doit prouver une chose : un utilisateur décrit une panne et obtient un magasin d'Oran qui a la pièce. Tout le reste attend.

| ID | Fonctionnalité | Quand | Critère d'acceptation |
| --- | --- | --- | --- |
| F1 | Sélection du véhicule (marque, modèle, année, motorisation) | PFE | Référentiel couvrant les marques prioritaires de la section 5 ; saisie en moins de 20 secondes |
| F2 | Diagnostic par texte en français | PFE | Renvoie 1 à 3 causes avec pièce associée et niveau de confiance ; répond « je ne sais pas » sous un seuil de confiance |
| F3 | Saisie d'un code OBD-II | PFE | Tout code générique reconnu est expliqué en français et relié à des pièces candidates |
| F4 | Questions de précision | PFE | Au plus 3 questions fermées quand deux causes sont trop proches |
| F5 | Taxonomie des pièces (familles, sous-familles, synonymes) | PFE | Chaque cause de panne pointe vers une entrée de la taxonomie |
| F6 | Annuaire des magasins avec marques et familles vendues | PFE | Fiche : nom, téléphone, position, horaires, marques, familles, source et date de la donnée |
| F7 | Recommandation de magasins pour une pièce et un véhicule | PFE | Liste classée avec score expliqué (« vend Renault, vend freinage, à 2 km ») ; carte et liste |
| F8 | Contact du magasin (appel, WhatsApp avec message pré-rempli) | PFE | Le message contient véhicule et pièce ; le clic est enregistré |
| F9 | Retour utilisateur « pièce trouvée ? » | PFE | Réponse oui/non rattachée au magasin et à la pièce ; alimente le score |
| F10 | Back-office administrateur | PFE | Création, import CSV, validation et fusion de fiches magasin |
| F11 | Compte magasin en libre-service | PFE | Inscription par téléphone, validation par l'administrateur, modification de sa fiche |
| F12 | Catalogue du magasin (saisie, import Excel) | PFE | Un produit se crée en moins de 30 secondes ; import de 500 lignes sans erreur |
| F13 | Saisie vocale en français | PFE | Transcription du message vocal avant diagnostic, avec correction possible |
| F14 | Référence exacte de la pièce | PFE, pilote | Référence lue dans une base pour cinq modèles pilotes ; recherche par numéro gravé sur l'ancienne pièce ; famille de pièce pour le reste |
| F15 | Application installable sur téléphone depuis le site | PFE | Le site s'installe comme une application et s'ouvre en plein écran |
| F16 | Demande de pièce diffusée aux magasins pertinents | PFE, en option | Les magasins qui vendent la marque et la famille sont notifiés et répondent « disponible / prix » |
| F17 | Compte mécanicien avec véhicules en cours et historique | Après le PFE | Reprise d'une recherche en un clic |
| F18 | Statistiques magasin (vues, appels, demandes) | Après le PFE | Tableau de bord mensuel |
| F19 | Application mobile native | Après le PFE | Publiée sur les magasins d'applications |
| F20 | Arabe et darija, à l'écrit puis à la voix | Après le PFE | Jeu de test dédié par langue |
| F21 | Référence exacte généralisée (catalogue sous licence) | Après le PFE | Couverture de toutes les marques prioritaires |
| F22 | Photo de la pièce ; lecture d'un boîtier OBD Bluetooth | Après le PFE | Famille de pièce proposée depuis une photo ; codes lus sans saisie |
| F23 | Extension à d'autres wilayas | Après le PFE | Activation d'une wilaya par configuration, sans développement |

**Amélioration proposée par rapport à l'idée initiale.** La demande diffusée (F16) règle le problème du stock : un petit magasin ne tiendra pas un inventaire à jour, mais il répondra à une demande précise sur son téléphone. Chaque réponse enrichit aussi les données sur ce qu'il vend réellement.

## 4. Données magasins d'Oran

L'annuaire qualifié est l'actif principal du produit : sans lui, le diagnostic ne mène nulle part. Il se construit en deux phases.

**Phase A — collecte par l'équipe (avant le lancement)**

| Source | Ce qu'elle apporte | Limite |
| --- | --- | --- |
| Visite terrain avec formulaire mobile | Donnée la plus fiable : marques, familles de pièces, téléphone, position exacte | Lent ; à concentrer sur les quartiers où les magasins sont regroupés |
| [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_parts) (balises `shop=car_parts`, `shop=car_repair`, `shop=tyres`) via l'API Overpass | Liste de départ gratuite et réutilisable, avec position | Couverture d'Oran inconnue, à mesurer dès la première requête |
| Google Maps | Noms, téléphones, horaires | Conditions d'utilisation à lire avant tout stockage ; à utiliser comme aide à la visite, pas comme base copiée |
| [Ouedkniss, rubrique pièces détachées](https://www.ouedkniss.com/pieces_detachees-pieces_automobiles/1) | Boutiques déjà actives en ligne, avec leurs spécialités affichées | Pas de collecte automatique sans accord du site ; repérage manuel, puis invitation à s'inscrire |
| Pages Facebook et Instagram des magasins | Spécialités, photos de stock, numéro WhatsApp | Repérage manuel |

**Fiche à remplir par magasin** : nom, téléphone, WhatsApp, commune, position GPS, horaires, marques vendues, familles de pièces vendues, origine des pièces (origine, adaptable, occasion), gros ou détail, photo de la devanture, date de la visite, nom de l'enquêteur.

**Objectif de lancement** : une couverture dense de quelques communes vaut mieux qu'une couverture mince de toute la wilaya. Le seuil chiffré (nombre de magasins) est à fixer après le premier comptage OSM et terrain.

**Phase B — libre-service (après le lancement)**

1. Le magasin s'inscrit avec son numéro de téléphone, ou « revendique » la fiche que l'équipe a déjà créée.
2. Un administrateur valide (appel de vérification).
3. Le magasin coche ses marques et familles, puis ajoute ses produits : saisie rapide, import Excel, ou photo.
4. Les demandes de pièces qu'il reçoit et ses réponses mettent à jour automatiquement ce que la plateforme sait de lui.

**Fraîcheur.** Chaque information porte sa source et sa date. Une fiche non confirmée depuis six mois est signalée à l'administrateur et perd des points dans le classement.

**Incitation pour les magasins.** Inscription gratuite, clients qualifiés (le client sait déjà quelle pièce il veut), statistiques de vues et d'appels. Un modèle payant (mise en avant, abonnement) ne se décide qu'après avoir prouvé le trafic.

## 5. Sources de données pour le diagnostic

Les meilleures sources ouvertes sont américaines et en anglais ; aucune ne couvre bien Renault, Peugeot ou Dacia, ni le français et la darija. Le plan combine donc trois couches : données ouvertes pour le volume, données francophones pour les marques locales, données d'Oran pour la langue et la vérité terrain.

**Couche 1 — données ouvertes, utilisables tout de suite**

| Source | Contenu | Usage dans le projet | Licence et limites |
| --- | --- | --- | --- |
| [NHTSA – plaintes des propriétaires (ODI Complaints)](https://catalog.data.gov/dataset/nhtsas-office-of-defects-investigation-odi-complaints) | Récits de pannes écrits par les conducteurs, avec marque, modèle, année et composant en cause. Fichier `FLAT_CMPL.zip`, champs décrits dans `CMPL.txt` ; API `api.nhtsa.gov/complaints/complaintsByVehicle` | Corpus principal pour apprendre « symptôme décrit → composant » | Données publiques du gouvernement américain. Anglais, marché américain, orienté sécurité ; catégories de composants assez larges |
| [NHTSA – communications constructeurs (bulletins techniques)](https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS.txt) | Résumés de bulletins de service depuis 1995, avec marque, modèle, année, composants et sous-système constructeur | Base de connaissances : problème connu → pièce et procédure | Public. Résumés seulement, pas tous les bulletins |
| [NHTSA – rappels](https://catalog.data.gov/dataset/nhtsas-office-of-defects-investigation-odi-recalls-complaints-flat-file) | Campagnes de rappel par véhicule et composant | Défauts connus par modèle | Domaine public américain |
| [OBDex](https://github.com/foerbsnavi/OBDex) | 9 533 codes défaut OBD-II génériques ; pour chacun : description, composants touchés, causes fréquentes, symptômes, réparation. JSON téléchargeable | Table `dtc_codes` complète dès le premier jour ; lien code → pièces candidates | Données en CC0. Anglais et allemand : traduction française à produire. Pas de codes constructeur (P1xxx) |
| [Stack Exchange – Motor Vehicle Maintenance & Repair](https://archive.org/details/stackexchange_20251231) | Questions de panne avec réponses votées et réponse acceptée | Paires question → diagnostic de bonne qualité | CC BY-SA, attribution obligatoire. Les exports depuis juin 2025 contiennent des données volontairement altérées : prendre un export antérieur |
| [NHTSA vPIC](https://vpic.nhtsa.dot.gov/api/) | Décodage de VIN, listes de marques et modèles. API gratuite, sans clé | Amorçage du référentiel véhicules | Couverture surtout nord-américaine : décodage partiel pour les véhicules vendus en Algérie |
| Jeux de données Hugging Face ([questions-réponses diagnostic](https://huggingface.co/datasets/build-small-hackathon/nemotron-car-diagnostics-datasets), [défauts automobiles](https://huggingface.co/datasets/zhengr/Automotive_Industry_Fault_Data_Set)) | Petits jeux, souvent synthétiques | Complément et jeux de test rapides | Qualité inégale : à lire échantillon par échantillon avant usage |

**Couche 1 bis — sources hors États-Unis**

Collecter dans toutes les langues n'a d'intérêt que si la source apporte ce que les données américaines n'ont pas : les modèles européens et chinois du parc algérien. Les sources sont classées de la plus utile à la moins utile.

| Source | Pays, langue | Ce qu'elle apporte | Licence et limites |
| --- | --- | --- | --- |
| [Contrôle technique britannique (DVSA, données MOT)](https://open.data.dvsa.gov.uk/mot-anonymised/index.html) | Royaume-Uni, anglais | Tous les contrôles depuis 2005 : marque, modèle, kilométrage, motifs d'échec. Les marques européennes et coréennes du parc algérien y sont | Open Government Licence. Données codées, sans texte libre : elles disent quelle pièce lâche sur quel modèle et à quel kilométrage, pas comment le client décrit la panne |
| [RappelConso, rappels automobiles (DGCCRF)](https://iautos.fr/fiabilite) | France, français | Campagnes de rappel rédigées en français, par modèle | Licence Ouverte 2.0. Défauts de sécurité seulement |
| [Safety Gate, alertes européennes](https://car-recalls.eu/2025-safety-gate-recalls-overall-table/) | Europe | Environ 400 alertes véhicules par an (399 en 2025), avec marque, modèle et défaut | Données officielles ouvertes. Défauts graves seulement |
| [Rappels du KBA](https://car-recalls.eu/car-recalls-full-year-2024-mercedes-bmw-ford-top) | Allemagne, allemand | Plus large que Safety Gate : 387 rappels en 2024 | Conditions de réutilisation à lire |
| [Chinese Vehicle Fleet Fault Association Dataset](https://data.mendeley.com/datasets/r98g7g6k5t/1) | Chine, chinois | Dossiers d'entretien réels de 2020 à 2023 : codes défaut, entités annotées, liens de cause à effet entre codes | Publié en juin 2026 ; licence à lire sur la page. Seule piste trouvée pour les marques chinoises |
| [Rappels et défauts du ministère japonais des transports](https://apify.com/jp-data-engine/japan-recall-monitor) | Japon, japonais | Défauts des marques japonaises | Pas d'export officiel en bloc : beaucoup d'effort pour peu de volume, à traiter en dernier |

**Traduction.** Tous les textes sont traduits en français par un modèle de traduction ouvert, exécuté sur GPU gratuit. Le texte d'origine reste stocké à côté. Le lexique des pièces impose les termes français, et un échantillon de 200 traductions est relu à la main : une erreur sur un nom de pièce fausse l'étiquette d'entraînement.

**Limite à garder en tête.** Le volume ne remplace pas la vérité terrain. Cent cas réels d'Oran valent plus pour l'évaluation que cent mille plaintes traduites.

**Couche 2 — données francophones et marques locales (autorisation à demander)**

| Source | Intérêt | Condition |
| --- | --- | --- |
| Forums techniques francophones, par exemple [Planète Renault, rubrique mécanique](https://www.planeterenault.com/forum/technique-mecanique-f3-240.html) | Des milliers de sujets par modèle Renault et Dacia, en français, dont certains marqués « Réglé » | Pas de licence ouverte : demander l'accord écrit des administrateurs avant toute collecte |
| Revues techniques et manuels d'atelier | Procédures et pannes types par modèle | Sous droit d'auteur : usage en consultation pour rédiger des fiches, pas en copie |
| Catalogue TecDoc (TecAlliance) | Référence du marché pour la compatibilité pièce – véhicule | [Licence commerciale obligatoire](https://dev-opla.com/resources/what-is-tecdoc-auto-parts-ecommerce-guide) ; à envisager en V3 seulement |

À éviter : Reddit. La communauté r/AskAMechanic interdit explicitement les demandes liées à l'entraînement d'IA, et les conditions de la plateforme sont à vérifier avant tout usage.

**Couche 3 — données d'Oran (à créer, c'est l'avantage du projet)**

- **Cas réels de mécaniciens partenaires** : véhicule, symptôme dit par le client dans ses mots, cause trouvée, pièce changée. Un formulaire de 30 secondes par cas.
- **Lexique local** : noms des pièces et des symptômes en darija, en lettres arabes et latines, avec leur équivalent français.
- **Données synthétiques contrôlées** : un modèle de langage reformule les symptômes d'OBDex et des plaintes NHTSA en français et en darija ; un mécanicien valide un échantillon.
- **Retours de l'application** : chaque « diagnostic confirmé » ou « pièce trouvée » devient un exemple d'entraînement.

**Jeu de test figé.** Avant tout entraînement, mettre de côté un jeu de cas réels d'Oran, annotés par des mécaniciens, qui ne sert qu'à mesurer. Cible proposée : 200 cas.

**Contexte du parc.** Selon l'ONS, les véhicules d'origine française formaient [40,76 % du parc algérien fin 2018](https://atlas-mag.net/fr/articles/algerie-le-parc-national-automobile-en-2018), devant le Japon (10,29 %) et l'Allemagne (8,33 %). Ces chiffres datent ; la liste des marques prioritaires est à confirmer auprès des magasins d'Oran.

**Marques et modèles prioritaires**

Le parc d'Oran mêle deux générations : les modèles vendus en masse entre 2010 et 2015, qui demandent le plus de pièces, et la vague récente, surtout chinoise.

| Génération | Marques et modèles | Ce que disent les chiffres |
| --- | --- | --- |
| Années 2010 | Dacia Logan, Sandero, Duster ; Renault Symbol, Clio ; Hyundai Accent, i10 ; Peugeot 301 ; Kia Picanto ; Toyota Hilux | [Logan (24 469) et Accent (23 569) en tête des ventes 2014](https://journalauto.com/data-center/le-top-10-des-modeles-les-plus-vendus-en-algerie/) ; [groupe Renault à 33,4 % du marché en 2015](https://bestsellingcarsblog.com/2016/01/algeria-full-year-2015-dacia-logan-holds-off-renault-symbol-for-now/) |
| Depuis 2023 | Fiat (usine à Oran) ; Geely Coolray ; MG5 ; Chery Tiggo 4 ; Jetour X70 ; Livan, GAC, Roewe ; Opel ; DFSK | [Fiat première marque en 2025, devant Geely, Opel, Chery et DFSK](https://www.focus2move.com/algerian-vehicles-sales/) ; [190 045 véhicules expédiés de Chine vers l'Algérie de janvier à août 2026](https://www.algerie360.com/voitures-chinoises-algerie-190000-vehicules-8-mois/) |
| Citées par l'équipe, à confirmer sur le terrain | Skoda ; Volkswagen Golf, Polo, T-Roc | Pas de chiffre trouvé |

**Conséquences**

- Les modèles des années 2010 sont bien couverts par les sources britanniques et françaises, peu par les sources américaines : parmi eux, seule la Hyundai Accent a été vendue aux États-Unis. La Symbol et la 301 n'ont pas été vendues au Royaume-Uni ; leurs données viendront de modèles à la mécanique proche, comme la Logan pour la Symbol.
- Les marques chinoises récentes ont peu de données de pannes et peu de catalogues de références accessibles. Le diagnostic y sera moins précis au départ.
- Le formulaire de collecte gagne une question : « quels sont les dix modèles pour lesquels on vous demande le plus de pièces ? ». Les réponses de 20 magasins fixeront la liste définitive.

## 6. Approche IA

Recommandation : ne pas entraîner un seul grand modèle « sur le maximum de données », mais assembler quatre briques simples, mesurées une par une. C'est plus fiable, moins cher, et la comparaison des variantes fournit la partie expérimentale du mémoire.

**6.1 Chaîne de diagnostic**

1. **Normalisation.** Détection de la langue et de l'écriture (français, arabe, darija en lettres arabes ou latines), correction légère, remplacement des termes locaux par leur entrée du lexique.
2. **Recherche.** Recherche hybride (mots-clés et vecteurs multilingues) dans la base de connaissances : codes OBD, bulletins, plaintes regroupées, questions-réponses, fiches de pannes rédigées.
3. **Classification.** Un classifieur prédit la famille de pièce à partir du texte et du véhicule. Référence de départ : TF-IDF et régression logistique. Variante : encodeur multilingue affiné. Pour la darija, [DziriBERT](https://huggingface.co/alger-ia/dziribert) est un candidat (licence Apache 2.0, lettres arabes et latines, entraîné sur environ un million de tweets).
4. **Synthèse.** Un modèle de langage reçoit le texte, le véhicule, les passages retrouvés et les prédictions du classifieur. Il renvoie un JSON strict : causes classées, identifiant de famille de pièce, confiance, questions de précision, niveau d'urgence. Il ne cite que des pièces présentes dans la taxonomie.

**Règles de sûreté**

- Sous un seuil de confiance, l'outil répond qu'il ne sait pas et propose de consulter un mécanicien.
- Freinage, direction, odeur de carburant, surchauffe : message « ne roulez pas » affiché en premier.
- Chaque résultat rappelle qu'il s'agit d'une aide, pas d'un diagnostic certifié.

**6.2 Expériences à mener (matière du mémoire)**

| Variante | Ce qu'elle teste |
| --- | --- |
| A. TF-IDF + régression logistique | Référence minimale |
| B. Encodeur multilingue affiné | Gain de l'apprentissage profond et du transfert anglais → français / darija |
| C. Recherche + modèle de langage, sans classifieur | Ce que vaut la base de connaissances seule |
| D. Chaîne complète (recherche + classifieur + modèle de langage) | Solution visée |

Mesures sur le jeu de test d'Oran : exactitude top-1 et top-3 sur la famille de pièce, par langue ; taux de « je ne sais pas » ; temps de réponse ; coût par requête.

**6.3 Passage de l'anglais au français et à la darija**

Deux voies à comparer : traduire automatiquement les données américaines en français avant l'entraînement, ou entraîner un encodeur multilingue en anglais et compter sur le transfert. Dans les deux cas, les cas réels d'Oran servent à l'affinage final.

**6.4 Moteur de recommandation des magasins**

Le score d'un magasin pour une pièce et un véhicule additionne cinq signaux. Les poids ci-dessous sont un point de départ, à recalibrer avec les retours « pièce trouvée ».

| Signal | Poids initial | Calcul |
| --- | --- | --- |
| Produit au catalogue compatible avec le véhicule | 0,35 | 1 si un produit correspond, sinon 0 |
| Vend la marque du véhicule | 0,25 | 1 si déclaré ou observé |
| Vend la famille de pièce | 0,20 | 1 si déclaré ou observé |
| Proximité | 0,10 | Décroît avec la distance |
| Fiabilité | 0,10 | Taux de « pièce trouvée », fraîcheur de la fiche, taux de réponse aux demandes |

Chaque résultat affiche la raison du classement. Plus tard, quand les retours seront assez nombreux, un modèle appris pourra remplacer les poids fixes.

**6.5 Voix**

Transcription du message vocal par un modèle de reconnaissance de la parole, puis même chaîne que le texte. Première version en français, avec Whisper sans affinage. La qualité est à mesurer sur une cinquantaine d'enregistrements réels d'Oran, où le français se mêle à la darija.

**6.6 Modèles retenus**

Pour chaque brique, un choix principal et une alternative à comparer sur le jeu de test d'Oran. Les classements publics ne suffisent pas pour choisir : un [audit publié en novembre 2026](https://aclanthology.org/2026.aacl-short.28.pdf) montre qu'un même score global cache des comportements très différents selon la langue.

| Brique | Choix principal | À comparer | Où il tourne |
| --- | --- | --- | --- |
| Classifieur de famille de pièce | [mmBERT-base](https://huggingface.co/blog/mmbert) affiné : encodeur multilingue de 2025, licence MIT, au-dessus de XLM-R sur les tests multilingues | XLM-RoBERTa (référence historique) ; pour la darija, [DziriBERT](https://huggingface.co/alger-ia/dziribert) et [algerianDeBERTa](https://huggingface.co/81melody/algerianDeBERTa) | Carte RTX 3050 |
| Vecteurs de recherche | [Qwen3-Embedding](https://www.datallmlab.com/blog/best-embedding-models.html) : licence Apache 2.0 ; version 8B classée première du classement multilingue MTEB en juin 2025 | BGE-M3 (licence MIT, recherche dense et par mots-clés dans un seul modèle) ; gemini-embedding-001 en service payant | Version 0.6B en local ; 8B sur GPU en ligne |
| Reclassement des passages | [bge-reranker-v2-m3](https://futureagi.com/blog/best-rerankers-for-rag-2026/) : multilingue, Apache 2.0 | Qwen3-Reranker (0.6B ou 4B) ; [jina-reranker-v3](https://jina.ai/news/jina-reranker-v3-0-6b-listwise-reranker-for-sota-multilingual-retrieval/), licence à vérifier | Carte RTX 3050 |
| Synthèse, qualité maximale | Modèle de langage de dernière génération en service payant : Claude Sonnet 5.5 ou Opus 5.5 | Les modèles les plus récents d'OpenAI et de Google au moment du test | Service en ligne |
| Synthèse, modèle entraîné par l'étudiant | Qwen3-8B ou Gemma 3 (4B ou 12B), affiné par LoRA en 4 bits. Ces deux familles sont données comme [les plus solides en arabe parmi les modèles utilisables en local](https://www.promptquorum.com/local-llms/multilingual-local-llms) (avril 2026) | Mistral Small pour le français ; [awras-chat-v0](https://huggingface.co/awras/awras-chat-v0), modèle de 4,3 milliards de paramètres dédié à la darija algérienne | GPU gratuit de Kaggle ou Colab pour l'entraînement |
| Voix (V2) | Whisper large-v3-turbo affiné sur de la darija algérienne | SeamlessM4T-v2 Large ; Whisper-medium | GPU en ligne |

**Trois remarques**

- **Le plus gros modèle n'est pas toujours le meilleur.** Sur la traduction de dialectes arabes, [des modèles de 9 milliards de paramètres affinés ont battu des modèles bien plus grands utilisés tels quels](https://arxiv.org/pdf/2507.20301). C'est l'hypothèse à tester ici : un petit modèle affiné sur les pannes peut-il rejoindre un grand modèle généraliste ?
- **La voix en darija reste difficile.** Dans une [compétition de 2025 sur huit dialectes arabes](https://arxiv.org/abs/2511.10090v1), le meilleur système de l'équipe citée gardait 38,54 % d'erreurs sur les mots. Ne pas la promettre avant de l'avoir mesurée.
- **Vérifier les versions le jour de l'entraînement.** Ces familles sortent une nouvelle version plusieurs fois par an ; le jeu de test figé permet de changer de modèle sans refaire le protocole.

**6.7 Référence exacte de la pièce**

La référence exacte ne sort jamais du modèle : un modèle de langage invente des numéros plausibles. Le modèle désigne la famille de pièce ; la référence est ensuite lue dans une base.

Trois niveaux de réponse, affichés tels quels à l'utilisateur :

1. **Famille de pièce** (« plaquettes de frein avant ») : toujours disponible, produite par le modèle entraîné.
2. **Référence trouvée** : quand une base connaît la référence pour ce véhicule précis.
3. **Référence confirmée** : un magasin a ce produit à son catalogue ou a répondu « disponible ».

| D'où vient la référence | Coût | Limite |
| --- | --- | --- |
| Numéro gravé sur l'ancienne pièce, saisi par l'utilisateur | Gratuit | La pièce doit être démontée |
| Catalogues des magasins inscrits | Gratuit | Se remplit avec le temps |
| [Service de catalogue tiers](https://github.com/ronhartman/tecdoc-autoparts-catalog), annoncé à [29 $ par mois](https://apify.com/making-data-meaningful/tecdoc/api/openapi) | Petit abonnement | Origine des données et couverture des modèles algériens et chinois à vérifier avant de payer |
| [Service « numéro de châssis → référence constructeur »](https://eitserv.tech/en/vin-to-oem-parts-api) | Sur devis | Fiable, mais c'est un coût de startup financée |
| TecDoc | Licence commerciale | Après une levée de fonds |

**Pour le PFE.** Niveau 2 sur un pilote de cinq modèles très répandus (Logan, Symbol, Accent, 301, Picanto) et une vingtaine de familles de pièces d'usure, saisies avec les magasins partenaires. Niveau 1 pour tout le reste. Le mémoire présente la généralisation comme perspective.

| Modèle du pilote | Pourquoi lui | Données de pannes disponibles |
| --- | --- | --- |
| Dacia Logan | [Première des ventes en 2013, 2014 et 2015](https://bestsellingcarsblog.com/2016/01/algeria-full-year-2015-dacia-logan-holds-off-renault-symbol-for-now/) | Contrôle technique britannique |
| Renault Symbol | [Produite près d'Oran depuis 2014](https://journalauto.com/constructeurs/lalgerie-tout-un-symbol-pour-renault/) ; mécanique proche de la Logan | Celles de la Logan |
| Hyundai Accent | Deuxième des ventes en 2014 | Plaintes NHTSA : seul modèle du pilote vendu aux États-Unis |
| Peugeot 301 | Deuxième des ventes en 2013 | Peu de données propres : le cas difficile du pilote, utile pour mesurer la limite |
| Kia Picanto | [Troisième des ventes en septembre 2014](https://bestsellingcarsblog.com/2014/10/algeria-september-2014-renault-symbol-leads-the-way/) | Contrôle technique britannique |

**Familles de pièces du pilote** : plaquettes avant et arrière, disques, filtres à huile, à air, à carburant et d'habitacle, bougies, bobine d'allumage, kit de distribution, courroie d'accessoires, pompe à eau, thermostat, amortisseurs, rotules, biellettes, roulements de roue, kit d'embrayage, batterie, alternateur, démarreur.

**Catalogue payant.** La carte de paiement permet d'essayer un service de catalogue. Vérifier d'abord, pendant la période d'essai, qu'il connaît ces cinq modèles ; sinon, ne pas s'abonner.

**6.8 Entraîner et faire tourner sans carte graphique**

Le portable sert à développer ; l'entraînement se fait sur GPU gratuit en ligne.

| Tâche | Où | Coût |
| --- | --- | --- |
| Code, base de données, API, modèle de référence TF-IDF | Portable | Aucun |
| Affinage de mmBERT, affinage LoRA du modèle de langage, traduction des corpus | Kaggle : GPU gratuit, [quota hebdomadaire affiché dans le compte, souvent autour de 30 heures](https://gpuperhour.com/blog/free-cloud-gpus-and-credits). Colab en appoint | Aucun |
| Démonstration en local | Portable : classifieur, recherche, et modèle de langage affiné compressé en 4 bits | Aucun ; réponses lentes sur processeur |
| Mise en ligne | À décider à la fin : serveur sans carte graphique avec petit modèle compressé, ou GPU facturé à l'usage | À chiffrer le moment venu |

- **Taille du modèle.** Viser 4 milliards de paramètres (Qwen3-4B ou Gemma 3 4B) pour qu'il tourne sans carte graphique. [Un adaptateur LoRA pour un modèle de 7 à 8 milliards s'entraîne aussi sur un T4 gratuit](https://amitpandeytiktok.github.io/awesome-free-compute-2026/compute.html) : à garder comme variante de comparaison.
- **Modèle payant.** Utilisé une seule fois, sur le jeu de test, pour mesurer l'écart avec le modèle entraîné. Pas en production.
- **Sauvegardes.** Les sessions Kaggle sont limitées en durée : enregistrer les poids à chaque époque et reprendre l'entraînement d'une session à l'autre.

## 7. Architecture

Une API unique sert l'application et le back-office ; elle regroupe les trois moteurs et s'appuie sur une seule base de données.

&#91;embedded content: architecture · 2 interfaces, 1 API, 3 moteurs, 1 base, pipelines de données\]

Le diagnostic désigne une famille de pièce du référentiel, que la recommandation transforme en liste de magasins. Les pipelines de données tournent hors ligne et alimentent la base ; l'application n'en dépend pas pour répondre.

| Couche | Choix proposé | Raison |
| --- | --- | --- |
| Backend | Python, FastAPI, SQLAlchemy, Alembic | Même langage que les modèles ; documentation d'API automatique |
| Base de données | PostgreSQL avec PostGIS et pgvector | Une seule base pour le métier, la géographie et la recherche vectorielle |
| Frontend | Next.js, TypeScript, application web installable | Un seul code pour téléphone et ordinateur ; pas de passage par les magasins d'applications |
| Carte | Leaflet avec fond OpenStreetMap | Gratuit, sans clé |
| Modèles | scikit-learn pour la référence, Transformers pour l'encodeur affiné | Standards, reproductibles |
| Modèle de langage | Derrière une interface unique ; fournisseur à choisir (question ouverte) | Changer de fournisseur sans toucher au reste |
| Connexion | Code à usage unique par SMS | Les commerçants n'utilisent pas tous l'e-mail |
| Déploiement | Conteneurs Docker ; hébergement à choisir (question ouverte) | Reproductible en local et en ligne |

## 8. Modèle de données

Une seule base PostgreSQL porte tout : données métier, positions géographiques (PostGIS) et vecteurs de recherche (pgvector).

| Table | Champs clés | Rôle |
| --- | --- | --- |
| `wilayas`, `communes` | code, nom\_fr, nom\_ar | Découpage géographique, prêt pour l'extension nationale |
| `users` | id, phone, role (driver, mechanic, shop\_owner, admin), name, lang | Comptes |
| `shops` | id, name, phone, whatsapp, commune\_id, geom, address, hours, status (draft, verified, claimed), source, verified\_at, owner\_user\_id | Magasins |
| `brands`, `models`, `vehicle_variants` | brand\_id, model\_id, year\_from, year\_to, engine, fuel | Référentiel véhicules |
| `part_categories` | id, parent\_id, name\_fr, name\_ar, synonyms\[\] | Taxonomie des pièces, avec synonymes locaux |
| `shop_brands` | shop\_id, brand\_id, source, confirmed\_at | Marques vendues par magasin |
| `shop_categories` | shop\_id, category\_id, source, confidence, confirmed\_at | Familles vendues par magasin |
| `products` | id, shop\_id, category\_id, title, oem\_ref, part\_brand, condition, price, in\_stock, photo\_url, updated\_at | Catalogue des magasins |
| `product_fitments` | product\_id, variant\_id | Compatibilité produit – véhicule |
| `faults` | id, name\_fr, system, severity, description | Pannes types |
| `fault_parts` | fault\_id, category\_id, weight | Lien panne → pièces |
| `dtc_codes` | code, title\_fr, title\_en, description, causes, symptoms | Codes OBD-II |
| `dtc_parts` | code, category\_id, weight | Lien code → pièces |
| `knowledge_chunks` | id, source, lang, text, embedding, metadata, license | Base de connaissances pour la recherche |
| `diagnosis_sessions` | id, user\_id, variant\_id, input\_text, lang, dtc\_codes\[\], result\_json, model\_version, created\_at | Trace de chaque diagnostic |
| `part_requests` | id, session\_id, user\_id, variant\_id, category\_id, status, created\_at | Demandes de pièces diffusées (V2) |
| `request_responses` | request\_id, shop\_id, available, price, responded\_at | Réponses des magasins (V2) |
| `contact_events` | session\_id, shop\_id, channel, created\_at | Clics d'appel et de WhatsApp |
| `feedback` | session\_id, shop\_id, part\_found, diagnosis\_correct, comment | Retours utilisateurs |

**Règles**

- Toute information sur un magasin garde sa `source` (terrain, osm, declared, observed) et sa date.
- `shop_categories.source = observed` est écrit automatiquement quand un magasin répond « disponible » ou qu'un client confirme avoir trouvé la pièce.
- `knowledge_chunks.license` est obligatoire : aucune donnée sans licence connue n'entre dans la base.
- `diagnosis_sessions.model_version` permet de comparer les variantes de la section 6.

## 9. API

API REST en JSON, préfixe `/api/v1`, documentation OpenAPI générée automatiquement.

| Méthode et chemin | Rôle | Accès |
| --- | --- | --- |
| `GET /vehicles/brands`, `/vehicles/models`, `/vehicles/variants` | Listes pour la sélection du véhicule | Public |
| `POST /diagnosis` | Texte, véhicule, codes OBD → causes, pièces, questions | Public, limité en débit |
| `POST /diagnosis/{id}/answers` | Réponses aux questions de précision → résultat affiné | Public |
| `GET /dtc/{code}` | Explication d'un code OBD-II | Public |
| `GET /parts/categories`, `GET /parts/search?q=` | Taxonomie et recherche de pièce, synonymes compris | Public |
| `GET /shops/recommend?category_id=&variant_id=&lat=&lng=` | Magasins classés, avec la raison du score | Public |
| `GET /shops/{id}` | Fiche magasin | Public |
| `POST /contact-events` | Enregistre un appel ou un clic WhatsApp | Public |
| `POST /feedback` | Pièce trouvée, diagnostic correct | Public |
| `POST /auth/otp/request`, `POST /auth/otp/verify` | Connexion par téléphone | Public |
| `POST /shops`, `PATCH /shops/{id}`, `POST /shops/{id}/claim` | Inscription, modification, revendication d'une fiche | Magasin |
| `POST /shops/{id}/products`, `POST /shops/{id}/products/import` | Ajout et import du catalogue | Magasin |
| `POST /part-requests`, `POST /part-requests/{id}/responses` | Demande diffusée et réponse (V2) | Client, magasin |
| `GET /admin/shops?status=`, `POST /admin/shops/{id}/verify`, `POST /admin/shops/import` | Validation, import CSV, fusion | Administrateur |
| `GET /admin/metrics` | Indicateurs de suivi | Administrateur |

## 10. Exigences non fonctionnelles

| Domaine | Exigence |
| --- | --- |
| Langues | Première version en français seulement. Tous les textes passent par des fichiers de traduction, pour ajouter l'arabe et la darija plus tard |
| Mobile | Conçu d'abord pour téléphone ; application web installable (PWA) ; utilisable sur écran de 360 px de large |
| Réseau faible | Première page légère ; images compressées ; listes consultables hors ligne après un premier chargement |
| Performance | Recherche de magasins en moins de 1 seconde ; diagnostic en moins de 10 secondes, avec indicateur de progression |
| Simplicité côté magasin | Inscription en moins de 3 minutes ; ajout d'un produit en moins de 30 secondes ; aucune adresse e-mail exigée |
| Sécurité | Connexion par code reçu sur le téléphone ; rôles contrôlés côté serveur ; limitation de débit sur le diagnostic ; secrets hors du dépôt ; journal des actions administrateur |
| Qualité du code | Tests automatiques sur le score de recommandation, l'import CSV et l'API ; intégration continue ; migrations de base versionnées |
| Traçabilité IA | Chaque diagnostic enregistre la version du modèle, les passages utilisés et la réponse, pour audit et réentraînement |
| Coût | Plafond mensuel sur les appels au modèle de langage ; cache des réponses pour les codes OBD et les questions fréquentes |
| Extension | Ajout d'une wilaya par données et configuration, sans changer le code |

**Protection des données personnelles.** L'application traite des numéros de téléphone et des positions. En Algérie, la loi 18-07 impose [une déclaration préalable à l'ANPDP](https://cms.law/en/int/expert-guides/cms-expert-guide-to-data-protection-and-cyber-security-laws/algeria2) pour tout traitement de données personnelles ; elle a été [modifiée par la loi 25-11 de juillet 2025](https://natlex.ilo.org/dyn/natlex2/r/natlex/fe/details?p3_isn=107253), qui prévoit notamment [la désignation d'un délégué à la protection des données](https://www.tsa-algerie.com/protection-de-donnees-personnelles-nouvelle-obligation-en-algerie/). À faire valider par un juriste avant la commercialisation. Côté produit : consentement explicite, collecte minimale, suppression du compte sur demande, pas de position enregistrée sans accord.

## 11. Plan de réalisation pour Claude Code

Douze étapes, à réaliser dans l'ordre, une par session de travail. Une étape n'est finie que lorsque son critère est vérifié par un test ou une démonstration.

**Mode d'emploi**

1. Exporter ce document en Markdown et le placer dans le dépôt sous `docs/cahier-des-charges.md`.
2. Créer à la racine un fichier `CLAUDE.md` qui résume les conventions (section « Consignes » ci-dessous) et renvoie vers ce document.
3. À chaque session, demander : « Lis `docs/cahier-des-charges.md`, réalise l'étape N, écris les tests, puis montre-moi comment vérifier le critère de fin. »
4. Faire proposer un plan avant tout code pour les étapes 5 à 8, qui portent les choix d'IA.

**Étape 0 — outils de Claude Code (avant l'étape 1)**

Claude Code doit travailler avec ses skills et avec un graphe du projet, pour ne pas relire tous les fichiers à chaque session et ne pas consommer des crédits pour rien.

1. **Installer Graphify** (Python 3.10 ou plus) : `pip install graphifyy && graphify install`. Le paquet s'appelle `graphifyy` sur PyPI, la commande reste `graphify`. Vérifier que `/graphify` apparaît dans Claude Code.
2. **Construire le graphe** : lancer `/graphify .` à la racine du dépôt. Il crée un dossier `graphify-out/` avec `graph.json` (le graphe), `GRAPH_REPORT.md` (résumé : modules centraux, regroupements) et `graph.html` (vue interactive). Le code est analysé par arbre syntaxique, sans appel à un modèle ; seuls les documents (cahier des charges, notes, PDF) passent par un modèle.
3. **Forcer son usage** : lancer une fois `graphify claude install`. Cela ajoute des règles dans `CLAUDE.md` et un crochet qui rappelle à Claude, avant chaque recherche dans les fichiers, de lire d'abord `graphify-out/GRAPH_REPORT.md`.
4. **Garder le graphe à jour** : relancer la mise à jour incrémentale à la fin de chaque étape, après les tests et avant le commit. Un graphe périmé donne de mauvaises réponses.
5. **Commiter `graphify-out/`** (sauf `graph.html` s'il est lourd) pour que le graphe suive le dépôt et serve aux deux membres du binôme.

Limite à connaître : le graphe sert à comprendre et à retrouver le code, pas à l'écrire. Pour modifier un fichier, Claude doit toujours lire ce fichier.

**Skills à utiliser**

Au début de chaque étape, Claude liste les skills disponibles et charge tous ceux qui s'appliquent avant d'écrire du code. Les noms exacts dépendent de l'installation : vérifier avec la liste des skills de Claude Code.

| Besoin | Skill ou outil | Étapes |
| --- | --- | --- |
| Comprendre le dépôt sans tout relire | Graphify (`/graphify`) | Toutes |
| Interface soignée, cohérente, adaptée au mobile | Skill de conception d'interface (frontend-design) | 9, 10 |
| Test du parcours dans un vrai navigateur | Skill ou outil de test web (Playwright) | 9, 10, 11 |
| Graphiques et tableau d'indicateurs | Skill de visualisation de données | 7, 11 |
| Import et export Excel du catalogue, tableaux de résultats | Skill tableur (xlsx) | 4, 7, 10 |
| Mémoire, présentation de soutenance, fiches PDF | Skills Word, PowerPoint et PDF | Hors dépôt, de l'étape 8 à la soutenance |
| Revue de code et revue de sécurité (connexion par SMS, droits, données personnelles) | Commandes de revue intégrées | 2, 10, 12 |
| Écrire de nouveaux skills du projet (par exemple « ajouter une source de données avec sa licence ») | Skill de création de skills | 6 |

Règle : si un skill existe pour la tâche, Claude l'utilise au lieu de réinventer la méthode ; s'il n'en existe pas, il le dit avant de continuer.

| Étape | Livrable | Critère de fin |
| --- | --- | --- |
| 1. Socle | Dépôt mono-repo (`backend/`, `frontend/`, `data/`, `ml/`, `docs/`), Docker Compose avec PostgreSQL, PostGIS et pgvector, intégration continue | `docker compose up` démarre l'API et la base sur le portable ; un test passe en intégration continue |
| 2. Schéma | Migrations de toutes les tables de la section 8 ; communes de la ville d'Oran chargées | Migrations rejouables sur une base vide |
| 3. Référentiels | Marques et modèles prioritaires ; taxonomie des pièces à deux niveaux avec synonymes ; codes OBDex importés et traduits en français | `GET /dtc/P0420` répond en français ; la recherche « plaquettes » renvoie la bonne famille |
| 4. Annuaire | Back-office administrateur, import CSV, script Overpass pour OpenStreetMap, formulaire de collecte terrain sur téléphone | Un magasin saisi sur téléphone apparaît sur la carte |
| 5. Recommandation | Service de score de la section 6.4, point d'entrée `/shops/recommend`, raisons du classement | Tests unitaires sur dix scénarios de classement écrits à la main |
| 6. Données de diagnostic | Scripts de téléchargement, de nettoyage et de traduction (NHTSA, MOT britannique, RappelConso, Stack Exchange, jeu chinois), correspondance vers la taxonomie, base de connaissances indexée | Pipeline rejouable par une commande ; fiche de chaque source avec sa licence |
| 7. Modèles | Carnets Kaggle : référence TF-IDF, mmBERT affiné, modèle de langage affiné par LoRA ; carnet d'expériences | Tableau de résultats top-1 et top-3 reproductible ; poids exportés et chargés sur le portable |
| 8. Chaîne de diagnostic | Point d'entrée `/diagnosis` avec sortie JSON validée, questions de précision, règles de sûreté ; référence exacte sur les modèles pilotes | 20 cas de démonstration passent ; une entrée hors sujet reçoit « je ne sais pas » ; aucune référence n'est générée |
| 9. Application | Parcours automobiliste et mécanicien, carte, contact WhatsApp, saisie vocale, site installable | Parcours de bout en bout sur téléphone ; test automatisé du parcours principal |
| 10. Espace magasin | Inscription, revendication de fiche, catalogue, import Excel | Un magasin test publie 20 produits |
| 11. Retours et tests | Enregistrement des contacts et des retours, page d'indicateurs, essais avec des mécaniciens et des magasins d'Oran | Un retour « pièce trouvée » modifie le score ; compte rendu des essais |
| 12. Mise en ligne | Déploiement, sauvegardes, surveillance, guide pour les magasins | Lancée seulement sur décision de l'équipe |

**Consignes à recopier dans `CLAUDE.md`**

- Backend en Python avec FastAPI, SQLAlchemy et Alembic ; frontend en Next.js avec TypeScript ; base PostgreSQL.
- Aucune donnée externe sans licence notée dans `data/SOURCES.md`.
- Tout texte d'interface passe par les fichiers de traduction (français, arabe).
- Le modèle de langage est appelé derrière une interface unique, pour pouvoir changer de fournisseur.
- Chaque point d'entrée a un test ; chaque script de données est rejouable.
- Ne jamais inventer de magasin, de prix ou de référence de pièce : données de démonstration clairement marquées comme fictives. Une référence de pièce est toujours lue dans une table, jamais générée par un modèle.

* Avant de chercher dans le code, lire `graphify-out/GRAPH_REPORT.md` et interroger le graphe ; ne relire un fichier que pour le modifier.
* Mettre à jour le graphe (`/graphify`, mode incrémental) à la fin de chaque étape, avant le commit.
* Au début de chaque étape, lister les skills disponibles et charger ceux qui s'appliquent (section « Étape 0 »).

**Pour le PFE.** Les étapes 1 à 11 forment le prototype à soutenir, testé en local. Les étapes 6 à 8 portent la contribution scientifique. L'étape 12 attend le feu vert de l'équipe.

**Calendrier**

&#91;embedded content: calendrier · 10 phases, novembre 2026 à juin 2027\]

La collecte terrain démarre dès la deuxième semaine : c'est la tâche la plus longue et la seule qui ne dépend pas du code. Les trois premières semaines de janvier sont réservées aux examens (bande grisée) : seuls des traitements Kaggle sans surveillance, comme la traduction des corpus, tournent pendant ce temps.

**Si le calendrier glisse**, retirer dans cet ordre : la demande diffusée (F16), la saisie vocale (F13), puis le pilote de référence exacte (F14). Le diagnostic entraîné, l'annuaire et la recommandation ne se retirent pas : ils sont le sujet.

## 12. Idées complémentaires

Classées par rapport valeur / effort, de la plus rentable à la plus lourde.

| Idée | Pourquoi | Quand |
| --- | --- | --- |
| Demande diffusée aux magasins (déjà en F16) | Résout l'absence de stock à jour ; crée de la donnée à chaque réponse | V2, à avancer si possible |
| Robot WhatsApp pour les magasins | Les commerçants répondent déjà sur WhatsApp ; évite d'installer quoi que ce soit | V2 |
| Mode mécanicien « recherche express » | Le mécanicien connaît la pièce ; il veut le magasin en deux clics. C'est probablement l'usage le plus fréquent | MVP (parcours direct) |
| Casses automobiles et pièces d'occasion | Souvent la seule source pour les véhicules anciens | V2, simple ajout d'un type de magasin |
| Fourchette de prix indicative par pièce | Aide l'automobiliste à ne pas surpayer ; alimentée par les réponses des magasins | V2 |
| Annuaire des mécaniciens par spécialité | Après la pièce, il faut quelqu'un pour la monter | V2 |
| Carnet d'entretien du véhicule | Fait revenir l'utilisateur ; rappels de vidange, de courroie | V3 |
| Photo de la pièce usée → famille de pièce | Utile quand le client ne connaît pas le nom de la pièce | V3 |
| Lecture d'un boîtier OBD Bluetooth | Supprime la saisie manuelle du code | V3 |
| Tableau de bord de la demande | Montre aux grossistes quelles pièces sont cherchées et introuvables à Oran ; piste de revenus | V3 |

## 13. Risques et questions ouvertes

Le risque principal n'est pas technique : c'est d'obtenir et de garder à jour les données des magasins.

| Risque | Conséquence | Réponse |
| --- | --- | --- |
| Les magasins ne mettent pas à jour leur catalogue | Recommandations fausses, perte de confiance | Recommander d'abord par marque et famille ; demandes diffusées ; score de fraîcheur |
| Les données d'entraînement ne couvrent ni les marques locales ni la darija | Diagnostic médiocre sur les cas réels | Cas collectés chez des mécaniciens d'Oran, lexique local, jeu de test local |
| Diagnostic erroné présenté comme sûr | Pièce achetée pour rien, danger sur les organes de sécurité | Seuil de confiance, plusieurs causes, messages de sûreté, avis du mécanicien recommandé |
| Démarrage à froid : peu de magasins, donc peu de clients, donc peu de magasins | Le produit ne décolle pas | Lancer dense sur quelques communes ; commencer par les mécaniciens, qui cherchent des pièces chaque jour |
| Usage de données sans droit (forums, catalogues, cartes) | Risque juridique, retrait de données | Champ licence obligatoire ; accords écrits ; sources ouvertes d'abord |
| Coût du modèle de langage à l'échelle | Budget dépassé | Cache, classifieur local en premier, plafond mensuel |
| Périmètre trop large pour un PFE | Prototype inachevé | Soutenir les étapes 1 à 11 ; ordre de retrait fixé sous le calendrier de la section 11 |

**Questions à trancher avant de coder**

- [ ] Prendre rendez-vous avec l'incubateur de l'USTO : modèle de mémoire, grille d'évaluation à jour, label « Projet innovant »
- [ ] Vérifier à l'INAPI que le nom DALIL est libre avant de le fixer
- [ ] Choisir le modèle de revenus (nécessaire pour l'axe 5 du mémoire) : mise en avant, abonnement magasin, données de demande
- [ ] Choisir l'hébergement et le fournisseur de SMS, au moment de la mise en ligne
- [ ] Relever la mémoire vidéo de la RTX 3050 (non bloquant : l'entraînement se fait sur Kaggle)

## 14. Protection du projet et statut de startup

Un logiciel se protège surtout par le droit d'auteur, la marque et le secret ; le brevet est incertain pour un programme seul. Ce qui suit n'est pas un avis juridique : à faire confirmer par l'incubateur de l'université ou par l'INAPI.

| Outil | Ce qu'il protège | Organisme | À savoir |
| --- | --- | --- | --- |
| Droit d'auteur | Le code, dès sa création | ONDA | [L'ordonnance 03-05 couvre les programmes d'ordinateur](https://www.inpi.fr/sites/default/files/2025-09/Fiche%20PI%20Algerie%202025.pdf). Garder l'historique du dépôt de code comme preuve de date |
| Marque | Le nom et le logo | INAPI | [Ordonnance 03-06](https://algeriatech.news/?p=2296). À déposer avant la mise en ligne |
| Brevet | Une invention technique | INAPI | Ordonnance 03-07. La doctrine algérienne relève [le rejet de la brevetabilité du logiciel](https://www.asjp.cerist.dz/en/downArticle/86/2/3/6413) ; à vérifier avant d'engager des frais |
| Secret | Les données d'Oran et les poids des modèles | L'équipe | Dépôt privé, accès limités. C'est l'actif le plus difficile à copier |

**Dispositif « un diplôme, une startup ».** L'[arrêté ministériel n° 1275 du 27 septembre 2022, modifié en février 2025](https://fac.umc.edu.dz/fse/fr/page~slug-texte-reg-g.php), permet de soutenir le PFE comme projet de startup ou de brevet. Selon la [synthèse d'un incubateur universitaire](https://www.univ-saida.dz/downloads/incubator/arrete-1275.pdf), il ouvre le dépôt du label « Projet innovant », un accès facilité aux financements et l'accompagnement gratuit de l'incubateur.

**Conséquence pour le mémoire.** Le PFE est inscrit dans ce dispositif. Le [guide ministériel](https://elearning-facsci.univ-annaba.dz/mod/resource/view.php?id=30484) organise le mémoire en six axes. Une [présentation universitaire de 2022](https://www.univ-mosta.dz/fss/wp-content/uploads/sites/10/2022/11/Mecanismes-accompagnement-startup.pdf) indiquait comme poids d'évaluation : innovation 25 %, solidité du modèle économique 30 %, prototype 25 %. Le texte ayant été modifié en 2025, ces poids sont à confirmer auprès de l'incubateur.

| Axe du mémoire | Déjà couvert par | Reste à produire |
| --- | --- | --- |
| 1. Présentation du projet | Sections 1 et 2 | Fiche de l'équipe et de l'encadrement |
| 2. Aspects innovants | Sections 5 et 6 | Comparaison avec l'existant : annonces en ligne, catalogues, lecteurs OBD |
| 3. Analyse stratégique du marché | Marques et parc (section 5) | Nombre de magasins et de garages à Oran, entretiens, concurrence |
| 4. Plan de production et d'organisation | Sections 7 et 11 | Répartition des rôles, partenaires |
| 5. Plan financier | Rien | Coûts, revenus, seuil de rentabilité, modèle économique |
| 6. Prototype expérimental | Sections 3 et 6 à 11 | Le prototype et ses mesures |

**Le terrain sert deux fois.** Chaque visite de magasin alimente l'annuaire et l'étude de marché. Ajouter trois questions au formulaire : combien de demandes par jour, comment les clients vous trouvent, seriez-vous prêt à payer pour être mis en avant.

## 15. Sources

Pages consultées le 13 novembre 2026.

- [NHTSA – ODI Complaints, catalogue data.gov](https://catalog.data.gov/dataset/nhtsas-office-of-defects-investigation-odi-complaints)
- [NHTSA – Manufacturer Communications, description des fichiers](https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS.txt)
- [NHTSA – ODI Recalls, catalogue data.gov](https://catalog.data.gov/dataset/nhtsas-office-of-defects-investigation-odi-recalls-complaints-flat-file)
- [NHTSA – API vPIC](https://vpic.nhtsa.dot.gov/api/)
- [OBDex – base ouverte des codes OBD-II](https://github.com/foerbsnavi/OBDex)
- [Stack Exchange Data Dump 2025-12-31, Internet Archive](https://archive.org/details/stackexchange_20251231)
- [Stack Exchange – licence des contenus et export](https://stackoverflow.blog/2014/01/23/stack-exchange-cc-data-now-hosted-by-the-internet-archive/)
- [DziriBERT, Hugging Face](https://huggingface.co/alger-ia/dziribert)
- [Jeu de données de diagnostic automobile, Hugging Face](https://huggingface.co/datasets/build-small-hackathon/nemotron-car-diagnostics-datasets)
- [OpenStreetMap – balise shop=car\_parts](https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_parts)
- [Ouedkniss – pièces automobiles](https://www.ouedkniss.com/pieces_detachees-pieces_automobiles/1)
- [Planète Renault – forum technique mécanique](https://www.planeterenault.com/forum/technique-mecanique-f3-240.html)
- [TecDoc – licence et intégration](https://dev-opla.com/resources/what-is-tecdoc-auto-parts-ecommerce-guide)
- [Atlas Magazine – parc automobile algérien 2018 (ONS)](https://atlas-mag.net/fr/articles/algerie-le-parc-national-automobile-en-2018)
- [CMS – guide de la protection des données en Algérie](https://cms.law/en/int/expert-guides/cms-expert-guide-to-data-protection-and-cyber-security-laws/algeria2)
- [NATLEX – loi 18-07 et loi modificative 25-11](https://natlex.ilo.org/dyn/natlex2/r/natlex/fe/details?p3_isn=107253)
- [TSA – délégué à la protection des données](https://www.tsa-algerie.com/protection-de-donnees-personnelles-nouvelle-obligation-en-algerie/)

* [mmBERT, Hugging Face](https://huggingface.co/blog/mmbert)
* [Comparatif des modèles de vecteurs 2026](https://www.datallmlab.com/blog/best-embedding-models.html)
* [Audit de fiabilité des scores MTEB, AACL 2026](https://aclanthology.org/2026.aacl-short.28.pdf)
* [Comparatif des modèles de reclassement 2026](https://futureagi.com/blog/best-rerankers-for-rag-2026/)
* [Modèles locaux multilingues, avril 2026](https://www.promptquorum.com/local-llms/multilingual-local-llms)
* [Traduction de dialectes arabes, modèles affinés](https://arxiv.org/pdf/2507.20301)
* [NADI 2025, reconnaissance vocale multi-dialectes](https://arxiv.org/abs/2511.10090v1)
* [awras-chat-v0, Hugging Face](https://huggingface.co/awras/awras-chat-v0)
* [algerianDeBERTa, Hugging Face](https://huggingface.co/81melody/algerianDeBERTa)

- [DVSA – données MOT anonymisées](https://open.data.dvsa.gov.uk/mot-anonymised/index.html)
- [Rappels Safety Gate 2025](https://car-recalls.eu/2025-safety-gate-recalls-overall-table/)
- [Chinese Vehicle Fleet Fault Association Dataset, Mendeley Data](https://data.mendeley.com/datasets/r98g7g6k5t/1)
- [Top 10 des modèles vendus en Algérie en 2014, Journal de l'Automobile](https://journalauto.com/data-center/le-top-10-des-modeles-les-plus-vendus-en-algerie/)
- [Marché algérien 2015, Best Selling Cars Blog](https://bestsellingcarsblog.com/2016/01/algeria-full-year-2015-dacia-logan-holds-off-renault-symbol-for-now/)
- [Marché algérien 2025, Focus2Move](https://www.focus2move.com/algerian-vehicles-sales/)
- [Importations de véhicules chinois en 2026, Algérie360](https://www.algerie360.com/voitures-chinoises-algerie-190000-vehicules-8-mois/)
- [GPU gratuits en 2026](https://gpuperhour.com/blog/free-cloud-gpus-and-credits)
- [Fiche propriété intellectuelle Algérie, INPI](https://www.inpi.fr/sites/default/files/2025-09/Fiche%20PI%20Algerie%202025.pdf)
- [Arrêté 1275, synthèse de l'incubateur de l'université de Saïda](https://www.univ-saida.dz/downloads/incubator/arrete-1275.pdf)
