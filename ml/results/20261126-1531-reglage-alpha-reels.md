# Résultats 20261126-1531 reglage-alpha-reels

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, largus_test.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| a0.15 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.15-20261126 | dev_fr_synthetique | 50 | 92% | 98% | 2% | 100% | 414.9 / 81.0 |
| a0.15 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.15-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 67.5 / 75.3 |
| a0.15 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.15-20261126 | audit_ecriture_oran | 45 | 89% | 91% | 7% | 100% | 64.8 / 70.2 |
| a0.15 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.15-20261126 | largus_test | 104 | 40% | 59% | 5% | – | 107.8 / 126.4 |
| a0.25 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | dev_fr_synthetique | 50 | 94% | 98% | 2% | 100% | 70.1 / 78.5 |
| a0.25 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 69.2 / 78.0 |
| a0.25 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 89% | 91% | 7% | 100% | 63.9 / 69.0 |
| a0.25 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 40% | 61% | 1% | – | 106.3 / 127.0 |
| a0.5 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.5-20261126 | dev_fr_synthetique | 50 | 94% | 98% | 2% | 100% | 69.0 / 77.6 |
| a0.5 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.5-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 68.8 / 78.3 |
| a0.5 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.5-20261126 | audit_ecriture_oran | 45 | 87% | 91% | 7% | 100% | 67.2 / 75.0 |
| a0.5 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.5-20261126 | largus_test | 104 | 38% | 60% | 0% | – | 107.8 / 129.7 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### a0.15 / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### a0.15 / D (chaîne complète) | demo_cases (0)
- aucune

### a0.15 / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### a0.15 / D (chaîne complète) | largus_test (43)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['batterie', 'ampoules', 'pompe-direction']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu ['kit-embrayage', 'alternateur', 'batterie']
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'courroie-accessoires', 'alternateur']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'injecteurs', 'batterie']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['thermostat', 'pompe-eau']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu unknown
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['vanne-egr', 'batterie', 'injecteurs']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['turbocompresseur', 'boite-vitesses', 'courroie-accessoires']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['bougies-allumage', 'turbocompresseur', 'boite-vitesses']
- `lar025` (texte privé) : attendu ['roulements-roue'], obtenu unknown
- `lar026` (texte privé) : attendu ['pompe-carburant'], obtenu ['kit-embrayage', 'bougies-allumage', 'boite-vitesses']
- `lar034` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'bougies-allumage']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur', 'batterie']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'batterie']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'cable-embrayage', 'batterie']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage', 'batterie', 'bougies-allumage']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['bougies-allumage', 'filtre-air', 'pompe-carburant']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['batterie', 'demarreur', 'bobine-allumage']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'pompe-eau']
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['ventilateur-radiateur', 'thermostat', 'injecteurs']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'vanne-egr', 'pompe-carburant']
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['batterie', 'injecteurs', 'alternateur']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu ['injecteurs', 'pompe-carburant', 'filtre-air']
- `lar064` (texte privé) : attendu ['etrier-frein'], obtenu ['plaquettes-avant']
- `lar065` (texte privé) : attendu ['turbocompresseur'], obtenu ['vanne-egr', 'injecteurs', 'batterie']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'demarreur', 'pompe-carburant']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'pompe-direction', 'alternateur']
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'batterie', 'thermostat']
- `lar075` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'batterie', 'demarreur']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'bougies-prechauffage']
- `lar085` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'bobine-allumage', 'pompe-carburant']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'etrier-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu unknown
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu unknown
- `lar097` (texte privé) : attendu ['bougies-allumage'], obtenu unknown
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'batterie', 'thermostat']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'bobine-allumage', 'pompe-carburant']

### a0.25 / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### a0.25 / D (chaîne complète) | demo_cases (0)
- aucune

### a0.25 / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### a0.25 / D (chaîne complète) | largus_test (41)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['batterie', 'ampoules', 'pompe-direction']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu ['kit-embrayage', 'alternateur', 'batterie']
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'alternateur', 'courroie-accessoires']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'injecteurs', 'pompe-carburant']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['thermostat', 'pompe-eau']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu ['turbocompresseur', 'bougies-prechauffage', 'pompe-carburant']
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['vanne-egr', 'injecteurs', 'batterie']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['turbocompresseur', 'boite-vitesses', 'injecteurs']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['bougies-allumage', 'turbocompresseur', 'boite-vitesses']
- `lar025` (texte privé) : attendu ['roulements-roue'], obtenu unknown
- `lar034` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'bougies-allumage']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur', 'batterie']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'batterie']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'cable-embrayage', 'batterie']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage', 'batterie', 'bougies-allumage']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['bougies-allumage', 'pompe-carburant', 'filtre-air']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['batterie', 'demarreur', 'bobine-allumage']
- `lar051` (texte privé) : attendu ['bougies-allumage'], obtenu ['filtre-air', 'injecteurs', 'pompe-carburant']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'pompe-eau']
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['ventilateur-radiateur', 'thermostat', 'injecteurs']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'vanne-egr', 'pompe-carburant']
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['batterie', 'amortisseurs', 'injecteurs']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu ['injecteurs', 'pompe-carburant', 'kit-embrayage']
- `lar064` (texte privé) : attendu ['etrier-frein'], obtenu ['plaquettes-avant', 'disques-frein']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'demarreur', 'pompe-carburant']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'pompe-direction']
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'batterie', 'thermostat']
- `lar075` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'batterie', 'demarreur']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'bougies-prechauffage']
- `lar085` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'bobine-allumage', 'pompe-carburant']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'etrier-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu ['batterie', 'silencieux', 'alternateur']
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu ['amortisseurs', 'ampoules', 'alternateur']
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'batterie', 'thermostat']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'bobine-allumage', 'pompe-carburant']

### a0.5 / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### a0.5 / D (chaîne complète) | demo_cases (0)
- aucune

### a0.5 / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### a0.5 / D (chaîne complète) | largus_test (42)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['batterie', 'ampoules', 'alternateur']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu ['kit-embrayage', 'boite-vitesses', 'injecteurs']
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'alternateur', 'courroie-accessoires']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'injecteurs', 'pompe-carburant']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['thermostat', 'pompe-eau']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu ['bougies-prechauffage', 'turbocompresseur', 'bougies-allumage']
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['vanne-egr', 'injecteurs', 'pompe-carburant']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['turbocompresseur', 'injecteurs', 'boite-vitesses']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['turbocompresseur', 'bougies-allumage', 'boite-vitesses']
- `lar025` (texte privé) : attendu ['roulements-roue'], obtenu ['rotules-direction', 'etrier-frein', 'disques-frein']
- `lar026` (texte privé) : attendu ['pompe-carburant'], obtenu ['kit-embrayage', 'cable-embrayage', 'boite-vitesses']
- `lar034` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'bougies-allumage']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur', 'batterie']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'batterie', 'pompe-carburant']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'cable-embrayage']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage', 'bougies-allumage']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['bougies-allumage', 'pompe-carburant', 'injecteurs']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['batterie', 'demarreur', 'bobine-allumage']
- `lar051` (texte privé) : attendu ['bougies-allumage'], obtenu ['filtre-air', 'injecteurs', 'pompe-carburant']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'pompe-eau', 'radiateur']
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['ventilateur-radiateur', 'thermostat', 'radiateur']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'pompe-carburant', 'injecteurs']
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['amortisseurs', 'batterie', 'alternateur']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu ['injecteurs', 'pompe-carburant', 'kit-embrayage']
- `lar064` (texte privé) : attendu ['etrier-frein'], obtenu ['plaquettes-avant', 'disques-frein']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'demarreur', 'pompe-carburant']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'pompe-direction']
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'thermostat']
- `lar075` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'bougies-allumage', 'bobine-allumage']
- `lar077` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'injecteurs', 'pompe-carburant']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'injecteurs', 'demarreur']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction', 'rotules-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'etrier-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu ['batterie', 'alternateur', 'silencieux']
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu ['amortisseurs', 'ampoules', 'alternateur']
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'thermostat', 'bougies-allumage']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'bobine-allumage', 'pompe-carburant']
