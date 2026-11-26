# Résultats 20261126-1359 nouvelles-fiches

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle, largus_test, largus_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| avant / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 1380.3 / 116.0 |
| avant / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 74.2 / 100.3 |
| avant / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 87% | 91% | 7% | 100% | 74.3 / 93.6 |
| avant / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran_controle | 16 | 94% | 100% | 0% | 100% | 73.0 / 91.3 |
| avant / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 36% | 57% | 5% | – | 115.5 / 146.4 |
| avant / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 37% | 58% | 14% | – | 118.4 / 136.8 |
| apres / D (chaîne complète) | tfidf-lr-fault-20261126+familles-largus-fort-a0.25-20261126 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 72.9 / 94.3 |
| apres / D (chaîne complète) | tfidf-lr-fault-20261126+familles-largus-fort-a0.25-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 71.9 / 91.7 |
| apres / D (chaîne complète) | tfidf-lr-fault-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 82% | 89% | 7% | 100% | 71.8 / 96.6 |
| apres / D (chaîne complète) | tfidf-lr-fault-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 66.9 / 89.9 |
| apres / D (chaîne complète) | tfidf-lr-fault-20261126+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 35% | 61% | 9% | – | 113.7 / 145.7 |
| apres / D (chaîne complète) | tfidf-lr-fault-20261126+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 37% | 54% | 16% | – | 134.1 / 166.5 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### avant / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### avant / D (chaîne complète) | demo_cases (0)
- aucune

### avant / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### avant / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### avant / D (chaîne complète) | largus_test (45)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction', 'demarreur', 'ampoules']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu ['kit-embrayage', 'boite-vitesses', 'demarreur']
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'courroie-accessoires', 'alternateur']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'pompe-carburant']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['thermostat', 'pompe-eau']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu ['bougies-prechauffage', 'turbocompresseur', 'bougies-allumage']
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['vanne-egr', 'filtre-huile', 'catalyseur']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['turbocompresseur', 'boite-vitesses', 'debitmetre']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['turbocompresseur', 'debitmetre', 'bougies-allumage']
- `lar026` (texte privé) : attendu ['pompe-carburant'], obtenu ['kit-embrayage', 'boite-vitesses', 'bougies-allumage']
- `lar030` (texte privé) : attendu ['injecteurs'], obtenu ['demarreur', 'batterie', 'kit-embrayage']
- `lar033` (texte privé) : attendu ['injecteurs'], obtenu ['sonde-lambda', 'bougies-allumage', 'alternateur']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'plaquettes-avant', 'demarreur']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'cable-embrayage']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'bougies-prechauffage']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['bougies-allumage', 'boite-vitesses', 'pompe-carburant']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['demarreur', 'batterie', 'bobine-allumage']
- `lar052` (texte privé) : attendu ['ampoules'], obtenu ['demarreur', 'ventilateur-radiateur', 'batterie']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu ['pompe-eau', 'radiateur', 'joint-culasse']
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['ventilateur-radiateur', 'thermostat', 'radiateur']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'pompe-carburant', 'vanne-egr']
- `lar058` (texte privé) : attendu ['bobine-allumage'], obtenu unknown
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['amortisseurs', 'rotules-direction', 'etrier-frein']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu ['kit-embrayage', 'pompe-carburant', 'filtre-air']
- `lar064` (texte privé) : attendu ['etrier-frein'], obtenu ['plaquettes-avant']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['demarreur', 'batterie', 'alternateur']
- `lar068` (texte privé) : attendu ['batterie'], obtenu unknown
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['demarreur', 'batterie', 'pompe-carburant']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'thermostat']
- `lar075` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'bougies-allumage', 'demarreur']
- `lar079` (texte privé) : attendu ['batterie'], obtenu ['alternateur', 'ampoules', 'demarreur']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['pompe-carburant', 'demarreur', 'bougies-allumage']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['demarreur', 'batterie', 'silencieux']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'bougies-prechauffage']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction', 'rotules-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'disques-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu unknown
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu ['amortisseurs', 'biellette-stabilisatrice', 'ampoules']
- `lar097` (texte privé) : attendu ['bougies-allumage'], obtenu unknown
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'thermostat']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'bobine-allumage']

### avant / D (chaîne complète) | largus_controle (18)
- `ctl001` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['demarreur', 'batterie', 'bougies-prechauffage']
- `ctl008` (texte privé) : attendu ['triangles'], obtenu ['rotules-direction', 'amortisseurs', 'etrier-frein']
- `ctl009` (texte privé) : attendu ['debitmetre'], obtenu ['batterie', 'demarreur', 'bougies-allumage']
- `ctl012` (texte privé) : attendu ['alternateur'], obtenu unknown
- `ctl013` (texte privé) : attendu ['thermostat'], obtenu ['ventilateur-radiateur', 'radiateur', 'compresseur-clim']
- `ctl015` (texte privé) : attendu ['pompe-carburant'], obtenu ['bougies-prechauffage', 'bougies-allumage']
- `ctl018` (texte privé) : attendu ['injecteurs'], obtenu ['cable-embrayage', 'kit-embrayage']
- `ctl019` (texte privé) : attendu ['pompe-carburant'], obtenu ['sonde-lambda', 'capteur-vilebrequin']
- `ctl020` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'pompe-carburant', 'kit-distribution']
- `ctl021` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'alternateur']
- `ctl022` (texte privé) : attendu ['papillon-motorise'], obtenu ['alternateur', 'batterie']
- `ctl025` (texte privé) : attendu ['filtre-carburant'], obtenu ['bougies-prechauffage', 'bougies-allumage', 'filtre-huile']
- `ctl029` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `ctl031` (texte privé) : attendu ['turbocompresseur'], obtenu ['boite-vitesses', 'kit-embrayage', 'bougies-allumage']
- `ctl035` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `ctl036` (texte privé) : attendu ['bobine-allumage'], obtenu unknown
- `ctl038` (texte privé) : attendu ['cardans'], obtenu unknown
- `ctl039` (texte privé) : attendu ['debitmetre'], obtenu unknown

### apres / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### apres / D (chaîne complète) | demo_cases (0)
- aucune

### apres / D (chaîne complète) | audit_ecriture_oran (5)
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'coupelles', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu ['amortisseurs', 'papillon-motorise', 'debitmetre']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### apres / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### apres / D (chaîne complète) | largus_test (41)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction', 'demarreur', 'ampoules']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu ['sonde-temperature', 'kit-embrayage', 'filtre-carburant']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'capteur-pression-admission', 'pompe-carburant']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu ['capteur-pression-admission', 'bougies-prechauffage', 'turbocompresseur']
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['capteur-pression-admission', 'vanne-egr']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['filtre-carburant', 'turbocompresseur', 'boite-vitesses']
- `lar026` (texte privé) : attendu ['pompe-carburant'], obtenu ['kit-embrayage', 'volant-moteur', 'boite-vitesses']
- `lar030` (texte privé) : attendu ['injecteurs'], obtenu ['demarreur', 'batterie', 'kit-embrayage']
- `lar032` (texte privé) : attendu ['bobine-allumage'], obtenu ['bougies-allumage', 'filtre-carburant', 'boite-vitesses']
- `lar033` (texte privé) : attendu ['injecteurs'], obtenu ['sonde-lambda', 'bougies-allumage', 'alternateur']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['sonde-temperature', 'injecteurs']
- `lar045` (texte privé) : attendu ['joint-culasse'], obtenu ['pompe-eau', 'radiateur', 'durite-refroidissement']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage', 'bougies-allumage']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'filtre-carburant', 'demarreur']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['bougies-allumage', 'boite-vitesses', 'filtre-air']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['demarreur', 'batterie', 'bobine-allumage']
- `lar052` (texte privé) : attendu ['ampoules'], obtenu unknown
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'pompe-carburant', 'vanne-egr']
- `lar058` (texte privé) : attendu ['bobine-allumage'], obtenu unknown
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu unknown
- `lar064` (texte privé) : attendu ['etrier-frein'], obtenu ['plaquettes-avant']
- `lar065` (texte privé) : attendu ['turbocompresseur'], obtenu ['capteur-pression-admission', 'vanne-egr', 'sonde-temperature']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['demarreur', 'batterie', 'alternateur']
- `lar068` (texte privé) : attendu ['batterie'], obtenu unknown
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['demarreur', 'batterie', 'pompe-carburant']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu ['capteur-pression-admission', 'batterie', 'pompe-direction']
- `lar075` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'sonde-temperature', 'bougies-allumage']
- `lar077` (texte privé) : attendu ['capteur-vilebrequin'], obtenu unknown
- `lar079` (texte privé) : attendu ['batterie'], obtenu ['alternateur', 'ampoules', 'demarreur']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['pompe-carburant', 'durite-refroidissement', 'demarreur']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu unknown
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'filtre-carburant', 'demarreur']
- `lar085` (texte privé) : attendu ['papillon-motorise'], obtenu unknown
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction', 'rotules-direction']
- `lar091` (texte privé) : attendu ['cardans'], obtenu unknown
- `lar097` (texte privé) : attendu ['bougies-allumage'], obtenu ['filtre-carburant', 'filtre-air', 'sonde-temperature']
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'thermostat']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'filtre-carburant', 'bobine-allumage']

### apres / D (chaîne complète) | largus_controle (20)
- `ctl001` (texte privé) : attendu ['capteur-vilebrequin'], obtenu unknown
- `ctl009` (texte privé) : attendu ['debitmetre'], obtenu ['batterie', 'sonde-temperature', 'demarreur']
- `ctl012` (texte privé) : attendu ['alternateur'], obtenu unknown
- `ctl013` (texte privé) : attendu ['thermostat'], obtenu ['sonde-temperature', 'ventilateur-radiateur', 'compresseur-clim']
- `ctl015` (texte privé) : attendu ['pompe-carburant'], obtenu ['bougies-prechauffage', 'sonde-temperature', 'bougies-allumage']
- `ctl018` (texte privé) : attendu ['injecteurs'], obtenu ['volant-moteur', 'kit-embrayage', 'cable-embrayage']
- `ctl019` (texte privé) : attendu ['pompe-carburant'], obtenu ['sonde-lambda', 'capteur-vilebrequin']
- `ctl020` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'pompe-carburant', 'kit-distribution']
- `ctl021` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'sonde-temperature']
- `ctl022` (texte privé) : attendu ['papillon-motorise'], obtenu ['alternateur', 'batterie']
- `ctl026` (texte privé) : attendu ['injecteurs', 'pompe-carburant'], obtenu ['bougies-allumage', 'turbocompresseur', 'filtre-carburant']
- `ctl028` (texte privé) : attendu ['batterie'], obtenu ['sonde-temperature', 'bougies-allumage', 'pompe-carburant']
- `ctl029` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `ctl030` (texte privé) : attendu ['turbocompresseur'], obtenu unknown
- `ctl031` (texte privé) : attendu ['turbocompresseur'], obtenu unknown
- `ctl035` (texte privé) : attendu ['pompe-carburant'], obtenu ['capteur-pression-admission', 'filtre-carburant', 'debitmetre']
- `ctl036` (texte privé) : attendu ['bobine-allumage'], obtenu unknown
- `ctl038` (texte privé) : attendu ['cardans'], obtenu unknown
- `ctl039` (texte privé) : attendu ['debitmetre'], obtenu ['volant-moteur', 'boite-vitesses']
- `ctl042` (texte privé) : attendu ['roulements-roue'], obtenu ['kit-distribution', 'galet-tendeur', 'pompe-carburant']
