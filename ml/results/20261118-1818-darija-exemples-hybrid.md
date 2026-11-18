# Résultats 20261118-1818 darija-exemples-hybrid

Modèle de langage : `none`. Jeux : audit_ecriture_oran, audit_ecriture_oran_controle, dev_fr_synthetique, demo_cases.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran | 45 | 82% | 89% | 7% | 100% | 5860.5 / 6443.8 |
| A / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 75% | 4762.4 / 5941.5 |
| A / D (chaîne complète) | tfidf-lr-fault-20261118 | dev_fr_synthetique | 50 | 92% | 98% | 2% | 100% | 4786.0 / 6040.0 |
| A / D (chaîne complète) | tfidf-lr-fault-20261118 | demo_cases | 17 | 94% | 100% | 0% | 100% | 5206.8 / 6675.1 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A / D (chaîne complète) | audit_ecriture_oran (5)
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu ['amortisseurs', 'papillon-motorise', 'rotules-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown

### A / D (chaîne complète) | audit_ecriture_oran_controle (1)
- `ctl20` 'nheb nechri tomobil jdida' : attendu je ne sais pas, obtenu ['bougies-allumage', 'alternateur', 'pompe-carburant']

### A / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A / D (chaîne complète) | demo_cases (0)
- aucune
