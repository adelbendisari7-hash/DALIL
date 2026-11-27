# Résultats 20261127-0332 camembert-pieces

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle, largus_test, largus_controle, techniconnexion_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBP-a0.25 / D (chaîne complète) | camembert-base_set-20261127+camembert-base_set-20261127-a0.25 | dev_fr_synthetique | 50 | 84% | 94% | 2% | 100% | 9319.2 / 9832.1 |
| CBP-a0.25 / D (chaîne complète) | camembert-base_set-20261127+camembert-base_set-20261127-a0.25 | demo_cases | 17 | 82% | 100% | 0% | 100% | 9275.3 / 12800.4 |
| CBP-a0.25 / D (chaîne complète) | camembert-base_set-20261127+camembert-base_set-20261127-a0.25 | audit_ecriture_oran | 45 | 84% | 91% | 4% | 100% | 8132.0 / 12233.4 |
| CBP-a0.25 / D (chaîne complète) | camembert-base_set-20261127+camembert-base_set-20261127-a0.25 | audit_ecriture_oran_controle | 16 | 94% | 94% | 0% | 100% | 5480.0 / 6574.9 |
| CBP-a0.25 / D (chaîne complète) | camembert-base_set-20261127+camembert-base_set-20261127-a0.25 | largus_test | 104 | 38% | 64% | 1% | – | 6376.9 / 9109.5 |
| CBP-a0.25 / D (chaîne complète) | camembert-base_set-20261127+camembert-base_set-20261127-a0.25 | largus_controle | 43 | 33% | 56% | 0% | – | 3982.4 / 4425.5 |
| CBP-a0.25 / D (chaîne complète) | camembert-base_set-20261127+camembert-base_set-20261127-a0.25 | techniconnexion_controle | 39 | 46% | 67% | 0% | – | 4325.8 / 5088.7 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### CBP-a0.25 / D (chaîne complète) | dev_fr_synthetique (3)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux', 'turbocompresseur']
- `dev041` "grincement aigu à l'arrière à chaque arrêt" : attendu ['plaquettes-arriere', 'plaquettes-avant', 'machoires-frein'], obtenu ['courroie-accessoires', 'alternateur', 'disques-frein']

### CBP-a0.25 / D (chaîne complète) | demo_cases (0)
- aucune

### CBP-a0.25 / D (chaîne complète) | audit_ecriture_oran (4)
- `aud03` 'le moteur chaufe bcp leguille monte au rouge' : attendu ['thermostat', 'radiateur', 'pompe-eau', 'ventilateur-radiateur', 'durite-refroidissement', 'vase-expansion'], obtenu ['papillon-motorise', 'bougies-allumage', 'vanne-egr']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['pompe-direction', 'courroie-accessoires']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### CBP-a0.25 / D (chaîne complète) | audit_ecriture_oran_controle (1)
- `ctl04` 'siyara t3ayi f la monté w ma tetla3ch' : attendu ['kit-embrayage', 'turbocompresseur', 'filtre-carburant', 'injecteurs', 'filtre-air'], obtenu ['vanne-egr', 'papillon-motorise', 'kit-distribution']

### CBP-a0.25 / D (chaîne complète) | largus_test (38)
- `lar001` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction']
- `lar005` (texte privé) : attendu ['demarreur'], obtenu ['alternateur', 'capteur-vilebrequin']
- `lar006` (texte privé) : attendu ['catalyseur'], obtenu ['turbocompresseur']
- `lar008` (texte privé) : attendu ['durite-refroidissement'], obtenu ['pompe-eau', 'ventilateur-radiateur', 'radiateur']
- `lar012` (texte privé) : attendu ['filtre-carburant'], obtenu ['injecteurs', 'vanne-egr']
- `lar015` (texte privé) : attendu ['galet-tendeur'], obtenu ['courroie-accessoires', 'alternateur', 'silencieux']
- `lar022` (texte privé) : attendu ['filtre-air'], obtenu ['vanne-egr', 'papillon-motorise', 'boite-vitesses']
- `lar026` (texte privé) : attendu ['pompe-carburant'], obtenu ['kit-embrayage', 'bougies-allumage', 'boite-vitesses']
- `lar033` (texte privé) : attendu ['injecteurs'], obtenu ['sonde-lambda', 'bobine-allumage', 'bougies-allumage']
- `lar035` (texte privé) : attendu ['compresseur-clim'], obtenu ['thermostat']
- `lar036` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['alternateur']
- `lar037` (texte privé) : attendu ['ampoules'], obtenu ['alternateur']
- `lar038` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['pompe-carburant', 'injecteurs']
- `lar042` (texte privé) : attendu ['coupelles'], obtenu ['rotules-direction', 'cardans', 'roulements-roue']
- `lar046` (texte privé) : attendu ['huile-moteur'], obtenu ['bougies-prechauffage', 'bougies-allumage']
- `lar047` (texte privé) : attendu ['pompe-carburant'], obtenu ['demarreur', 'batterie', 'alternateur']
- `lar050` (texte privé) : attendu ['injecteurs'], obtenu ['bobine-allumage', 'bougies-allumage', 'demarreur']
- `lar052` (texte privé) : attendu ['ampoules'], obtenu ['batterie', 'alternateur', 'demarreur']
- `lar053` (texte privé) : attendu ['pompe-carburant'], obtenu unknown
- `lar055` (texte privé) : attendu ['sonde-temperature'], obtenu ['ventilateur-radiateur', 'thermostat', 'compresseur-clim']
- `lar057` (texte privé) : attendu ['capteur-pression-admission'], obtenu ['turbocompresseur']
- `lar060` (texte privé) : attendu ['silentblocs'], obtenu ['cardans', 'biellette-stabilisatrice', 'pompe-direction']
- `lar061` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-allumage', 'pompe-carburant', 'bobine-allumage']
- `lar065` (texte privé) : attendu ['turbocompresseur'], obtenu ['vanne-egr', 'papillon-motorise', 'pompe-carburant']
- `lar066` (texte privé) : attendu ['bougies-allumage'], obtenu ['batterie', 'alternateur', 'pompe-carburant']
- `lar070` (texte privé) : attendu ['pompe-carburant'], obtenu ['bobine-allumage', 'bougies-allumage', 'batterie']
- `lar073` (texte privé) : attendu ['sonde-temperature'], obtenu ['bougies-prechauffage', 'batterie', 'demarreur']
- `lar080` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['pompe-carburant', 'injecteurs', 'demarreur']
- `lar081` (texte privé) : attendu ['support-moteur'], obtenu ['courroie-accessoires', 'alternateur', 'batterie']
- `lar084` (texte privé) : attendu ['pompe-carburant'], obtenu ['capteur-vilebrequin', 'alternateur', 'demarreur']
- `lar088` (texte privé) : attendu ['courroie-accessoires'], obtenu ['pompe-direction']
- `lar089` (texte privé) : attendu ['maitre-cylindre'], obtenu ['flexible-frein', 'plaquettes-avant', 'disques-frein']
- `lar096` (texte privé) : attendu ['silentblocs'], obtenu ['cardans', 'biellette-stabilisatrice']
- `lar097` (texte privé) : attendu ['bougies-allumage'], obtenu ['filtre-air', 'debitmetre', 'injecteurs']
- `lar098` (texte privé) : attendu ['batterie'], obtenu ['demarreur']
- `lar100` (texte privé) : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'turbocompresseur', 'thermostat']
- `lar102` (texte privé) : attendu ['flexible-frein'], obtenu ['plaquettes-avant', 'disques-frein', 'etrier-frein']
- `lar104` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bobine-allumage', 'bougies-allumage']

### CBP-a0.25 / D (chaîne complète) | largus_controle (19)
- `ctl001` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'demarreur', 'alternateur']
- `ctl003` (texte privé) : attendu ['batterie'], obtenu ['alternateur', 'boite-vitesses']
- `ctl004` (texte privé) : attendu ['thermostat'], obtenu ['capteur-vilebrequin', 'alternateur', 'batterie']
- `ctl008` (texte privé) : attendu ['triangles'], obtenu ['plaquettes-avant', 'disques-frein', 'cardans']
- `ctl009` (texte privé) : attendu ['debitmetre'], obtenu ['alternateur', 'batterie']
- `ctl014` (texte privé) : attendu ['ampoules'], obtenu ['batterie', 'alternateur', 'demarreur']
- `ctl015` (texte privé) : attendu ['pompe-carburant'], obtenu ['bobine-allumage', 'bougies-allumage', 'batterie']
- `ctl018` (texte privé) : attendu ['injecteurs'], obtenu ['kit-embrayage', 'cable-embrayage', 'boite-vitesses']
- `ctl019` (texte privé) : attendu ['pompe-carburant'], obtenu ['sonde-lambda', 'catalyseur']
- `ctl020` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['injecteurs', 'bougies-prechauffage', 'pompe-carburant']
- `ctl021` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'alternateur', 'demarreur']
- `ctl022` (texte privé) : attendu ['papillon-motorise'], obtenu ['alternateur']
- `ctl025` (texte privé) : attendu ['filtre-carburant'], obtenu ['bougies-allumage', 'bobine-allumage', 'papillon-motorise']
- `ctl028` (texte privé) : attendu ['batterie'], obtenu ['pompe-carburant', 'bougies-allumage', 'bobine-allumage']
- `ctl030` (texte privé) : attendu ['turbocompresseur'], obtenu ['injecteurs', 'bobine-allumage', 'pompe-carburant']
- `ctl031` (texte privé) : attendu ['turbocompresseur'], obtenu ['debitmetre', 'papillon-motorise', 'boite-vitesses']
- `ctl038` (texte privé) : attendu ['cardans'], obtenu ['disques-frein', 'boite-vitesses', 'roulements-roue']
- `ctl039` (texte privé) : attendu ['debitmetre'], obtenu ['kit-embrayage', 'boite-vitesses', 'cable-embrayage']
- `ctl043` (texte privé) : attendu ['batterie'], obtenu ['bougies-prechauffage', 'demarreur']

### CBP-a0.25 / D (chaîne complète) | techniconnexion_controle (13)
- `tecc002` (texte privé) : attendu ['papillon-motorise'], obtenu ['pompe-carburant', 'alternateur', 'bobine-allumage']
- `tecc003` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['pompe-carburant']
- `tecc004` (texte privé) : attendu ['ventilateur-radiateur'], obtenu ['joint-culasse', 'pompe-eau', 'radiateur']
- `tecc006` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'alternateur', 'demarreur']
- `tecc009` (texte privé) : attendu ['bougies-allumage'], obtenu ['demarreur', 'kit-distribution', 'bougies-prechauffage']
- `tecc011` (texte privé) : attendu ['support-moteur'], obtenu ['injecteurs']
- `tecc012` (texte privé) : attendu ['pompe-carburant'], obtenu ['batterie', 'demarreur', 'alternateur']
- `tecc013` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['bobine-allumage', 'bougies-allumage']
- `tecc014` (texte privé) : attendu ['ventilateur-radiateur'], obtenu ['compresseur-clim']
- `tecc021` (texte privé) : attendu ['papillon-motorise'], obtenu ['injecteurs', 'pompe-carburant', 'boite-vitesses']
- `tecc027` (texte privé) : attendu ['courroie-accessoires'], obtenu ['alternateur', 'demarreur', 'catalyseur']
- `tecc030` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['batterie', 'alternateur', 'demarreur']
- `tecc039` (texte privé) : attendu ['capteur-vilebrequin'], obtenu ['papillon-motorise', 'debitmetre', 'vanne-egr']
