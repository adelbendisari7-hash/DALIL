# Résultats 20261114-1235 poids-recherche

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-panne / classifieur seul | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 88% | 92% | 6% | 100% | 62.2 / 49.7 |
| A-panne / classifieur seul | tfidf-lr-fault-20261114 | demo_cases | 17 | 94% | 100% | 0% | 100% | 41.8 / 48.1 |
| C (recherche + LM) | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 78% | 88% | 4% | 80% | 41.4 / 50.3 |
| C (recherche + LM) | tfidf-lr-fault-20261114 | demo_cases | 17 | 88% | 94% | 0% | 100% | 40.0 / 44.0 |
| A-piece / classifieur seul | tfidf-lr-part-20261114 | dev_fr_synthetique | 50 | 86% | 90% | 8% | 100% | 46.8 / 52.2 |
| A-piece / classifieur seul | tfidf-lr-part-20261114 | demo_cases | 17 | 94% | 100% | 0% | 100% | 48.2 / 54.3 |
| A-piece / D (chaîne complète) | tfidf-lr-part-20261114 | dev_fr_synthetique | 50 | 88% | 94% | 2% | 100% | 47.5 / 53.2 |
| A-piece / D (chaîne complète) | tfidf-lr-part-20261114 | demo_cases | 17 | 94% | 100% | 0% | 100% | 47.2 / 52.0 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A-panne / classifieur seul | dev_fr_synthetique (4)
- `dev007` "j'entends juste un clic quand je mets le contact mais le moteur ne se lance pas, les feux " : attendu ['demarreur', 'batterie'], obtenu ['pompe-carburant']
- `dev021` 'quand je braque complètement en accélérant ça claque côté roue avant gauche' : attendu ['cardans'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu unknown

### A-panne / classifieur seul | demo_cases (0)
- aucune

### C (recherche + LM) | dev_fr_synthetique (7)
- `dev001` "quand j'appuie sur la pédale de frein j'entends un frottement métallique à l'avant" : attendu ['plaquettes-avant', 'disques-frein'], obtenu unknown
- `dev007` "j'entends juste un clic quand je mets le contact mais le moteur ne se lance pas, les feux " : attendu ['demarreur', 'batterie'], obtenu ['pompe-carburant']
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu ['filtre-air', 'kit-embrayage', 'turbocompresseur']
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu ['vanne-egr', 'support-moteur']
- `dev045` 'un cylindre ne fonctionne pas, la valise indique un raté sur le cylindre 2' : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev055` 'comment changer le mot de passe de mon compte' : attendu je ne sais pas, obtenu ['capteur-vilebrequin', 'roulements-roue']

### C (recherche + LM) | demo_cases (1)
- `demo_cases002` "au feu rouge l'aiguille de température grimpe, sur la route ça va" : attendu ['ventilateur-radiateur', 'sonde-temperature'], obtenu ['thermostat']

### A-piece / classifieur seul | dev_fr_synthetique (5)
- `dev007` "j'entends juste un clic quand je mets le contact mais le moteur ne se lance pas, les feux " : attendu ['demarreur', 'batterie'], obtenu ['pompe-carburant']
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev021` 'quand je braque complètement en accélérant ça claque côté roue avant gauche' : attendu ['cardans'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu unknown

### A-piece / classifieur seul | demo_cases (0)
- aucune

### A-piece / D (chaîne complète) | dev_fr_synthetique (3)
- `dev007` "j'entends juste un clic quand je mets le contact mais le moteur ne se lance pas, les feux " : attendu ['demarreur', 'batterie'], obtenu ['pompe-carburant']
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu ['support-moteur', 'vanne-egr', 'bougies-allumage']

### A-piece / D (chaîne complète) | demo_cases (0)
- aucune
