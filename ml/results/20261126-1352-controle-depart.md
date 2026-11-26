# Résultats 20261126-1352 controle-depart

Modèle de langage : `none`. Jeux : largus_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| en-service / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261126 | largus_controle | 43 | 37% | 58% | 14% | – | 2181.7 / 512.5 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

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
