# Étape 9 : vérification sur un vrai téléphone

Critère de fin de l'étape 9 (section 11) : parcours de bout en bout sur téléphone, plus un test automatisé du parcours principal.

- **Test automatisé** : fait, `cd frontend && npx playwright test`, 7 tests sur un téléphone simulé (Pixel 5), dont la largeur de 360 px.
- **Vérification sur un vrai téléphone** : la fiche ci-dessous, environ 10 minutes.

## Préparer

1. Sur le PC, double-cliquer sur `DEMARRER-DALIL.bat`. À la fin, il affiche une adresse du type `http://192.168.1.20:3000`.
2. Si Windows demande d'autoriser **Node.js** sur le réseau privé, accepter.
3. Connecter le téléphone au **même Wi-Fi** que le PC et ouvrir cette adresse dans Chrome.

**Dictée et installation de l'application.** Le navigateur ne les autorise que sur une adresse sécurisée (https) ou sur `localhost`. Pour les essayer sur le téléphone avec l'adresse du PC :
1. Dans Chrome Android, ouvrir `chrome://flags/#unsafely-treat-insecure-origin-as-secure`.
2. Y saisir l'adresse affichée, par exemple `http://192.168.1.20:3000`.
3. Choisir **Enabled**, puis redémarrer Chrome.

Une fois le site mis en ligne en https (étape 12), ce réglage ne sera plus nécessaire.

## Parcours à suivre (cocher)

**Automobiliste**
- [ ] La page d'accueil s'affiche sans défilement horizontal.
- [ ] Choisir le véhicule : marque, modèle, année, motorisation.
- [ ] Décrire la panne au clavier : « ça grince fort quand je freine ». Lancer.
- [ ] Le diagnostic arrive. La progression s'affiche pendant l'attente.
- [ ] Le message « Ne roulez pas » s'affiche en premier.
- [ ] Les causes et la pièce s'affichent, avec la mention qu'il s'agit d'une aide, pas d'un diagnostic certifié.
- [ ] « Voir les magasins » ouvre la liste des magasins, chacun avec la raison de son classement.
- [ ] La carte s'affiche, et on peut la déplacer au doigt.
- [ ] Le bouton WhatsApp d'un magasin [DÉMO] indique bien « magasin fictif ».
- [ ] « Pièce trouvée ? » enregistre la réponse.
- [ ] Dictée (après le réglage Chrome) : « Dicter », parler, le texte apparaît, puis on le corrige.
- [ ] Installation (après le réglage Chrome) : menu Chrome, puis « Installer l'application ». L'icône DALIL apparaît sur l'écran d'accueil.

**Mécanicien**
- [ ] « Chercher une pièce » : taper « amortisseur », puis voir les magasins.

**Magasin**
- [ ] Connexion par numéro de téléphone : le code s'affiche dans la fenêtre « DALIL - API » du PC.

## Résultat

Noter ici la date, le modèle de téléphone, le navigateur et ce qui n'a pas marché (avec une capture d'écran). Puis mettre à jour `docs/SUIVI.md`.

| Date | Téléphone | Navigateur | Résultat | Problèmes |
| --- | --- | --- | --- | --- |
| | | | | |
