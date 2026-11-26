# Résultats 20261126-1412 exemples-reels-hybride

Modèle de langage : `none`. Jeux : audit_ecriture_oran, largus_test, largus_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 87% | 91% | 7% | 100% | 4251.2 / 3621.6 |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 35% | 59% | 5% | – | 3187.1 / 3618.8 |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 40% | 56% | 9% | – | 4359.1 / 5173.8 |
| reels / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 89% | 91% | 7% | 100% | 5.8 / 6.9 |
| reels / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 40% | 60% | 3% | – | 11.9 / 19.9 |
| reels / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 46% | 58% | 12% | – | 12.1 / 16.4 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### en-service / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### en-service / D (chaîne complète) | largus_test (43)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction', 'demarreur', 'ampoules']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu ['kit-embrayage', 'boite-vitesses', 'filtre-air']
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'courroie-accessoires', 'alternateur']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'pompe-carburant']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['pompe-eau', 'thermostat', 'ventilateur-radiateur']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu ['bougies-prechauffage', 'pompe-carburant', 'turbocompresseur']
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['vanne-egr', 'filtre-huile']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['turbocompresseur', 'boite-vitesses', 'silencieux']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['turbocompresseur', 'boite-vitesses', 'debitmetre']
- `lar026` (texte privé) : attendu ['pompe-carburant'], obtenu ['kit-embrayage', 'boite-vitesses', 'filtre-air']
- `lar030` (texte privé) : attendu ['injecteurs'], obtenu ['batterie', 'demarreur', 'kit-embrayage']
- `lar033` (texte privé) : attendu ['injecteurs'], obtenu ['sonde-lambda', 'pompe-carburant', 'bougies-allumage']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'plaquettes-avant', 'demarreur']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'etrier-frein']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['demarreur', 'batterie', 'bougies-prechauffage']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['bougies-allumage', 'boite-vitesses', 'pompe-carburant']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['demarreur', 'bobine-allumage', 'batterie']
- `lar051` (texte privé) : attendu ['bougies-allumage'], obtenu ['filtre-air', 'filtre-huile', 'pompe-carburant']
- `lar052` (texte privé) : attendu ['ampoules'], obtenu ['demarreur', 'ventilateur-radiateur', 'batterie']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['ventilateur-radiateur', 'thermostat', 'compresseur-clim']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'pompe-carburant', 'vanne-egr']
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['amortisseurs', 'rotules-direction', 'etrier-frein']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu ['kit-embrayage', 'pompe-carburant', 'capteur-vilebrequin']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['demarreur', 'batterie', 'alternateur']
- `lar068` (texte privé) : attendu ['batterie'], obtenu unknown
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['demarreur', 'batterie', 'pompe-carburant']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'batterie']
- `lar075` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'bougies-allumage', 'demarreur']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['pompe-carburant', 'demarreur', 'bougies-allumage']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['demarreur', 'plaquettes-avant', 'batterie']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction', 'rotules-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'disques-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu unknown
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu ['amortisseurs', 'biellette-stabilisatrice', 'ampoules']
- `lar097` (texte privé) : attendu ['bougies-allumage'], obtenu unknown
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'thermostat', 'demarreur']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'pompe-carburant']

### en-service / D (chaîne complète) | largus_controle (19)
- `ctl001` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'bougies-prechauffage']
- `ctl003` (texte privé) : attendu ['batterie'], obtenu ['alternateur', 'demarreur', 'boite-vitesses']
- `ctl008` (texte privé) : attendu ['triangles'], obtenu ['rotules-direction', 'etrier-frein', 'plaquettes-avant']
- `ctl009` (texte privé) : attendu ['debitmetre'], obtenu ['batterie', 'demarreur', 'bougies-allumage']
- `ctl012` (texte privé) : attendu ['alternateur'], obtenu unknown
- `ctl013` (texte privé) : attendu ['thermostat'], obtenu ['ventilateur-radiateur', 'radiateur', 'compresseur-clim']
- `ctl015` (texte privé) : attendu ['pompe-carburant'], obtenu ['bougies-prechauffage', 'batterie', 'alternateur']
- `ctl018` (texte privé) : attendu ['injecteurs'], obtenu ['cable-embrayage', 'kit-embrayage']
- `ctl019` (texte privé) : attendu ['pompe-carburant'], obtenu ['sonde-lambda', 'capteur-vilebrequin']
- `ctl020` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'pompe-carburant', 'batterie']
- `ctl021` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'alternateur', 'demarreur']
- `ctl022` (texte privé) : attendu ['papillon-motorise'], obtenu ['alternateur', 'batterie']
- `ctl025` (texte privé) : attendu ['filtre-carburant'], obtenu ['bougies-prechauffage', 'bougies-allumage', 'filtre-huile']
- `ctl031` (texte privé) : attendu ['turbocompresseur'], obtenu ['boite-vitesses', 'kit-embrayage', 'filtre-air']
- `ctl035` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `ctl036` (texte privé) : attendu ['bobine-allumage'], obtenu unknown
- `ctl038` (texte privé) : attendu ['cardans'], obtenu ['boite-vitesses', 'disques-frein', 'roulements-roue']
- `ctl039` (texte privé) : attendu ['debitmetre'], obtenu unknown
- `ctl042` (texte privé) : attendu ['roulements-roue'], obtenu ['kit-distribution', 'boite-vitesses', 'courroie-accessoires']

### reels / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### reels / D (chaîne complète) | largus_test (42)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['batterie', 'pompe-direction', 'alternateur']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu unknown
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'alternateur', 'courroie-accessoires']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'injecteurs', 'pompe-carburant']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['thermostat', 'pompe-eau', 'ventilateur-radiateur']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu ['bougies-prechauffage', 'pompe-carburant', 'turbocompresseur']
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['vanne-egr', 'injecteurs', 'pompe-carburant']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['turbocompresseur', 'boite-vitesses', 'pompe-direction']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['turbocompresseur', 'boite-vitesses', 'vanne-egr']
- `lar025` (texte privé) : attendu ['roulements-roue'], obtenu unknown
- `lar030` (texte privé) : attendu ['injecteurs'], obtenu ['batterie', 'kit-embrayage', 'alternateur']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur', 'batterie']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'batterie', 'pompe-carburant']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'batterie', 'etrier-frein']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage', 'batterie']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['boite-vitesses', 'bougies-allumage', 'pompe-carburant']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['batterie', 'demarreur', 'bobine-allumage']
- `lar051` (texte privé) : attendu ['bougies-allumage'], obtenu ['filtre-air', 'pompe-carburant', 'injecteurs']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'joint-culasse']
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['ventilateur-radiateur', 'thermostat', 'injecteurs']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'vanne-egr', 'pompe-carburant']
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['batterie', 'alternateur', 'amortisseurs']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu ['injecteurs', 'pompe-carburant', 'kit-embrayage']
- `lar065` (texte privé) : attendu ['turbocompresseur'], obtenu ['vanne-egr', 'pompe-carburant', 'injecteurs']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'pompe-carburant', 'demarreur']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'injecteurs']
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'batterie']
- `lar075` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'batterie', 'alternateur']
- `lar077` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'injecteurs', 'pompe-carburant']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['demarreur', 'pompe-carburant', 'batterie']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['batterie', 'alternateur', 'plaquettes-avant']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'bougies-prechauffage']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'etrier-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu ['batterie', 'alternateur', 'support-moteur']
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu unknown
- `lar097` (texte privé) : attendu ['bougies-allumage'], obtenu ['pompe-carburant', 'injecteurs', 'batterie']
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'thermostat', 'batterie']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'pompe-carburant', 'bobine-allumage']

### reels / D (chaîne complète) | largus_controle (18)
- `ctl001` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'injecteurs']
- `ctl008` (texte privé) : attendu ['triangles'], obtenu ['rotules-direction', 'batterie', 'alternateur']
- `ctl009` (texte privé) : attendu ['debitmetre'], obtenu ['batterie', 'alternateur', 'injecteurs']
- `ctl011` (texte privé) : attendu ['bougies-allumage'], obtenu unknown
- `ctl015` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'bougies-prechauffage', 'alternateur']
- `ctl018` (texte privé) : attendu ['injecteurs'], obtenu ['cable-embrayage', 'kit-embrayage']
- `ctl019` (texte privé) : attendu ['pompe-carburant'], obtenu ['sonde-lambda', 'capteur-vilebrequin', 'batterie']
- `ctl020` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'bougies-prechauffage', 'pompe-carburant']
- `ctl021` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'alternateur', 'demarreur']
- `ctl022` (texte privé) : attendu ['papillon-motorise'], obtenu ['alternateur', 'batterie']
- `ctl025` (texte privé) : attendu ['filtre-carburant'], obtenu ['bougies-prechauffage', 'bougies-allumage', 'filtre-huile']
- `ctl030` (texte privé) : attendu ['turbocompresseur'], obtenu ['injecteurs', 'pompe-carburant', 'batterie']
- `ctl031` (texte privé) : attendu ['turbocompresseur'], obtenu ['boite-vitesses', 'batterie', 'filtre-air']
- `ctl035` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `ctl036` (texte privé) : attendu ['bobine-allumage'], obtenu unknown
- `ctl038` (texte privé) : attendu ['cardans'], obtenu unknown
- `ctl039` (texte privé) : attendu ['debitmetre'], obtenu unknown
- `ctl042` (texte privé) : attendu ['roulements-roue'], obtenu ['kit-distribution', 'boite-vitesses', 'courroie-accessoires']
