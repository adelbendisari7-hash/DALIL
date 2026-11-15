# Résultats 20261114-1234 hors-sujet-domaine

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-panne / classifieur seul | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 86% | 90% | 8% | 100% | 61.4 / 51.5 |
| A-panne / classifieur seul | tfidf-lr-fault-20261114 | demo_cases | 17 | 88% | 94% | 6% | 100% | 42.3 / 46.4 |
| A-panne / D (chaîne complète) | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 86% | 92% | 4% | 100% | 42.2 / 46.4 |
| A-panne / D (chaîne complète) | tfidf-lr-fault-20261114 | demo_cases | 17 | 82% | 94% | 6% | 100% | 41.8 / 46.9 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A-panne / classifieur seul | dev_fr_synthetique (5)
- `dev002` 'en freinant depuis 100 km/h tout le volant se met à trembler' : attendu ['disques-frein'], obtenu unknown
- `dev007` "j'entends juste un clic quand je mets le contact mais le moteur ne se lance pas, les feux " : attendu ['demarreur', 'batterie'], obtenu ['pompe-carburant']
- `dev021` 'quand je braque complètement en accélérant ça claque côté roue avant gauche' : attendu ['cardans'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu unknown

### A-panne / classifieur seul | demo_cases (1)
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-panne / D (chaîne complète) | dev_fr_synthetique (4)
- `dev002` 'en freinant depuis 100 km/h tout le volant se met à trembler' : attendu ['disques-frein'], obtenu unknown
- `dev007` "j'entends juste un clic quand je mets le contact mais le moteur ne se lance pas, les feux " : attendu ['demarreur', 'batterie'], obtenu ['pompe-carburant']
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu ['vanne-egr', 'support-moteur', 'bougies-allumage']

### A-panne / D (chaîne complète) | demo_cases (1)
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown
