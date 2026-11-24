# Résultats 20261124-1205 deux-niveaux-hybride

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases, audit_ecriture_oran, audit_ecriture_oran_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | dev_fr_synthetique | 50 | 92% | 98% | 2% | 100% | 4872.8 / 5610.9 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | demo_cases | 17 | 94% | 100% | 0% | 100% | 3499.4 / 5340.5 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran | 45 | 82% | 89% | 7% | 100% | 4680.9 / 6629.3 |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 2873.4 / 3338.2 |
| 2niv-a0.25 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261124 | dev_fr_synthetique | 50 | 92% | 98% | 2% | 100% | 9.4 / 15.4 |
| 2niv-a0.25 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261124 | demo_cases | 17 | 94% | 100% | 0% | 100% | 7.2 / 9.5 |
| 2niv-a0.25 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261124 | audit_ecriture_oran | 45 | 87% | 91% | 7% | 100% | 5.8 / 6.6 |
| 2niv-a0.25 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261124 | audit_ecriture_oran_controle | 16 | 94% | 100% | 0% | 100% | 5.9 / 7.2 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A-actuel / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A-actuel / D (chaîne complète) | demo_cases (0)
- aucune

### A-actuel / D (chaîne complète) | audit_ecriture_oran (5)
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu ['amortisseurs', 'papillon-motorise', 'rotules-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A-actuel / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### 2niv-a0.25 / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### 2niv-a0.25 / D (chaîne complète) | demo_cases (0)
- aucune

### 2niv-a0.25 / D (chaîne complète) | audit_ecriture_oran (4)
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### 2niv-a0.25 / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune
