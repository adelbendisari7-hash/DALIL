# Résultats 20261118-1805 darija-keyword

Modèle de langage : `none`. Jeux : audit_ecriture_oran, audit_ecriture_oran_controle, dev_fr_synthetique, demo_cases.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A / D (chaîne complète) | tfidf-lr-fault-20261114 | audit_ecriture_oran | 45 | 67% | 76% | 22% | 67% | 695.6 / 170.9 |
| A / D (chaîne complète) | tfidf-lr-fault-20261114 | audit_ecriture_oran_controle | 16 | 94% | 94% | 6% | 100% | 104.6 / 145.9 |
| A / D (chaîne complète) | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 86% | 94% | 6% | 100% | 98.5 / 149.4 |
| A / D (chaîne complète) | tfidf-lr-fault-20261114 | demo_cases | 17 | 94% | 100% | 0% | 100% | 83.3 / 98.9 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A / D (chaîne complète) | audit_ecriture_oran (12)
- `aud02` 'ma voitur demare pa le matin ca fait tac tac' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud07` 'fumé noir a lechapement et ca consome bcp' : attendu ['injecteurs', 'filtre-air', 'turbocompresseur', 'debitmetre', 'vanne-egr'], obtenu unknown
- `aud09` 'les vitesse rentre mal surtout la 2' : attendu ['kit-embrayage', 'boite-vitesses', 'cable-embrayage'], obtenu unknown
- `aud17` 'phare avant grillé' : attendu ['ampoules'], obtenu unknown
- `aud19` 'ca cale au ralenti au feu rouge' : attendu ['papillon-motorise', 'vanne-egr', 'capteur-vilebrequin', 'debitmetre', 'bougies-allumage'], obtenu unknown
- `aud24` 'kayen bruit f la roue avant' : attendu ['roulements-roue', 'cardans', 'triangles'], obtenu unknown
- `aud32` 'ki ndour el volant tsoni tak tak' : attendu ['cardans'], obtenu ['rotules-direction', 'courroie-accessoires', 'pompe-direction']
- `aud33` 'el phare ma ycha3elch' : attendu ['ampoules'], obtenu unknown
- `aud36` 'tomobil tetfa wahedha f la route' : attendu ['capteur-vilebrequin', 'pompe-carburant', 'filtre-carburant', 'alternateur'], obtenu unknown
- `aud42` 'الطوموبيل ما تديماريش في الصباح' : attendu ['batterie', 'demarreur'], obtenu unknown
- `aud45` 'كاين صوت في الروضة القدامية' : attendu ['roulements-roue', 'cardans', 'triangles'], obtenu unknown
- `aud47` 'chhal soum el gasoil lyoum' : attendu je ne sais pas, obtenu ['bougies-prechauffage', 'pompe-carburant', 'debitmetre']

### A / D (chaîne complète) | audit_ecriture_oran_controle (1)
- `ctl16` 'ريحة ليسانس في الطوموبيل' : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown

### A / D (chaîne complète) | dev_fr_synthetique (3)
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu unknown

### A / D (chaîne complète) | demo_cases (0)
- aucune
