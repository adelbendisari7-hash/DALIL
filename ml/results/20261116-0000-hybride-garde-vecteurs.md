# Résultats 20261116-0000 hybride-garde-vecteurs

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C (recherche + LM) | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 68% | 78% | 8% | 100% | 48758.0 / 69439.2 |
| C (recherche + LM) | tfidf-lr-fault-20261114 | demo_cases | 17 | 65% | 88% | 6% | 100% | 27711.2 / 39777.3 |
| A / D (chaîne complète) | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 92% | 98% | 2% | 100% | 18.2 / 36.0 |
| A / D (chaîne complète) | tfidf-lr-fault-20261114 | demo_cases | 17 | 88% | 100% | 0% | 100% | 16.3 / 26.2 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### C (recherche + LM) | dev_fr_synthetique (11)
- `dev006` "le témoin de charge rouge reste allumé quand je roule et la radio s'est éteinte" : attendu ['alternateur', 'courroie-accessoires'], obtenu ['batterie']
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu ['boite-vitesses']
- `dev011` "il y a un sifflement aigu sous le capot quand je tourne le volant à l'arrêt" : attendu ['courroie-accessoires', 'galet-tendeur', 'pompe-direction'], obtenu ['roulements-roue', 'bougies-allumage']
- `dev018` 'la voiture se balance longtemps après un ralentisseur et elle penche dans les virages' : attendu ['amortisseurs', 'coupelles', 'ressorts'], obtenu unknown
- `dev022` "toc toc à l'avant quand je passe sur les pavés doucement" : attendu ['biellette-stabilisatrice', 'silentblocs', 'amortisseurs', 'rotules-direction'], obtenu ['cardans', 'boite-vitesses', 'disques-frein']
- `dev023` "en montée le moteur s'emballe mais la voiture n'accélère presque pas" : attendu ['kit-embrayage'], obtenu ['pompe-carburant', 'filtre-air']
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev035` "une fois chaud le moteur coupe net et ne repart qu'après une demi-heure" : attendu ['capteur-vilebrequin'], obtenu unknown
- `dev039` 'le volant est devenu lourd et il gémit quand je manoeuvre' : attendu ['pompe-direction', 'cremaillere'], obtenu unknown
- `dev041` "grincement aigu à l'arrière à chaque arrêt" : attendu ['plaquettes-arriere', 'plaquettes-avant', 'machoires-frein'], obtenu ['disques-frein', 'boite-vitesses', 'demarreur']
- `dev045` 'un cylindre ne fonctionne pas, la valise indique un raté sur le cylindre 2' : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu ['kit-distribution', 'sonde-lambda']

### C (recherche + LM) | demo_cases (2)
- `demo_cases006` 'on entend un sifflement strident au démarrage qui part après quelques minutes' : attendu ['courroie-accessoires', 'galet-tendeur'], obtenu ['pompe-direction', 'pompe-carburant', 'sonde-lambda']
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A / D (chaîne complète) | dev_fr_synthetique (1)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown

### A / D (chaîne complète) | demo_cases (0)
- aucune
