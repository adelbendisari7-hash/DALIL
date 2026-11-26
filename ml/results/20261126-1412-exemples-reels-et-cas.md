# Résultats 20261126-1412 exemples-reels-et-cas

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle, largus_test, largus_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| reels+cas / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | dev_fr_synthetique | 50 | 94% | 98% | 2% | 100% | 518.4 / 91.9 |
| reels+cas / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 71.6 / 80.7 |
| reels+cas / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 89% | 91% | 7% | 100% | 68.8 / 74.8 |
| reels+cas / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran_controle | 16 | 94% | 100% | 0% | 100% | 67.7 / 76.4 |
| reels+cas / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 40% | 59% | 5% | – | 143.4 / 251.5 |
| reels+cas / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 40% | 58% | 9% | – | 250.6 / 299.2 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### reels+cas / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### reels+cas / D (chaîne complète) | demo_cases (0)
- aucune

### reels+cas / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### reels+cas / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### reels+cas / D (chaîne complète) | largus_test (43)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['batterie', 'alternateur', 'ampoules']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu unknown
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'courroie-accessoires', 'alternateur']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'injecteurs', 'pompe-carburant']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['thermostat', 'pompe-eau']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu unknown
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['vanne-egr', 'injecteurs', 'pompe-carburant']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['turbocompresseur', 'pompe-carburant', 'boite-vitesses']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['turbocompresseur', 'vanne-egr', 'debitmetre']
- `lar025` (texte privé) : attendu ['roulements-roue'], obtenu unknown
- `lar034` (texte privé) : attendu ['demarreur'], obtenu ['batterie']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur', 'batterie']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'batterie']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'batterie', 'cable-embrayage']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage', 'batterie', 'demarreur']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['pompe-carburant', 'bougies-allumage', 'filtre-air']
- `lar051` (texte privé) : attendu ['bougies-allumage'], obtenu ['filtre-air', 'injecteurs', 'pompe-carburant']
- `lar052` (texte privé) : attendu ['ampoules'], obtenu ['batterie', 'thermostat', 'pompe-carburant']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu ['alternateur', 'batterie', 'pompe-eau']
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['ventilateur-radiateur', 'thermostat', 'injecteurs']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'vanne-egr', 'pompe-carburant']
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['batterie', 'alternateur', 'amortisseurs']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu ['injecteurs', 'pompe-carburant', 'batterie']
- `lar064` (texte privé) : attendu ['etrier-frein'], obtenu ['plaquettes-avant', 'capteur-vilebrequin', 'alternateur']
- `lar065` (texte privé) : attendu ['turbocompresseur'], obtenu ['vanne-egr', 'injecteurs', 'pompe-carburant']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'pompe-carburant', 'demarreur']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'bobine-allumage']
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'batterie', 'ampoules']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'pompe-carburant', 'demarreur']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'bougies-prechauffage', 'injecteurs']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction', 'batterie']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'etrier-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu unknown
- `lar093` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'alternateur']
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu unknown
- `lar097` (texte privé) : attendu ['bougies-allumage'], obtenu ['pompe-carburant', 'injecteurs', 'filtre-air']
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'demarreur', 'batterie']
- `lar102` (texte privé) : attendu ['flexible-frein'], obtenu ['plaquettes-avant', 'disques-frein', 'etrier-frein']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['pompe-carburant', 'bougies-allumage', 'bobine-allumage']

### reels+cas / D (chaîne complète) | largus_controle (18)
- `ctl001` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'injecteurs']
- `ctl008` (texte privé) : attendu ['triangles'], obtenu ['batterie', 'rotules-direction', 'turbocompresseur']
- `ctl009` (texte privé) : attendu ['debitmetre'], obtenu ['batterie', 'alternateur', 'pompe-carburant']
- `ctl012` (texte privé) : attendu ['alternateur'], obtenu unknown
- `ctl015` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'bougies-prechauffage', 'bobine-allumage']
- `ctl018` (texte privé) : attendu ['injecteurs'], obtenu ['cable-embrayage', 'kit-embrayage']
- `ctl019` (texte privé) : attendu ['pompe-carburant'], obtenu ['sonde-lambda', 'batterie', 'capteur-vilebrequin']
- `ctl020` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'pompe-carburant', 'bougies-prechauffage']
- `ctl021` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'alternateur', 'demarreur']
- `ctl022` (texte privé) : attendu ['papillon-motorise'], obtenu ['alternateur', 'batterie']
- `ctl025` (texte privé) : attendu ['filtre-carburant'], obtenu ['bougies-prechauffage', 'bougies-allumage', 'pompe-carburant']
- `ctl026` (texte privé) : attendu ['injecteurs', 'pompe-carburant'], obtenu unknown
- `ctl030` (texte privé) : attendu ['turbocompresseur'], obtenu ['injecteurs', 'batterie', 'vanne-egr']
- `ctl031` (texte privé) : attendu ['turbocompresseur'], obtenu unknown
- `ctl036` (texte privé) : attendu ['bobine-allumage'], obtenu ['papillon-motorise', 'batterie', 'boite-vitesses']
- `ctl038` (texte privé) : attendu ['cardans'], obtenu unknown
- `ctl039` (texte privé) : attendu ['debitmetre'], obtenu ['cable-embrayage', 'kit-embrayage', 'injecteurs']
- `ctl042` (texte privé) : attendu ['roulements-roue'], obtenu ['kit-distribution', 'pompe-carburant', 'courroie-accessoires']
