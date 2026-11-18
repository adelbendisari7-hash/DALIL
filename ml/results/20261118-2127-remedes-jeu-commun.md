# Résultats 20261118-2127 remedes-jeu-commun

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-fort-x1 / D (chaîne complète) | tfidf-lr-set-fort-20261118 | dev_fr_synthetique | 50 | 90% | 96% | 2% | 100% | 561.1 / 127.5 |
| A-fort-x1 / D (chaîne complète) | tfidf-lr-set-fort-20261118 | demo_cases | 17 | 71% | 82% | 18% | 100% | 94.1 / 107.8 |
| A-fort-x1 / D (chaîne complète) | tfidf-lr-set-fort-20261118 | audit_ecriture_oran | 45 | 87% | 89% | 7% | 100% | 94.0 / 106.8 |
| A-fort-x1 / D (chaîne complète) | tfidf-lr-set-fort-20261118 | audit_ecriture_oran_controle | 16 | 81% | 94% | 6% | 100% | 91.7 / 110.7 |
| A-fort-x5 / D (chaîne complète) | tfidf-lr-set-fort-20261118 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 97.8 / 120.4 |
| A-fort-x5 / D (chaîne complète) | tfidf-lr-set-fort-20261118 | demo_cases | 17 | 88% | 94% | 6% | 100% | 90.5 / 108.8 |
| A-fort-x5 / D (chaîne complète) | tfidf-lr-set-fort-20261118 | audit_ecriture_oran | 45 | 84% | 87% | 9% | 100% | 90.3 / 104.5 |
| A-fort-x5 / D (chaîne complète) | tfidf-lr-set-fort-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 87.6 / 101.3 |
| A-moyen-x5 / D (chaîne complète) | tfidf-lr-set-moyen-20261118 | dev_fr_synthetique | 50 | 88% | 96% | 2% | 100% | 92.0 / 109.5 |
| A-moyen-x5 / D (chaîne complète) | tfidf-lr-set-moyen-20261118 | demo_cases | 17 | 82% | 88% | 12% | 100% | 90.9 / 110.1 |
| A-moyen-x5 / D (chaîne complète) | tfidf-lr-set-moyen-20261118 | audit_ecriture_oran | 45 | 80% | 84% | 11% | 100% | 93.2 / 103.9 |
| A-moyen-x5 / D (chaîne complète) | tfidf-lr-set-moyen-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 92.0 / 106.0 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A-fort-x1 / D (chaîne complète) | dev_fr_synthetique (2)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux', 'kit-embrayage', 'boite-vitesses']

### A-fort-x1 / D (chaîne complète) | demo_cases (3)
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu unknown
- `demo_cases006` 'on entend un sifflement strident au démarrage qui part après quelques minutes' : attendu ['courroie-accessoires', 'galet-tendeur'], obtenu unknown
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-fort-x1 / D (chaîne complète) | audit_ecriture_oran (5)
- `aud04` 'la direction tir a gauche quand je roule' : attendu ['rotules-direction', 'biellettes-direction', 'triangles'], obtenu ['pompe-direction']
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-fort-x1 / D (chaîne complète) | audit_ecriture_oran_controle (1)
- `ctl16` 'ريحة ليسانس في الطوموبيل' : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown

### A-fort-x5 / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A-fort-x5 / D (chaîne complète) | demo_cases (1)
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-fort-x5 / D (chaîne complète) | audit_ecriture_oran (6)
- `aud04` 'la direction tir a gauche quand je roule' : attendu ['rotules-direction', 'biellettes-direction', 'triangles'], obtenu ['pompe-direction']
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-fort-x5 / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### A-moyen-x5 / D (chaîne complète) | dev_fr_synthetique (2)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']

### A-moyen-x5 / D (chaîne complète) | demo_cases (2)
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu unknown
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-moyen-x5 / D (chaîne complète) | audit_ecriture_oran (7)
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud22` 'tomobil ma tdemarich' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud29` "kayen dkhan k7al men l'echappement" : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu ['silencieux', 'joint-culasse', 'joint-cache-culbuteurs']
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-moyen-x5 / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune
