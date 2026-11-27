# Plan : côté magasin (inscription, adresse et carte, catalogue, équipe, statistiques)

Rédigé le 27/11/2026, révisé le même jour avec les décisions de l'utilisateur. **Feu vert donné le 27/11/2026, avec les cinq idées A à E.**
Il complète les fonctions F6, F11, F12 et F18 du cahier des charges et l'étape 11 (essais à Oran).

**Prompt à lancer :**

> Lis `docs/SUIVI.md` puis `docs/plan-espace-magasin.md`, et réalise les phases 1 à 4 dans l'ordre. Pour chaque phase,
> écris les tests, vérifie le critère de fin (tests, vérification « comme un téléphone », captures), mets à jour le
> suivi et commite. Arrête-toi et demande-moi avant tout ce que le plan marque « décision ».

## Décisions prises (27/11/2026)

| Sujet | Décision |
| --- | --- |
| Priorités | Inscription et vérification, catalogue plus rapide, statistiques. Les demandes des clients restent telles quelles |
| Vérification d'un magasin | **Un appel suffit** (pas de registre du commerce pour l'instant) |
| Adresse | **Le magasin donne l'adresse de sa boutique**, qui le place sur la carte |
| Photos des produits | Décision laissée à Claude : voir phase 2 |
| Équipe | **Gérant + employés, sans nombre maximum.** Le gérant seul décide des rôles et des accès de chacun ; **l'équipe DALIL n'intervient pas** dans l'équipe d'un magasin |
| Notifications sur un vrai téléphone | **Plus tard** (avec la mise en ligne en https) |
| Langue arabe | **Plus tard** |
| Terrain | Le plan couvre aussi les visites et l'essai avec les magasins d'Oran |

Rappels du cahier : inscription en moins de 3 minutes, un produit en moins de 30 secondes, aucune adresse e-mail
exigée, ne jamais inventer de magasin, de prix ni de référence.

## Phase 1 — Inscription guidée, adresse et vérification (faite le 27/11/2026)

**Parcours** (le gérant a un compte DALIL ordinaire : prénom, nom, numéro, mot de passe) :

1. **Votre magasin** : nom, téléphone et WhatsApp du magasin, horaires (pastilles « samedi-jeudi 8h-18h » modifiables).
2. **Où est-il ?** Deux façons, au choix :
   - **taper l'adresse** (« 12 rue Larbi Ben M'hidi, Oran ») : DALIL propose les lieux correspondants dans la wilaya
     d'Oran et place une épingle sur la carte ;
   - **« Je suis au magasin »** : position du téléphone.

   Dans les deux cas, le magasin **ajuste l'épingle au doigt** (les adresses d'Oran sont souvent approximatives :
   « en face de la mosquée ») et peut ajouter un repère en texte. La commune est déduite de la position.
   L'adresse et le repère s'affichent sur sa fiche publique et sur la carte des clients.
3. **Fiche déjà connue ?** DALIL cherche les fiches de l'équipe à moins de 150 m ou au même numéro et propose
   « C'est mon magasin » (revendication) plutôt qu'un doublon.
4. **Ce que vous vendez** : marques et familles en pastilles, avec des raccourcis (« toutes les marques françaises »,
   « freinage complet ») ; origine des pièces (origine, adaptable, occasion) ; gros ou détail.
5. **Récapitulatif** puis envoi : « en attente de vérification », avec ce qui va se passer.

**Recherche d'adresse** : service Nominatim d'OpenStreetMap (gratuit, données ODbL déjà citées dans
`data/SOURCES.md`), limité à la wilaya d'Oran, une requête par seconde au plus comme l'exigent ses règles d'usage,
identifiant d'application générique. Seule l'adresse tapée part chez ce service ; si elle n'est pas trouvée, l'épingle
se pose au centre de la commune choisie et le magasin la déplace.

**Vérification par l'administrateur** : file « Magasins à vérifier » avec bouton Appeler et liste de contrôle
(numéro joignable, adresse confirmée, activité réelle) ; Valider, ou Refuser avec un motif montré au magasin. Fiche
validée : badge « Vérifié par DALIL » et sa date ; reconfirmation demandée au bout de six mois.

**Unicité** : le téléphone d'un magasin est unique (même règle que le numéro d'un client et le matricule) ; deux
fiches à moins de 30 m et au nom proche sont signalées à l'administrateur pour fusion.

**Critère de fin** : un magasin test s'inscrit par son adresse en moins de 3 minutes sur téléphone simulé
(chronométré) ; l'épingle se déplace au doigt ; la revendication évite le doublon ; l'administrateur valide ; le
magasin apparaît à la bonne place sur la carte des clients, avec son badge.

## Phase 2 — Catalogue plus rapide (faite le 27/11/2026)

- **Ajout en moins de 30 s** : famille en pastilles (les plus utilisées du magasin en premier), titre proposé d'après
  la famille, compatibilité par le sélecteur de véhicule (plusieurs modèles), prix, état en pastilles, « en stock »
  coché d'office ; « Ajouter et continuer » garde la famille et la compatibilité pour le produit suivant.
- **Liste du catalogue** : recherche, filtre par famille, « en stock / rupture » et prix modifiables en un toucher,
  « prix confirmé il y a N jours ».
- **Import Excel** : aperçu avant d'importer (lignes valides, erreurs ligne par ligne), mise à jour par référence ;
  l'objectif du cahier (500 lignes sans erreur) devient un test.

**Photos des produits (décision prise par Claude)** :

| Choix | Raison |
| --- | --- |
| Une photo par produit, prise ou choisie sur le téléphone | Suffit pour reconnaître une pièce ; simple à saisir |
| Réduite sur le téléphone avant l'envoi : 1 280 px de côté au plus, JPEG, environ 200 Ko | Envoi rapide en 3G ; peu de place sur le serveur |
| Métadonnées retirées (position GPS, modèle du téléphone), sur le téléphone **et** par le serveur | Une photo prise au magasin ou chez soi contient souvent sa position GPS |
| Serveur : JPEG seulement, 1 Mo au plus, contenu vérifié (pas seulement l'extension), nom de fichier tiré au hasard | Pas de fichier dangereux ni de nom deviné |
| Stockées sur le disque du serveur (`data/uploads/produits/`, hors git), derrière une interface unique | Simple aujourd'hui ; passage à un stockage en ligne à la mise en ligne sans toucher au reste |
| Supprimées avec le produit ou le magasin ; incluses dans les sauvegardes de l'étape 12 | Pas de fichier orphelin |
| Aucune reconnaissance automatique de la pièce | La photo illustre, elle ne remplit jamais la fiche (pas de référence inventée) |

Sans nouvelle dépendance (Pillow n'est pas installé) : le téléphone réencode l'image, le serveur retire les segments de
métadonnées du JPEG par une routine courte, testée.

**Critère de fin** : test chronométré « un produit en moins de 30 s » ; import de 500 lignes testé ; photo testée sur
téléphone simulé, sans position GPS dans le fichier stocké.

## Phase 3 — L'équipe du magasin (le gérant décide de tout) (faite le 27/11/2026)

- **Le gérant ajoute autant d'employés qu'il veut** : l'employé crée son compte DALIL, le gérant tape son numéro.
- **Accès à la carte** : pour chaque employé, le gérant coche ce qu'il peut faire :
  répondre aux demandes ; ajouter et modifier des produits ; changer prix et stock ; supprimer des produits ;
  voir les statistiques ; modifier la fiche du magasin. Des modèles prêts à cocher : « Vendeur » (demandes, prix
  et stock), « Responsable » (tout sauf l'équipe).
- **Seul le gérant** gère l'équipe : ajouter, changer les accès, suspendre, retirer, et **passer la main** à un autre
  membre (changement de gérant, confirmé par le mot de passe du gérant).
- **L'équipe DALIL n'a aucun écran pour l'équipe d'un magasin** : elle valide ou refuse le magasin, rien de plus.
- **Journal** : chaque réponse à une demande et chaque modification du catalogue garde son auteur ; le gérant voit qui
  a fait quoi.
- Un compte supprimé quitte toutes les équipes ; un employé retiré perd l'accès immédiatement.

**Critère de fin** : tests des droits, un par case (un vendeur ne peut pas modifier la fiche ni l'équipe ; un employé
retiré n'a plus accès ; un administrateur DALIL ne peut pas modifier une équipe) ; parcours e2e : le gérant ajoute un
vendeur, le vendeur répond à une demande, le journal l'affiche.

## Phase 4 — Statistiques du magasin

- **Événements enregistrés**, sans donnée personnelle (empreinte du client, comme pour « pièce trouvée ») :
  apparition dans un classement, fiche ouverte, appel, WhatsApp, demande reçue, réponse (et délai), « pièce trouvée ».
- **Tableau de bord** (30 derniers jours, comparé au mois précédent) : apparitions, vues, appels et WhatsApp, demandes
  reçues et répondues, délai moyen de réponse, retours « trouvée ».
- **« Ce que cherchent les clients près de chez vous »** : pièces et modèles les plus diagnostiqués et cherchés dans la
  commune et alentour, et la part que le magasin ne vend pas encore.
- Visible par le gérant et par les employés à qui il en donne l'accès.
- **Compteur des demandes en attente** sur l'onglet « Magasin » de la barre d'onglets (les notifications viendront
  avec la mise en ligne).

**Critère de fin** : chaque événement a un test ; le tableau affiche des chiffres justes sur une base de test connue.

## Terrain (équipe), à partir de la fin de la phase 2

1. **Préparer** : guide d'une page pour les magasins (pourquoi s'inscrire, comment, ce que DALIL fait des données),
   script de l'appel de vérification, liste de visite (`data/terrain/liste_visite_osm.xlsx`).
2. **Visiter** les 23 magasins de pièces repérés sur OpenStreetMap, puis ceux qui n'y sont pas ; question « les dix
   modèles qui vous font le plus vendre ».
3. **Essai chronométré** avec 5 à 10 magasins (protocole `docs/essais-oran.md`) : inscription par l'adresse, 3 produits
   avec photo, réponse à une demande test, ajout d'un employé ; noter les blocages.
4. **Compte rendu** (`docs/compte-rendu-essais.md`) ; ses constats ajustent les phases 3 et 4.

**Critère de fin** (étape 11) : 20 magasins ou plus dans DALIL avant la soutenance, dont une partie inscrits par
eux-mêmes ; temps mesurés.

## Idées proposées par Claude — toutes retenues par l'utilisateur (27/11/2026)

| Idée | Ce que ça apporte | Où |
| --- | --- | --- |
| **A. Affiche « Trouvez-nous sur DALIL »** avec QR code, à imprimer pour le comptoir | Le magasin fait venir ses clients sur DALIL ; utile pendant les visites | Phase 1 |
| **B. « Ouvert maintenant »** d'après les horaires, et bouton « Fermé exceptionnellement » (congé, Aïd) | Le client n'appelle pas un magasin fermé ; le magasin garde la main | Phase 1 |
| **C. Photo de la devanture** sur la fiche publique | Le client reconnaît la boutique dans la rue ; même traitement que les photos de produits | Phase 2 |
| **D. Badge « Répond vite »** quand le magasin répond à la plupart des demandes en moins d'une heure | Récompense les magasins actifs ; signal de plus pour le classement | Phase 4 |
| **E. Rappel de mise à jour** : « 12 prix n'ont pas été confirmés depuis 60 jours » | Catalogue à jour sans effort ; évite d'envoyer un client pour rien | Phase 4 |

## Reporté (décidé)

- Notifications sur un vrai téléphone (Web Push) : avec la mise en ligne en https (étape 12).
- Espace magasin en arabe : avec la traduction de l'interface.
- Pièces justificatives (registre du commerce) : si l'appel ne suffit plus.

## Estimation

Une session par phase (1 à 4) ; les idées retenues ajoutent chacune une petite part de leur phase. Terrain : selon
l'équipe, en parallèle des phases 3 et 4.
