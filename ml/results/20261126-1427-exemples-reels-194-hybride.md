# Résultats 20261126-1427 exemples-reels-194-hybride

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle, largus_test, largus_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| en-service / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | dev_fr_synthetique | 50 | 96% | 98% | 2% | 100% | 3058.3 / 2887.7 |
| en-service / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 2324.1 / 2690.4 |
| en-service / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 89% | 91% | 7% | 100% | 2350.1 / 2629.1 |
| en-service / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran_controle | 16 | 94% | 100% | 0% | 100% | 2244.1 / 2654.6 |
| en-service / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 40% | 60% | 3% | – | 3949.0 / 6378.8 |
| en-service / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 46% | 58% | 12% | – | 5031.3 / 6289.0 |
| reels194 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | dev_fr_synthetique | 50 | 96% | 98% | 2% | 100% | 2453.4 / 2819.6 |
| reels194 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | demo_cases | 17 | 94% | 100% | 0% | 100% | 2303.1 / 2681.4 |
| reels194 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran | 45 | 89% | 91% | 7% | 100% | 2369.7 / 2724.8 |
| reels194 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | audit_ecriture_oran_controle | 16 | 94% | 100% | 0% | 100% | 2233.9 / 2628.5 |
| reels194 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_test | 104 | 40% | 60% | 2% | – | 3184.2 / 3592.2 |
| reels194 / D (chaîne complète) | tfidf-lr-fault-reels-20261126+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 49% | 63% | 7% | – | 3303.9 / 3758.0 |

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

### en-service / D (chaîne complète) | largus_test (42)
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

### en-service / D (chaîne complète) | largus_controle (18)
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

### reels194 / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### reels194 / D (chaîne complète) | demo_cases (0)
- aucune

### reels194 / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### reels194 / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### reels194 / D (chaîne complète) | largus_test (42)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['batterie', 'pompe-direction', 'ampoules']
- `lar004` (texte privé) : attendu ['papillon-motorise'], obtenu ['kit-embrayage', 'boite-vitesses', 'filtre-air']
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['batterie', 'alternateur', 'courroie-accessoires']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur', 'injecteurs', 'pompe-carburant']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['thermostat', 'pompe-eau', 'ventilateur-radiateur']
- `lar010` (texte privé) : attendu ['vanne-egr'], obtenu ['bougies-prechauffage', 'pompe-carburant', 'turbocompresseur']
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['vanne-egr', 'injecteurs', 'pompe-carburant']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['turbocompresseur', 'boite-vitesses', 'injecteurs']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu unknown
- `lar025` (texte privé) : attendu ['roulements-roue'], obtenu unknown
- `lar026` (texte privé) : attendu ['pompe-carburant'], obtenu ['kit-embrayage', 'filtre-air', 'boite-vitesses']
- `lar030` (texte privé) : attendu ['injecteurs'], obtenu ['batterie', 'demarreur', 'kit-embrayage']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur', 'batterie']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'batterie']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'batterie', 'etrier-frein']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage', 'batterie', 'bougies-allumage']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar049` (texte privé) : attendu ['debitmetre'], obtenu ['bougies-allumage', 'boite-vitesses', 'pompe-carburant']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['batterie', 'demarreur', 'bobine-allumage']
- `lar051` (texte privé) : attendu ['bougies-allumage'], obtenu ['filtre-air', 'injecteurs', 'pompe-carburant']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'joint-culasse', 'alternateur']
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['thermostat', 'ventilateur-radiateur', 'injecteurs']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur', 'vanne-egr', 'pompe-carburant']
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['batterie', 'amortisseurs', 'injecteurs']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['pompe-carburant']
- `lar062` (texte privé) : attendu ['papillon-motorise'], obtenu ['injecteurs', 'pompe-carburant', 'kit-embrayage']
- `lar065` (texte privé) : attendu ['turbocompresseur'], obtenu ['vanne-egr', 'pompe-carburant', 'injecteurs']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar069` (texte privé) : attendu ['papillon-motorise'], obtenu ['batterie', 'demarreur', 'pompe-carburant']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'bougies-allumage']
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'batterie']
- `lar075` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'batterie', 'bougies-allumage']
- `lar077` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'injecteurs', 'pompe-carburant']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['demarreur', 'batterie', 'pompe-carburant']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['batterie', 'plaquettes-avant', 'alternateur']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'alternateur']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'etrier-frein']
- `lar091` (texte privé) : attendu ['cardans'], obtenu ['batterie', 'alternateur', 'support-moteur']
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu ['amortisseurs', 'ampoules', 'alternateur']
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'batterie', 'thermostat']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-allumage', 'pompe-carburant', 'bobine-allumage']

### reels194 / D (chaîne complète) | largus_controle (16)
- `ctl001` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'injecteurs']
- `ctl008` (texte privé) : attendu ['triangles'], obtenu ['batterie', 'rotules-direction', 'alternateur']
- `ctl009` (texte privé) : attendu ['debitmetre'], obtenu ['batterie', 'alternateur', 'injecteurs']
- `ctl015` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'bougies-prechauffage', 'alternateur']
- `ctl018` (texte privé) : attendu ['injecteurs'], obtenu ['cable-embrayage', 'kit-embrayage']
- `ctl019` (texte privé) : attendu ['pompe-carburant'], obtenu ['sonde-lambda', 'batterie', 'capteur-vilebrequin']
- `ctl020` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bougies-prechauffage', 'injecteurs', 'pompe-carburant']
- `ctl021` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'alternateur', 'demarreur']
- `ctl022` (texte privé) : attendu ['papillon-motorise'], obtenu ['alternateur', 'batterie']
- `ctl025` (texte privé) : attendu ['filtre-carburant'], obtenu ['bougies-prechauffage', 'bougies-allumage', 'filtre-huile']
- `ctl030` (texte privé) : attendu ['turbocompresseur'], obtenu ['injecteurs', 'batterie', 'pompe-carburant']
- `ctl031` (texte privé) : attendu ['turbocompresseur'], obtenu ['boite-vitesses', 'batterie', 'injecteurs']
- `ctl036` (texte privé) : attendu ['bobine-allumage'], obtenu unknown
- `ctl038` (texte privé) : attendu ['cardans'], obtenu unknown
- `ctl039` (texte privé) : attendu ['debitmetre'], obtenu unknown
- `ctl042` (texte privé) : attendu ['roulements-roue'], obtenu ['kit-distribution', 'boite-vitesses', 'courroie-accessoires']
