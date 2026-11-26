# Résultats 20261126-1410 exemples-reels

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle, largus_test, largus_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 411.7 / 79.1 |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 65.9 / 74.1 |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 87% | 91% | 7% | 100% | 67.0 / 90.4 |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran_controle | 16 | 94% | 100% | 0% | 100% | 75.1 / 100.0 |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 36% | 57% | 5% | – | 113.9 / 141.6 |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 37% | 58% | 14% | – | 115.2 / 146.1 |
| reels / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | dev_fr_synthetique | 50 | 94% | 98% | 2% | 100% | 66.9 / 76.0 |
| reels / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 66.5 / 75.3 |
| reels / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 89% | 91% | 7% | 100% | 63.2 / 69.6 |
| reels / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran_controle | 16 | 94% | 100% | 0% | 100% | 63.8 / 77.9 |
| reels / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 40% | 59% | 3% | – | 114.1 / 140.4 |
| reels / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 42% | 58% | 16% | – | 117.4 / 134.8 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### en-service / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### en-service / D (chaîne complète) | demo_cases (0)
- aucune

### en-service / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### en-service / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### en-service / D (chaîne complète) | largus_test (45)
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
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['pompe-carburant', 'demarreur', 'alternateur']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['demarreur', 'batterie', 'silencieux']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'bougies-prechauffage']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction', 'rotules-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'disques-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu unknown
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu ['amortisseurs', 'biellette-stabilisatrice', 'ampoules']
- `lar097` (texte privé) : attendu ['bougies-allumage'], obtenu unknown
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'thermostat']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'bobine-allumage']

### en-service / D (chaîne complète) | largus_controle (18)
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

### reels / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### reels / D (chaîne complète) | demo_cases (0)
- aucune

### reels / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### reels / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### reels / D (chaîne complète) | largus_test (43)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['batterie', 'alternateur', 'pompe-direction']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu unknown
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'alternateur', 'courroie-accessoires']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'injecteurs', 'pompe-carburant']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['thermostat', 'pompe-eau']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu ['turbocompresseur', 'bougies-prechauffage', 'pompe-carburant']
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['vanne-egr', 'injecteurs', 'pompe-carburant']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['turbocompresseur', 'boite-vitesses', 'injecteurs']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['turbocompresseur', 'vanne-egr', 'boite-vitesses']
- `lar025` (texte privé) : attendu ['roulements-roue'], obtenu unknown
- `lar034` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'bougies-allumage']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur', 'batterie']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'batterie', 'pompe-carburant']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'cable-embrayage', 'batterie']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage', 'batterie']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['bougies-allumage', 'pompe-carburant', 'filtre-air']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['batterie', 'bobine-allumage', 'demarreur']
- `lar051` (texte privé) : attendu ['bougies-allumage'], obtenu ['filtre-air', 'injecteurs', 'pompe-carburant']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'pompe-eau']
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['ventilateur-radiateur', 'thermostat', 'injecteurs']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'vanne-egr', 'pompe-carburant']
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['batterie', 'alternateur', 'amortisseurs']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu ['injecteurs', 'pompe-carburant', 'filtre-air']
- `lar064` (texte privé) : attendu ['etrier-frein'], obtenu ['plaquettes-avant', 'disques-frein']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'pompe-carburant', 'demarreur']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'pompe-direction']
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'thermostat', 'batterie']
- `lar075` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'batterie', 'demarreur']
- `lar077` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'injecteurs', 'pompe-carburant']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['pompe-carburant', 'batterie', 'demarreur']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'injecteurs']
- `lar085` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'pompe-carburant', 'bobine-allumage']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'etrier-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu ['batterie', 'alternateur', 'silencieux']
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu unknown
- `lar097` (texte privé) : attendu ['bougies-allumage'], obtenu ['pompe-carburant', 'injecteurs', 'batterie']
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'batterie', 'thermostat']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'bobine-allumage', 'pompe-carburant']

### reels / D (chaîne complète) | largus_controle (18)
- `ctl001` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'injecteurs']
- `ctl008` (texte privé) : attendu ['triangles'], obtenu ['rotules-direction', 'batterie', 'amortisseurs']
- `ctl009` (texte privé) : attendu ['debitmetre'], obtenu ['batterie', 'alternateur', 'injecteurs']
- `ctl011` (texte privé) : attendu ['bougies-allumage'], obtenu unknown
- `ctl012` (texte privé) : attendu ['alternateur'], obtenu unknown
- `ctl015` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'bougies-prechauffage', 'bobine-allumage']
- `ctl018` (texte privé) : attendu ['injecteurs'], obtenu ['cable-embrayage', 'kit-embrayage']
- `ctl019` (texte privé) : attendu ['pompe-carburant'], obtenu ['sonde-lambda', 'capteur-vilebrequin', 'batterie']
- `ctl020` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'bougies-prechauffage', 'pompe-carburant']
- `ctl021` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'alternateur', 'demarreur']
- `ctl022` (texte privé) : attendu ['papillon-motorise'], obtenu ['alternateur', 'batterie']
- `ctl025` (texte privé) : attendu ['filtre-carburant'], obtenu ['bougies-prechauffage', 'bougies-allumage', 'filtre-huile']
- `ctl026` (texte privé) : attendu ['injecteurs', 'pompe-carburant'], obtenu unknown
- `ctl031` (texte privé) : attendu ['turbocompresseur'], obtenu unknown
- `ctl036` (texte privé) : attendu ['bobine-allumage'], obtenu unknown
- `ctl038` (texte privé) : attendu ['cardans'], obtenu unknown
- `ctl039` (texte privé) : attendu ['debitmetre'], obtenu unknown
- `ctl042` (texte privé) : attendu ['roulements-roue'], obtenu ['kit-distribution', 'pompe-carburant', 'courroie-accessoires']
