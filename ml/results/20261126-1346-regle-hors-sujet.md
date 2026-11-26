# Résultats 20261126-1346 regle-hors-sujet

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle, largus_test.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2niv-regle / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 1642.5 / 329.4 |
| 2niv-regle / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 273.5 / 313.1 |
| 2niv-regle / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 87% | 91% | 7% | 100% | 273.8 / 297.2 |
| 2niv-regle / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran_controle | 16 | 94% | 100% | 0% | 100% | 272.8 / 306.8 |
| 2niv-regle / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 36% | 57% | 5% | – | 402.5 / 471.7 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### 2niv-regle / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### 2niv-regle / D (chaîne complète) | demo_cases (0)
- aucune

### 2niv-regle / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### 2niv-regle / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### 2niv-regle / D (chaîne complète) | largus_test (45)
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
