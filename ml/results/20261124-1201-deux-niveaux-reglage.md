# Résultats 20261124-1201 deux-niveaux-reglage

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 981.3 / 325.9 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | demo_cases | 17 | 94% | 100% | 0% | 100% | 282.8 / 346.6 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran | 45 | 82% | 87% | 9% | 100% | 274.6 / 335.0 |
| 2niv-a0.25 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261124 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 270.9 / 306.3 |
| 2niv-a0.25 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261124 | demo_cases | 17 | 94% | 100% | 0% | 100% | 274.9 / 308.8 |
| 2niv-a0.25 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261124 | audit_ecriture_oran | 45 | 84% | 91% | 7% | 100% | 267.6 / 310.4 |
| 2niv-a0.5 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.5-20261124 | dev_fr_synthetique | 50 | 94% | 98% | 2% | 100% | 268.0 / 318.9 |
| 2niv-a0.5 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.5-20261124 | demo_cases | 17 | 94% | 100% | 0% | 100% | 256.9 / 288.1 |
| 2niv-a0.5 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.5-20261124 | audit_ecriture_oran | 45 | 80% | 91% | 7% | 100% | 248.0 / 269.9 |
| 2niv-a1 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a1-20261124 | dev_fr_synthetique | 50 | 92% | 98% | 2% | 80% | 103.5 / 257.6 |
| 2niv-a1 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a1-20261124 | demo_cases | 17 | 88% | 100% | 0% | 100% | 83.5 / 103.0 |
| 2niv-a1 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a1-20261124 | audit_ecriture_oran | 45 | 80% | 91% | 4% | 100% | 80.5 / 90.8 |
| 2niv-a2 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a2-20261124 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 80% | 85.4 / 102.6 |
| 2niv-a2 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a2-20261124 | demo_cases | 17 | 82% | 94% | 0% | 100% | 81.8 / 101.3 |
| 2niv-a2 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a2-20261124 | audit_ecriture_oran | 45 | 76% | 84% | 4% | 100% | 79.6 / 98.1 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

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

### 2niv-a0.25 / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### 2niv-a0.25 / D (chaîne complète) | demo_cases (0)
- aucune

### 2niv-a0.25 / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### 2niv-a0.5 / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### 2niv-a0.5 / D (chaîne complète) | demo_cases (0)
- aucune

### 2niv-a0.5 / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### 2niv-a1 / D (chaîne complète) | dev_fr_synthetique (2)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev055` 'comment changer le mot de passe de mon compte' : attendu je ne sais pas, obtenu ['boite-vitesses', 'kit-embrayage', 'cable-embrayage']

### 2niv-a1 / D (chaîne complète) | demo_cases (0)
- aucune

### 2niv-a1 / D (chaîne complète) | audit_ecriture_oran (4)
- `aud13` 'fumee blanche et le liquide de refroidissement baisse' : attendu ['joint-culasse'], obtenu ['pompe-eau', 'radiateur', 'kit-distribution']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### 2niv-a2 / D (chaîne complète) | dev_fr_synthetique (2)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev055` 'comment changer le mot de passe de mon compte' : attendu je ne sais pas, obtenu ['boite-vitesses', 'cable-embrayage', 'kit-embrayage']

### 2niv-a2 / D (chaîne complète) | demo_cases (1)
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu ['thermostat', 'ventilateur-radiateur', 'radiateur']

### 2niv-a2 / D (chaîne complète) | audit_ecriture_oran (7)
- `aud06` 'bruit clak clak quand je tourne le volan a fond' : attendu ['cardans'], obtenu ['pompe-direction', 'rotules-direction', 'batterie']
- `aud13` 'fumee blanche et le liquide de refroidissement baisse' : attendu ['joint-culasse'], obtenu ['pompe-eau', 'radiateur', 'kit-distribution']
- `aud22` 'tomobil ma tdemarich' : attendu ['batterie', 'demarreur'], obtenu ['pompe-carburant', 'bougies-prechauffage', 'bougies-allumage']
- `aud29` "kayen dkhan k7al men l'echappement" : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'catalyseur', 'joint-culasse']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown
