# Résultats 20261124-0823 largus-famille

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-actuel / classifieur seul | tfidf-lr-fault-20261118 | dev_fr_synthetique | 50 | 90% | 96% | 4% | 100% | 435.0 / 99.5 |
| A-actuel / classifieur seul | tfidf-lr-fault-20261118 | demo_cases | 17 | 94% | 100% | 0% | 100% | 72.6 / 92.3 |
| A-actuel / classifieur seul | tfidf-lr-fault-20261118 | audit_ecriture_oran | 45 | 78% | 82% | 13% | 100% | 65.5 / 80.5 |
| A-actuel / classifieur seul | tfidf-lr-fault-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 64.9 / 84.1 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 72.0 / 96.9 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | demo_cases | 17 | 94% | 100% | 0% | 100% | 67.8 / 86.0 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran | 45 | 82% | 87% | 9% | 100% | 65.6 / 82.0 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 64.9 / 84.8 |
| A-sans-largus / classifieur seul | tfidf-lr-set-fort-20261124 | dev_fr_synthetique | 50 | 88% | 98% | 2% | 100% | 77.9 / 102.9 |
| A-sans-largus / classifieur seul | tfidf-lr-set-fort-20261124 | demo_cases | 17 | 88% | 94% | 6% | 100% | 77.2 / 99.8 |
| A-sans-largus / classifieur seul | tfidf-lr-set-fort-20261124 | audit_ecriture_oran | 45 | 89% | 89% | 7% | 100% | 80.1 / 98.3 |
| A-sans-largus / classifieur seul | tfidf-lr-set-fort-20261124 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 76.9 / 94.7 |
| A-sans-largus / D (chaîne complète) | tfidf-lr-set-fort-20261124 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 81.9 / 103.8 |
| A-sans-largus / D (chaîne complète) | tfidf-lr-set-fort-20261124 | demo_cases | 17 | 88% | 94% | 6% | 100% | 74.8 / 89.2 |
| A-sans-largus / D (chaîne complète) | tfidf-lr-set-fort-20261124 | audit_ecriture_oran | 45 | 84% | 87% | 9% | 100% | 78.4 / 97.5 |
| A-sans-largus / D (chaîne complète) | tfidf-lr-set-fort-20261124 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 86.0 / 102.1 |
| A-avec-largus / classifieur seul | tfidf-lr-set-fort-20261124 | dev_fr_synthetique | 50 | 92% | 98% | 2% | 100% | 84.0 / 107.2 |
| A-avec-largus / classifieur seul | tfidf-lr-set-fort-20261124 | demo_cases | 17 | 76% | 82% | 18% | 100% | 82.1 / 100.5 |
| A-avec-largus / classifieur seul | tfidf-lr-set-fort-20261124 | audit_ecriture_oran | 45 | 82% | 84% | 9% | 100% | 77.6 / 99.2 |
| A-avec-largus / classifieur seul | tfidf-lr-set-fort-20261124 | audit_ecriture_oran_controle | 16 | 88% | 94% | 0% | 100% | 75.9 / 96.5 |
| A-avec-largus / D (chaîne complète) | tfidf-lr-set-fort-20261124 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 80% | 80.7 / 107.5 |
| A-avec-largus / D (chaîne complète) | tfidf-lr-set-fort-20261124 | demo_cases | 17 | 76% | 82% | 18% | 100% | 80.8 / 106.8 |
| A-avec-largus / D (chaîne complète) | tfidf-lr-set-fort-20261124 | audit_ecriture_oran | 45 | 82% | 84% | 9% | 100% | 78.3 / 99.8 |
| A-avec-largus / D (chaîne complète) | tfidf-lr-set-fort-20261124 | audit_ecriture_oran_controle | 16 | 88% | 88% | 0% | 100% | 77.8 / 100.2 |
| A-largus-moyen / classifieur seul | tfidf-lr-set-moyen-20261124 | dev_fr_synthetique | 50 | 86% | 94% | 4% | 100% | 82.8 / 108.1 |
| A-largus-moyen / classifieur seul | tfidf-lr-set-moyen-20261124 | demo_cases | 17 | 82% | 88% | 12% | 100% | 81.5 / 106.8 |
| A-largus-moyen / classifieur seul | tfidf-lr-set-moyen-20261124 | audit_ecriture_oran | 45 | 78% | 84% | 9% | 100% | 81.9 / 103.1 |
| A-largus-moyen / classifieur seul | tfidf-lr-set-moyen-20261124 | audit_ecriture_oran_controle | 16 | 88% | 88% | 0% | 100% | 79.2 / 98.6 |
| A-largus-moyen / D (chaîne complète) | tfidf-lr-set-moyen-20261124 | dev_fr_synthetique | 50 | 88% | 98% | 2% | 80% | 84.7 / 110.5 |
| A-largus-moyen / D (chaîne complète) | tfidf-lr-set-moyen-20261124 | demo_cases | 17 | 82% | 88% | 12% | 100% | 85.0 / 106.0 |
| A-largus-moyen / D (chaîne complète) | tfidf-lr-set-moyen-20261124 | audit_ecriture_oran | 45 | 76% | 84% | 9% | 100% | 75.7 / 103.7 |
| A-largus-moyen / D (chaîne complète) | tfidf-lr-set-moyen-20261124 | audit_ecriture_oran_controle | 16 | 88% | 88% | 0% | 100% | 72.2 / 92.3 |

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

### A-sans-largus / classifieur seul | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A-sans-largus / classifieur seul | demo_cases (1)
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-sans-largus / classifieur seul | audit_ecriture_oran (5)
- `aud04` 'la direction tir a gauche quand je roule' : attendu ['rotules-direction', 'biellettes-direction', 'triangles'], obtenu ['pompe-direction']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-sans-largus / classifieur seul | audit_ecriture_oran_controle (0)
- aucune

### A-sans-largus / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A-sans-largus / D (chaîne complète) | demo_cases (1)
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-sans-largus / D (chaîne complète) | audit_ecriture_oran (6)
- `aud04` 'la direction tir a gauche quand je roule' : attendu ['rotules-direction', 'biellettes-direction', 'triangles'], obtenu ['pompe-direction']
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-sans-largus / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### A-avec-largus / classifieur seul | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A-avec-largus / classifieur seul | demo_cases (3)
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu unknown
- `demo_cases006` 'on entend un sifflement strident au démarrage qui part après quelques minutes' : attendu ['courroie-accessoires', 'galet-tendeur'], obtenu unknown
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-avec-largus / classifieur seul | audit_ecriture_oran (7)
- `aud02` 'ma voitur demare pa le matin ca fait tac tac' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud06` 'bruit clak clak quand je tourne le volan a fond' : attendu ['cardans'], obtenu unknown
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu ['catalyseur', 'silencieux', 'sonde-lambda']
- `aud29` "kayen dkhan k7al men l'echappement" : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'catalyseur', 'sonde-lambda']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-avec-largus / classifieur seul | audit_ecriture_oran_controle (1)
- `ctl14` 'دخان كحل من الشكمان' : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'catalyseur', 'sonde-lambda']

### A-avec-largus / D (chaîne complète) | dev_fr_synthetique (2)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev055` 'comment changer le mot de passe de mon compte' : attendu je ne sais pas, obtenu ['kit-embrayage', 'cable-embrayage', 'boite-vitesses']

### A-avec-largus / D (chaîne complète) | demo_cases (3)
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu unknown
- `demo_cases006` 'on entend un sifflement strident au démarrage qui part après quelques minutes' : attendu ['courroie-accessoires', 'galet-tendeur'], obtenu unknown
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-avec-largus / D (chaîne complète) | audit_ecriture_oran (7)
- `aud02` 'ma voitur demare pa le matin ca fait tac tac' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud06` 'bruit clak clak quand je tourne le volan a fond' : attendu ['cardans'], obtenu unknown
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu ['catalyseur', 'silencieux', 'sonde-lambda']
- `aud29` "kayen dkhan k7al men l'echappement" : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'catalyseur', 'sonde-lambda']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-avec-largus / D (chaîne complète) | audit_ecriture_oran_controle (2)
- `ctl04` 'siyara t3ayi f la monté w ma tetla3ch' : attendu ['kit-embrayage', 'turbocompresseur', 'filtre-carburant', 'injecteurs', 'filtre-air'], obtenu ['vanne-egr', 'papillon-motorise', 'kit-distribution']
- `ctl14` 'دخان كحل من الشكمان' : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'catalyseur', 'sonde-lambda']

### A-largus-moyen / classifieur seul | dev_fr_synthetique (3)
- `dev010` 'mon moteur gasoil peine à démarrer quand il fait froid, ça part après plusieurs tentatives' : attendu ['bougies-prechauffage'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev033` 'je dois faire la vidange, elle a 12 000 km de retard' : attendu ['filtre-huile', 'huile-moteur'], obtenu ['support-moteur', 'joint-culasse', 'joint-cache-culbuteurs']

### A-largus-moyen / classifieur seul | demo_cases (2)
- `demo_cases006` 'on entend un sifflement strident au démarrage qui part après quelques minutes' : attendu ['courroie-accessoires', 'galet-tendeur'], obtenu unknown
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-largus-moyen / classifieur seul | audit_ecriture_oran (7)
- `aud03` 'le moteur chaufe bcp leguille monte au rouge' : attendu ['thermostat', 'radiateur', 'pompe-eau', 'ventilateur-radiateur', 'durite-refroidissement', 'vase-expansion'], obtenu unknown
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu ['catalyseur', 'silencieux', 'sonde-lambda']
- `aud29` "kayen dkhan k7al men l'echappement" : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'catalyseur', 'sonde-lambda']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-largus-moyen / classifieur seul | audit_ecriture_oran_controle (2)
- `ctl04` 'siyara t3ayi f la monté w ma tetla3ch' : attendu ['kit-embrayage', 'turbocompresseur', 'filtre-carburant', 'injecteurs', 'filtre-air'], obtenu ['vanne-egr', 'papillon-motorise']
- `ctl14` 'دخان كحل من الشكمان' : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'catalyseur', 'sonde-lambda']

### A-largus-moyen / D (chaîne complète) | dev_fr_synthetique (2)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev055` 'comment changer le mot de passe de mon compte' : attendu je ne sais pas, obtenu ['kit-embrayage', 'boite-vitesses', 'cable-embrayage']

### A-largus-moyen / D (chaîne complète) | demo_cases (2)
- `demo_cases006` 'on entend un sifflement strident au démarrage qui part après quelques minutes' : attendu ['courroie-accessoires', 'galet-tendeur'], obtenu unknown
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-largus-moyen / D (chaîne complète) | audit_ecriture_oran (7)
- `aud02` 'ma voitur demare pa le matin ca fait tac tac' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu ['catalyseur', 'silencieux', 'sonde-lambda']
- `aud29` "kayen dkhan k7al men l'echappement" : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'catalyseur', 'sonde-lambda']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-largus-moyen / D (chaîne complète) | audit_ecriture_oran_controle (2)
- `ctl04` 'siyara t3ayi f la monté w ma tetla3ch' : attendu ['kit-embrayage', 'turbocompresseur', 'filtre-carburant', 'injecteurs', 'filtre-air'], obtenu ['vanne-egr', 'papillon-motorise', 'kit-distribution']
- `ctl14` 'دخان كحل من الشكمان' : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'catalyseur', 'sonde-lambda']
