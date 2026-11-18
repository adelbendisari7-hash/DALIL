# Résultats 20261118-1817 darija-exemples-keyword

Modèle de langage : `none`. Jeux : audit_ecriture_oran, audit_ecriture_oran_controle, dev_fr_synthetique, demo_cases.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran | 45 | 82% | 87% | 9% | 67% | 674.1 / 103.9 |
| A / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 96.3 / 158.3 |
| A / D (chaîne complète) | tfidf-lr-fault-20261118 | dev_fr_synthetique | 50 | 90% | 98% | 2% | 100% | 80.5 / 94.9 |
| A / D (chaîne complète) | tfidf-lr-fault-20261118 | demo_cases | 17 | 94% | 100% | 0% | 100% | 87.7 / 111.7 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A / D (chaîne complète) | audit_ecriture_oran (7)
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud21` 'el frein ysoni' : attendu ['plaquettes-avant', 'plaquettes-arriere', 'disques-frein'], obtenu unknown
- `aud31` "kayen ri7a ta3 l'essence" : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'pompe-direction']
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu ['amortisseurs', 'papillon-motorise', 'rotules-direction']
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud47` 'chhal soum el gasoil lyoum' : attendu je ne sais pas, obtenu ['bougies-prechauffage', 'pompe-carburant']

### A / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### A / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A / D (chaîne complète) | demo_cases (0)
- aucune
