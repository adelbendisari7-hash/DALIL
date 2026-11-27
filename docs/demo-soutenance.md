# Démonstration de DALIL pour la soutenance (5 minutes)

Fiche pour l'équipe qui présente. Tout ce qui est montré est **fictif et marqué [DÉMO]** : magasins, garage, compte
client, voiture, prix. Le dire au jury dès le début.

## La veille

1. Lancer `DEMARRER-DALIL.bat` (il met la base à jour). Attendre « DALIL est prêt ».
2. Préparer le compte de démonstration, dans une invite de commandes :
   `cd backend` puis `.venv\Scripts\python -m app.demo_soutenance`
   (rejouable : relancez-le juste avant la soutenance pour remettre les dates à jour).
3. Sur le téléphone de démonstration, ouvrir l'adresse Wi-Fi affichée par le lanceur, puis se connecter une fois avec
   le compte de démonstration : **numéro 0550 00 01 01, mot de passe `demo-soutenance`**.
4. Faire une fois le diagnostic de l'étape 2 ci-dessous : il sera relisible même si le réseau tombe le jour J.
5. Recopier l'écran du téléphone sur le vidéoprojecteur (câble ou partage d'écran), luminosité au maximum.

## Le déroulé

| Temps | Ce qu'on montre | Ce qu'on dit |
| --- | --- | --- |
| 0:00 | L'accueil | À Oran, une panne, c'est deux problèmes : savoir ce qui ne va pas, puis trouver la pièce. DALIL fait les deux, depuis un téléphone. |
| 0:30 | Toucher le voyant **Freins**, ou écrire « ça grince quand je freine », puis **Trouver la panne** | On écrit comme on parle, en français ou en darija. Résultat en quelques secondes : les causes classées, la consigne « ne roulez pas », la pièce et sa référence (fictive ici, toujours lue en base, jamais inventée). |
| 1:30 | **Voir les magasins** | Chaque magasin dit pourquoi il est classé là. Prix comparés, tri par prix, historique des prix sur six mois, avis vérifiés (seulement des clients qui ont vraiment contacté le magasin). |
| 2:00 | **Voir les mécaniciens** | Les garages vérifiés, classés selon leur spécialité : celui qui fait le freinage d'abord. DALIL n'invente jamais le prix de la main-d'œuvre. |
| 2:30 | Revenir à l'**accueil** (compte de démonstration) | Les rappels du jour : assurance qui finit dans 5 jours (en rouge, impossible à masquer), prix des plaquettes en baisse, vidange dépassée. |
| 3:00 | **Mon compte > voiture [DÉMO] Clio** : Entretien, Papiers, Rappels | Le carnet de chaque passage au garage (date, kilométrage, prix), les papiers avec « Ajouter à mon agenda », les rappels publiés par les constructeurs (« rappel possible », à vérifier avec le numéro de châssis). |
| 3:45 | **Vendre** (sans aller au bout) | À la revente, le vendeur donne un code : l'acheteur reprend le carnet, sans l'assurance ni les prix si le vendeur ne le veut pas. |
| 4:15 | Couper le Wi-Fi du téléphone, rouvrir le dernier diagnostic | Au garage, la 3G coupe : le dernier diagnostic et ses magasins restent lisibles, et on peut toujours appeler. |
| 4:40 | Une diapositive de chiffres | Honnêteté : sur de vrais textes de conducteurs (forums), la bonne pièce est dans les trois premières environ deux fois sur trois (64 à 67 % selon le jeu), contre plus de 90 % sur nos propres jeux ; le jeu de test d'Oran donnera le chiffre final. |

Pour aller plus loin si le jury le demande : l'espace magasin (inscription en 5 étapes, catalogue, « Votre semaine »)
se montre avec les captures d'écran (`cd frontend && npx playwright test -c playwright.captures.config.ts`).

## Si quelque chose ne marche pas

- **« DALIL se prépare »** sur l'accueil : les modèles se chargent (environ 1 minute après le lancement). Parler de
  l'étape suivante pendant ce temps.
- **Plus de réseau** : montrer le dernier diagnostic (préparé la veille) et les magasins enregistrés ; c'est justement
  la fonction hors ligne.
- **Le compte de démonstration a été modifié pendant une répétition** : relancer `python -m app.demo_soutenance`.
- **La dictée vocale ne marche pas** sur l'adresse Wi-Fi du PC : c'est normal sans https ; écrire le texte.

## Questions probables

- **Données personnelles ?** Collecte minimale : jamais l'adresse IP (une empreinte seulement), suppression du compte
  qui efface tout, déclaration à l'ANPDP prévue avant la mise en ligne.
- **Pourquoi pas un grand modèle de langage ?** Mesuré : il n'améliorait pas le diagnostic et prenait une minute par
  réponse sur un portable, pour une limite de 10 secondes. Il reste en option pour les mesures.
- **D'où viennent les prix ?** Des catalogues des magasins, jamais estimés ; ici ils sont fictifs.
- **Les magasins sont-ils réels ?** Pas dans cette démonstration. Sur le terrain, chaque fiche est vérifiée par un
  appel de l'équipe avant d'être recommandée.

## Après la soutenance

`cd backend` puis `.venv\Scripts\python -m app.seed --purge-demo` : supprime les magasins, le garage et le compte de
démonstration. Obligatoire avant toute mise en ligne.
