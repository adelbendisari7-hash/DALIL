# Mise en ligne de DALIL (étape 12) : plan et décisions

Préparé le 28/11/2026. **Rien n'est acheté ni publié** : ce plan sert à décider. Les prix viennent de pages publiques
consultées ce jour, souvent contradictoires d'une page à l'autre : **à confirmer par un devis** avant toute décision.

## En bref

- **Recommandation : héberger DALIL en Algérie**, sur un serveur virtuel de **4 cœurs et 12 Go de mémoire**. La loi
  18-07 soumet l'envoi de données personnelles à l'étranger à une autorisation de l'ANPDP ; un hébergement en Algérie
  l'évite. Coût public indicatif : environ 24 000 DZD HT par mois chez ICOSNET pour cette taille (centres de données
  d'Alger et d'Oran), à confirmer.
- **Le logiciel est prêt à être déployé** : fichiers de production, https automatique, sauvegardes, réglages de
  sécurité (voir « Ce qui est prêt »). La première installation sur un serveur reste à faire, et le diagnostic doit
  y être chronométré : le serveur a moins de cœurs que le portable.
- **Avant d'ouvrir au public** : déclaration à l'ANPDP, accords écrits des sources, données de démonstration
  supprimées (liste complète plus bas).

## Les décisions qui vous reviennent

| Décision | Options | Recommandation |
| --- | --- | --- |
| Où héberger | En Algérie (ICOSNET, Algérie Télécom, autres) ; à l'étranger (moins cher, mais autorisation de l'ANPDP) | En Algérie |
| Taille du serveur | 8 Go (juste) ; 12 Go (confortable) | 12 Go, 4 cœurs |
| Nom de domaine | En .dz (règles d'attribution à vérifier auprès du registre) ; en .com | À décider ; le .dz rassure les utilisateurs algériens |
| Qui administre | Un membre de l'équipe (mises à jour, sauvegardes, surveillance) | À désigner avant l'ouverture |
| Date d'ouverture | Avant ou après les essais d'Oran | Après les essais : les magasins et garages vérifiés sur le terrain font la valeur de DALIL |

## La contrainte légale

- **Loi 18-07** (JO n° 34 du 10/06/2018), article 44 : le responsable d'un traitement ne peut transférer des données
  personnelles vers un État étranger que sur **autorisation de l'ANPDP**, et si cet État assure un niveau de
  protection suffisant ; l'article 45 prévoit des dérogations. La **loi 25-11 du 24/07/2025** a modifié ce régime
  (articles 45 bis) : **lire le texte officiel**, les commentaires consultés ne s'accordent pas sur le détail.
- **Déclaration préalable à l'ANPDP** avant toute ouverture, quel que soit l'hébergeur. DALIL traite : numéro de
  téléphone, prénom et nom, e-mail et date de naissance facultatifs, matricule et numéro de châssis des voitures,
  carnet d'entretien, contrôle technique et assurance (dates, prestataire, prix), demandes de pièces avec photo,
  empreinte de l'adresse IP (jamais l'adresse elle-même), position arrondie à 1 km dans les statistiques.
  Les mesures de protection sont décrites au chapitre 5.3 du mémoire (suppression du compte, collecte minimale).

## Dimensionnement (mesuré sur le portable le 28/11/2026)

| Élément | Mesure |
| --- | --- |
| Mémoire de l'API au chargement des modèles | 5,1 Go au pic |
| Modèles de production à copier sur le serveur | environ 2,3 Go (`qwen3-embedding-0.6b`, `bge-reranker-v2-m3`, vecteurs, classifieur) |
| Diagnostic complet, téléphone en 3G | 3,7 s (portable à 12 cœurs) |
| Base, site, système | environ 2 Go de plus |

Avec 8 Go, le serveur tourne sans marge ; **12 Go** laissent de la place à PostgreSQL et aux mises à jour. Le
diagnostic sera plus lent sur 4 cœurs que sur le portable : à chronométrer dès l'installation (objectif du cahier :
moins de 10 s). S'il dépasse, réglage prévu : `DALIL_RETRIEVAL_QUERY_CHARS=400` (voir `ml/README.md`).

## Hébergeurs consultés (prix publics du 28/11/2026, à confirmer)

| Offre | Où | Taille | Prix affiché |
| --- | --- | --- | --- |
| ICOSNET VPS S | Alger, Oran | 1 cœur, 4 Go, 80 Go | 5 500 DZD HT/mois (d'autres pages affichent 7 950 DZD) |
| ICOSNET (offre intermédiaire) | Alger, Oran | 4 cœurs, 12 Go | 23 900 DZD HT/mois |
| Algérie Télécom (VPS) | Algérie | non trouvée | aucun prix public trouvé |
| Hetzner (CX33 / CPX31) | Allemagne, Finlande | 4 cœurs, 8 Go | environ 9 à 19 €/mois selon la page ; ouverture de comptes restreinte depuis juin 2026 ; **autorisation de l'ANPDP nécessaire** |

L'offre de 4 Go ne suffit pas (5,1 Go pour l'API seule).

## Ce qui est prêt (28/11/2026)

- **Intégration continue verte** : à chaque envoi, les migrations montent, descendent et remontent sur un vrai
  PostgreSQL avec PostGIS et pgvector, puis tous les tests passent. Elle échouait depuis au moins le 26/11 (image de
  base obsolète) : corrigé.
- **`deploy/docker-compose.prod.yml`** : base, API (avec les modèles), site, et le frontal **Caddy**, seul ouvert
  sur Internet, qui obtient et renouvelle le certificat **https** tout seul.
- **`deploy/Caddyfile`** : en-têtes de sécurité (HSTS, anti-cadre, anti-reniflage, droits du micro, de la position
  et de l'appareil photo limités à DALIL), taille des envois limitée.
- **Adresse réelle des clients** : derrière le frontal, l'API lit l'adresse du client dans un en-tête que le
  frontal écrase toujours, et ne le croit que venant du serveur. Sans cela, les limites d'essais et le décompte
  « une fois par client » auraient traité tous les visiteurs comme un seul.
- **Refus de démarrer avec des réglages de développement** (`DALIL_ENV=production`) : clé secrète par défaut ou trop
  courte, code de connexion des tests, mot de passe de base par défaut, SQLite.
- **Aucune donnée de démonstration** créée en production (`--no-demo`).
- **`deploy/sauvegarde.sh`** : base et photos chaque nuit, 14 jours gardés, procédure de restauration en tête du
  script.
- L'intégration continue construit aussi les images de production et vérifie que les modèles s'y importent.

## Pas à pas, le jour venu

1. Louer le serveur (Linux récent), y installer Docker, ouvrir les ports 80 et 443.
2. Faire pointer le nom de domaine vers l'adresse du serveur.
3. Copier le dépôt, puis `ml/artifacts/` (les modèles, hors git) et `data/` (référentiels).
4. Dans `deploy/`, copier `env.exemple` en `.env` et le remplir (secrets tirés au hasard ; jamais dans git).
5. `docker compose -f docker-compose.prod.yml --env-file .env up -d --build`.
6. Charger la base de connaissances et ses vecteurs (`python data/pipeline/run.py load`, puis
   `python ml/load_vectors.py`). **Pas encore essayé sur un serveur** : ces scripts tournent sur le portable, avec
   les dépendances du pipeline (`data/pipeline/requirements.txt`) que l'image de l'API n'installe pas. Le plus
   simple : les lancer depuis le portable vers la base du serveur (accès temporaire et chiffré), ou les ajouter à une
   image d'outils. À régler lors de la première installation.
7. Vérifier `https://<domaine>/api/v1/health` : `ready` vrai et `models` à `true` pour les deux modèles.
8. Chronométrer un diagnostic ; dérouler `docs/test-telephone.md` sur un vrai téléphone, en https : la dictée,
   l'installation et le hors-ligne complet doivent maintenant fonctionner.
9. Programmer `sauvegarde.sh` chaque nuit et copier les sauvegardes sur une autre machine ; faire un essai de
   restauration.
10. Mettre en place une surveillance simple (un service qui vérifie l'adresse de santé toutes les 5 minutes et
    prévient l'administrateur).

## À faire avant d'ouvrir au public

- [ ] Déclaration à l'ANPDP déposée (et autorisation si l'hébergement est à l'étranger).
- [ ] Accords écrits archivés : L'Argus, Techniconnexion, Ouedkniss (sans écrit : retirer les données concernées,
      dont le jeu privé envoyé sur Kaggle).
- [ ] Données de démonstration supprimées : `python -m app.seed --purge-demo` (magasins, garage et compte de
      démonstration).
- [ ] Magasins et garages vérifiés sur le terrain (seules les fiches vérifiées sont proposées).
- [ ] Jeton Kaggle révoqué ou remplacé.
- [ ] Administrateurs définis (`DALIL_ADMIN_PHONES`) et procédure « mot de passe oublié » connue de l'équipe.
- [ ] Mentions légales et politique de confidentialité publiées sur le site (à rédiger).

## Après l'ouverture (à développer, maintenant possible grâce au https)

- **Notifications envoyées par DALIL** (rappels d'assurance et de contrôle technique, réponses des magasins, baisses
  de prix) : notifications web, qui demandent le https et un petit service d'envoi.
- **SMS** (vérification du numéro) : seulement si un fournisseur et un budget sont choisis ; le code est prêt.

## Sources consultées

- [Loi 18-07, texte (JO n° 34 du 10/06/2018)](https://www.upgrowth.dz/journal-officiel/loi-18-07-protection-donnees-personnelles)
- [Gide, protection des données personnelles en Algérie](https://www.gide.com/en/news-insights/protection-of-personal-data-focus-on-algerian-regulations/)
- [DLA Piper, Data Protection in Algeria](https://www.dlapiperdataprotection.com/?c=DZ&t=law)
- [Comparaison des régimes de transfert, lois 18-07 et 25-11 (Université de M'Sila)](https://journals.univ-msila.dz/index.php/JTRLPS/article/view/6347)
- [ICOSNET, serveurs VPS en Algérie](https://icosnet.com.dz/en/vps-en/)
- [Comparatif VPS Algérie 2026](https://zoomalgerie.com/vps-algerie-serveur-cloud/)
- [Hetzner, ajustement des prix 2026](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/)
- [Better Stack, revue Hetzner 2026](https://betterstack.com/community/guides/web-servers/hetzner-cloud-review/)
