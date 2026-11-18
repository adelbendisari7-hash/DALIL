# Résultats 20261118-2122 point-zero-avant-largus

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-actuel / classifieur seul | tfidf-lr-fault-20261118 | dev_fr_synthetique | 50 | 90% | 96% | 4% | 100% | 597.3 / 135.9 |
| A-actuel / classifieur seul | tfidf-lr-fault-20261118 | demo_cases | 17 | 94% | 100% | 0% | 100% | 83.3 / 106.4 |
| A-actuel / classifieur seul | tfidf-lr-fault-20261118 | audit_ecriture_oran | 45 | 78% | 82% | 13% | 100% | 82.1 / 90.4 |
| A-actuel / classifieur seul | tfidf-lr-fault-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 83.1 / 95.1 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 96.7 / 116.9 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | demo_cases | 17 | 94% | 100% | 0% | 100% | 101.7 / 133.7 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran | 45 | 82% | 87% | 9% | 100% | 107.3 / 148.8 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 93.1 / 111.5 |
| A-jeu-commun / classifieur seul | tfidf-lr-set-moyen-20261118 | dev_fr_synthetique | 50 | 86% | 92% | 4% | 100% | 109.9 / 134.4 |
| A-jeu-commun / classifieur seul | tfidf-lr-set-moyen-20261118 | demo_cases | 17 | 76% | 88% | 12% | 100% | 111.0 / 131.5 |
| A-jeu-commun / classifieur seul | tfidf-lr-set-moyen-20261118 | audit_ecriture_oran | 45 | 71% | 80% | 16% | 100% | 99.3 / 119.2 |
| A-jeu-commun / classifieur seul | tfidf-lr-set-moyen-20261118 | audit_ecriture_oran_controle | 16 | 81% | 94% | 0% | 100% | 109.1 / 139.1 |
| A-jeu-commun / D (chaîne complète) | tfidf-lr-set-moyen-20261118 | dev_fr_synthetique | 50 | 86% | 96% | 2% | 100% | 109.9 / 133.0 |
| A-jeu-commun / D (chaîne complète) | tfidf-lr-set-moyen-20261118 | demo_cases | 17 | 76% | 88% | 12% | 100% | 108.4 / 129.4 |
| A-jeu-commun / D (chaîne complète) | tfidf-lr-set-moyen-20261118 | audit_ecriture_oran | 45 | 76% | 84% | 11% | 100% | 104.6 / 124.2 |
| A-jeu-commun / D (chaîne complète) | tfidf-lr-set-moyen-20261118 | audit_ecriture_oran_controle | 16 | 81% | 94% | 0% | 100% | 115.5 / 154.2 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A-actuel / classifieur seul | dev_fr_synthetique (2)
- `dev021` 'quand je braque complètement en accélérant ça claque côté roue avant gauche' : attendu ['cardans'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A-actuel / classifieur seul | demo_cases (0)
- aucune

### A-actuel / classifieur seul | audit_ecriture_oran (8)
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud21` 'el frein ysoni' : attendu ['plaquettes-avant', 'plaquettes-arriere', 'disques-frein'], obtenu unknown
- `aud24` 'kayen bruit f la roue avant' : attendu ['roulements-roue', 'cardans', 'triangles'], obtenu unknown
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu ['amortisseurs', 'papillon-motorise', 'rotules-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud45` 'كاين صوت في الروضة القدامية' : attendu ['roulements-roue', 'cardans', 'triangles'], obtenu unknown

### A-actuel / classifieur seul | audit_ecriture_oran_controle (0)
- aucune

### A-actuel / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A-actuel / D (chaîne complète) | demo_cases (0)
- aucune

### A-actuel / D (chaîne complète) | audit_ecriture_oran (6)
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud21` 'el frein ysoni' : attendu ['plaquettes-avant', 'plaquettes-arriere', 'disques-frein'], obtenu unknown
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu ['amortisseurs', 'papillon-motorise', 'rotules-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-actuel / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### A-jeu-commun / classifieur seul | dev_fr_synthetique (4)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']
- `dev030` 'le démarreur tourne mais le moteur ne prend pas, la jauge indique un demi-réservoir' : attendu ['pompe-carburant', 'filtre-carburant', 'capteur-vilebrequin'], obtenu ['demarreur']
- `dev043` 'ça patine et ça sent le brûlé quand je démarre en côte' : attendu ['kit-embrayage'], obtenu unknown

### A-jeu-commun / classifieur seul | demo_cases (2)
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu unknown
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-jeu-commun / classifieur seul | audit_ecriture_oran (9)
- `aud02` 'ma voitur demare pa le matin ca fait tac tac' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud03` 'le moteur chaufe bcp leguille monte au rouge' : attendu ['thermostat', 'radiateur', 'pompe-eau', 'ventilateur-radiateur', 'durite-refroidissement', 'vase-expansion'], obtenu unknown
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud09` 'les vitesse rentre mal surtout la 2' : attendu ['kit-embrayage', 'boite-vitesses', 'cable-embrayage'], obtenu unknown
- `aud29` "kayen dkhan k7al men l'echappement" : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-jeu-commun / classifieur seul | audit_ecriture_oran_controle (1)
- `ctl14` 'دخان كحل من الشكمان' : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux']

### A-jeu-commun / D (chaîne complète) | dev_fr_synthetique (2)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']

### A-jeu-commun / D (chaîne complète) | demo_cases (2)
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu unknown
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-jeu-commun / D (chaîne complète) | audit_ecriture_oran (7)
- `aud02` 'ma voitur demare pa le matin ca fait tac tac' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud29` "kayen dkhan k7al men l'echappement" : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'joint-culasse', 'joint-cache-culbuteurs']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-jeu-commun / D (chaîne complète) | audit_ecriture_oran_controle (1)
- `ctl14` 'دخان كحل من الشكمان' : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'joint-culasse', 'joint-cache-culbuteurs']
