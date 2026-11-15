# Résultats 20261114-1831 comparaison-A-B

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-amorcage / classifieur seul | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 88% | 92% | 6% | 100% | 563.9 / 123.3 |
| A-amorcage / classifieur seul | tfidf-lr-fault-20261114 | demo_cases | 17 | 94% | 100% | 0% | 100% | 90.1 / 109.3 |
| A-amorcage / D (chaîne complète) | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 86% | 94% | 6% | 100% | 93.1 / 121.2 |
| A-amorcage / D (chaîne complète) | tfidf-lr-fault-20261114 | demo_cases | 17 | 94% | 100% | 0% | 100% | 94.7 / 114.1 |
| A-corpus-panne / classifieur seul | tfidf-lr-fault-corpus-20261114 | dev_fr_synthetique | 50 | 80% | 96% | 2% | 60% | 90.0 / 111.0 |
| A-corpus-panne / classifieur seul | tfidf-lr-fault-corpus-20261114 | demo_cases | 17 | 82% | 94% | 6% | 100% | 88.9 / 103.4 |
| A-corpus-panne / D (chaîne complète) | tfidf-lr-fault-corpus-20261114 | dev_fr_synthetique | 50 | 82% | 96% | 2% | 80% | 92.3 / 119.0 |
| A-corpus-panne / D (chaîne complète) | tfidf-lr-fault-corpus-20261114 | demo_cases | 17 | 88% | 94% | 6% | 100% | 83.3 / 94.5 |
| A-corpus-piece / classifieur seul | tfidf-lr-part-corpus-20261114 | dev_fr_synthetique | 50 | 74% | 82% | 12% | 80% | 94.5 / 110.7 |
| A-corpus-piece / classifieur seul | tfidf-lr-part-corpus-20261114 | demo_cases | 17 | 82% | 82% | 12% | 100% | 102.1 / 122.8 |
| A-corpus-piece / D (chaîne complète) | tfidf-lr-part-corpus-20261114 | dev_fr_synthetique | 50 | 76% | 84% | 12% | 80% | 98.2 / 126.7 |
| A-corpus-piece / D (chaîne complète) | tfidf-lr-part-corpus-20261114 | demo_cases | 17 | 82% | 88% | 6% | 100% | 88.6 / 110.2 |
| B-fr / classifieur seul | mmBERT-base_fr-20261114 | dev_fr_synthetique | 50 | 58% | 78% | 6% | 60% | 197.6 / 240.0 |
| B-fr / classifieur seul | mmBERT-base_fr-20261114 | demo_cases | 17 | 59% | 65% | 6% | 100% | 185.3 / 231.7 |
| B-fr / D (chaîne complète) | mmBERT-base_fr-20261114 | dev_fr_synthetique | 50 | 62% | 84% | 4% | 60% | 180.0 / 224.7 |
| B-fr / D (chaîne complète) | mmBERT-base_fr-20261114 | demo_cases | 17 | 59% | 76% | 12% | 100% | 181.7 / 215.7 |
| B-enfr / classifieur seul | mmBERT-base_en-fr-20261114 | dev_fr_synthetique | 50 | 56% | 76% | 2% | 40% | 201.9 / 264.5 |
| B-enfr / classifieur seul | mmBERT-base_en-fr-20261114 | demo_cases | 17 | 41% | 65% | 0% | 100% | 185.4 / 225.5 |
| B-enfr / D (chaîne complète) | mmBERT-base_en-fr-20261114 | dev_fr_synthetique | 50 | 60% | 86% | 4% | 40% | 185.8 / 232.4 |
| B-enfr / D (chaîne complète) | mmBERT-base_en-fr-20261114 | demo_cases | 17 | 53% | 65% | 6% | 100% | 181.1 / 220.8 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A-amorcage / classifieur seul | dev_fr_synthetique (4)
- `dev007` "j'entends juste un clic quand je mets le contact mais le moteur ne se lance pas, les feux " : attendu ['demarreur', 'batterie'], obtenu ['pompe-carburant']
- `dev021` 'quand je braque complètement en accélérant ça claque côté roue avant gauche' : attendu ['cardans'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu unknown

### A-amorcage / classifieur seul | demo_cases (0)
- aucune

### A-amorcage / D (chaîne complète) | dev_fr_synthetique (3)
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu unknown

### A-amorcage / D (chaîne complète) | demo_cases (0)
- aucune

### A-corpus-panne / classifieur seul | dev_fr_synthetique (4)
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu ['boite-vitesses', 'catalyseur', 'filtre-air']
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev051` 'le prix du carburant a encore augmenté cette semaine' : attendu je ne sais pas, obtenu ['pompe-carburant', 'injecteurs']
- `dev053` 'je voudrais vendre ma voiture, combien elle vaut' : attendu je ne sais pas, obtenu ['boite-vitesses', 'demarreur', 'amortisseurs']

### A-corpus-panne / classifieur seul | demo_cases (1)
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-corpus-panne / D (chaîne complète) | dev_fr_synthetique (3)
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu ['boite-vitesses', 'catalyseur']
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev051` 'le prix du carburant a encore augmenté cette semaine' : attendu je ne sais pas, obtenu ['pompe-carburant', 'injecteurs']

### A-corpus-panne / D (chaîne complète) | demo_cases (1)
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-corpus-piece / classifieur seul | dev_fr_synthetique (10)
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev014` "sur l'autoroute la température grimpe vite alors que le ventilateur tourne" : attendu ['thermostat', 'pompe-eau', 'radiateur'], obtenu ['ventilateur-radiateur']
- `dev018` 'la voiture se balance longtemps après un ralentisseur et elle penche dans les virages' : attendu ['amortisseurs', 'coupelles', 'ressorts'], obtenu unknown
- `dev023` "en montée le moteur s'emballe mais la voiture n'accélère presque pas" : attendu ['kit-embrayage'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']
- `dev030` 'le démarreur tourne mais le moteur ne prend pas, la jauge indique un demi-réservoir' : attendu ['pompe-carburant', 'filtre-carburant', 'capteur-vilebrequin'], obtenu ['demarreur', 'batterie']
- `dev035` "une fois chaud le moteur coupe net et ne repart qu'après une demi-heure" : attendu ['capteur-vilebrequin'], obtenu unknown
- `dev043` 'ça patine et ça sent le brûlé quand je démarre en côte' : attendu ['kit-embrayage'], obtenu unknown
- `dev051` 'le prix du carburant a encore augmenté cette semaine' : attendu je ne sais pas, obtenu ['pompe-carburant', 'injecteurs', 'turbocompresseur']

### A-corpus-piece / classifieur seul | demo_cases (3)
- `demo_cases002` "au feu rouge l'aiguille de température grimpe, sur la route ça va" : attendu ['ventilateur-radiateur', 'sonde-temperature'], obtenu unknown
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu ['joint-culasse', 'joint-cache-culbuteurs', 'support-moteur']
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### A-corpus-piece / D (chaîne complète) | dev_fr_synthetique (9)
- `dev008` "la voiture broute à bas régime et la consommation d'essence a augmenté" : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev014` "sur l'autoroute la température grimpe vite alors que le ventilateur tourne" : attendu ['thermostat', 'pompe-eau', 'radiateur'], obtenu ['ventilateur-radiateur']
- `dev018` 'la voiture se balance longtemps après un ralentisseur et elle penche dans les virages' : attendu ['amortisseurs', 'coupelles', 'ressorts'], obtenu unknown
- `dev023` "en montée le moteur s'emballe mais la voiture n'accélère presque pas" : attendu ['kit-embrayage'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']
- `dev035` "une fois chaud le moteur coupe net et ne repart qu'après une demi-heure" : attendu ['capteur-vilebrequin'], obtenu unknown
- `dev043` 'ça patine et ça sent le brûlé quand je démarre en côte' : attendu ['kit-embrayage'], obtenu unknown
- `dev051` 'le prix du carburant a encore augmenté cette semaine' : attendu je ne sais pas, obtenu ['pompe-carburant', 'injecteurs', 'turbocompresseur']

### A-corpus-piece / D (chaîne complète) | demo_cases (2)
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu ['joint-culasse', 'joint-cache-culbuteurs', 'support-moteur']
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### B-fr / classifieur seul | dev_fr_synthetique (13)
- `dev007` "j'entends juste un clic quand je mets le contact mais le moteur ne se lance pas, les feux " : attendu ['demarreur', 'batterie'], obtenu ['joint-culasse', 'support-moteur', 'joint-cache-culbuteurs']
- `dev018` 'la voiture se balance longtemps après un ralentisseur et elle penche dans les virages' : attendu ['amortisseurs', 'coupelles', 'ressorts'], obtenu ['biellette-stabilisatrice', 'courroie-accessoires', 'support-moteur']
- `dev020` "un bourdonnement qui s'amplifie avec la vitesse, il change de ton quand je prends un virag" : attendu ['roulements-roue'], obtenu ['kit-embrayage', 'boite-vitesses', 'cable-embrayage']
- `dev021` 'quand je braque complètement en accélérant ça claque côté roue avant gauche' : attendu ['cardans'], obtenu ['rotules-direction', 'amortisseurs', 'etrier-frein']
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev026` "voyant moteur orange fixe et odeur d'oeuf pourri derrière la voiture" : attendu ['sonde-lambda', 'catalyseur'], obtenu ['injecteurs']
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu unknown
- `dev038` 'grosses vibrations dans la caisse au ralenti et choc quand je passe la marche arrière' : attendu ['support-moteur'], obtenu ['disques-frein', 'plaquettes-avant']
- `dev043` 'ça patine et ça sent le brûlé quand je démarre en côte' : attendu ['kit-embrayage'], obtenu ['courroie-accessoires', 'demarreur', 'alternateur']
- `dev045` 'un cylindre ne fonctionne pas, la valise indique un raté sur le cylindre 2' : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev051` 'le prix du carburant a encore augmenté cette semaine' : attendu je ne sais pas, obtenu ['injecteurs', 'pompe-carburant', 'turbocompresseur']
- `dev055` 'comment changer le mot de passe de mon compte' : attendu je ne sais pas, obtenu ['alternateur', 'demarreur', 'etrier-frein']

### B-fr / classifieur seul | demo_cases (6)
- `demo_cases002` "au feu rouge l'aiguille de température grimpe, sur la route ça va" : attendu ['ventilateur-radiateur', 'sonde-temperature'], obtenu ['thermostat', 'radiateur']
- `demo_cases008` "mon diesel a du mal à partir les matins d'hiver, il fume blanc" : attendu ['bougies-prechauffage'], obtenu ['pompe-carburant', 'debitmetre', 'courroie-accessoires']
- `demo_cases009` "en braquant complètement pour me garer j'entends clac clac" : attendu ['cardans'], obtenu ['plaquettes-avant', 'etrier-frein', 'flexible-frein']
- `demo_cases011` 'un liquide rose coule sous le moteur et le niveau du bocal baisse' : attendu ['radiateur', 'pompe-eau', 'durite-refroidissement'], obtenu ['thermostat', 'injecteurs', 'joint-culasse']
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown
- `demo_cases017` "pas d'air qui sort des aérateurs et ça sent le moisi" : attendu ['filtre-habitacle'], obtenu ['courroie-accessoires', 'alternateur', 'filtre-air']

### B-fr / D (chaîne complète) | dev_fr_synthetique (10)
- `dev018` 'la voiture se balance longtemps après un ralentisseur et elle penche dans les virages' : attendu ['amortisseurs', 'coupelles', 'ressorts'], obtenu ['biellette-stabilisatrice', 'courroie-accessoires', 'support-moteur']
- `dev020` "un bourdonnement qui s'amplifie avec la vitesse, il change de ton quand je prends un virag" : attendu ['roulements-roue'], obtenu ['kit-embrayage', 'boite-vitesses', 'pompe-carburant']
- `dev021` 'quand je braque complètement en accélérant ça claque côté roue avant gauche' : attendu ['cardans'], obtenu ['rotules-direction', 'biellette-stabilisatrice', 'amortisseurs']
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu ['pompe-carburant', 'joint-culasse', 'vanne-egr']
- `dev043` 'ça patine et ça sent le brûlé quand je démarre en côte' : attendu ['kit-embrayage'], obtenu ['courroie-accessoires', 'demarreur', 'alternateur']
- `dev045` 'un cylindre ne fonctionne pas, la valise indique un raté sur le cylindre 2' : attendu ['bougies-allumage', 'bobine-allumage', 'injecteurs'], obtenu unknown
- `dev051` 'le prix du carburant a encore augmenté cette semaine' : attendu je ne sais pas, obtenu ['injecteurs', 'pompe-carburant', 'turbocompresseur']
- `dev055` 'comment changer le mot de passe de mon compte' : attendu je ne sais pas, obtenu ['alternateur', 'demarreur', 'etrier-frein']

### B-fr / D (chaîne complète) | demo_cases (4)
- `demo_cases002` "au feu rouge l'aiguille de température grimpe, sur la route ça va" : attendu ['ventilateur-radiateur', 'sonde-temperature'], obtenu ['thermostat', 'radiateur']
- `demo_cases008` "mon diesel a du mal à partir les matins d'hiver, il fume blanc" : attendu ['bougies-prechauffage'], obtenu ['pompe-carburant', 'debitmetre', 'courroie-accessoires']
- `demo_cases009` "en braquant complètement pour me garer j'entends clac clac" : attendu ['cardans'], obtenu unknown
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu unknown

### B-enfr / classifieur seul | dev_fr_synthetique (15)
- `dev005` 'le matin il faut plusieurs essais pour démarrer, le démarreur tourne au ralenti' : attendu ['batterie'], obtenu ['demarreur', 'bougies-prechauffage']
- `dev013` "du liquide de refroidissement goutte sous le moteur côté courroie et l'aiguille de tempéra" : attendu ['pompe-eau', 'radiateur', 'durite-refroidissement'], obtenu ['thermostat', 'kit-distribution']
- `dev016` 'en ville dans les embouteillages ça chauffe, le ventilateur ne se déclenche jamais' : attendu ['ventilateur-radiateur', 'sonde-temperature'], obtenu ['thermostat', 'radiateur']
- `dev018` 'la voiture se balance longtemps après un ralentisseur et elle penche dans les virages' : attendu ['amortisseurs', 'coupelles', 'ressorts'], obtenu ['rotules-direction', 'debitmetre', 'support-moteur']
- `dev020` "un bourdonnement qui s'amplifie avec la vitesse, il change de ton quand je prends un virag" : attendu ['roulements-roue'], obtenu ['kit-embrayage', 'rotules-direction', 'amortisseurs']
- `dev021` 'quand je braque complètement en accélérant ça claque côté roue avant gauche' : attendu ['cardans'], obtenu ['rotules-direction', 'roulements-roue', 'amortisseurs']
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev026` "voyant moteur orange fixe et odeur d'oeuf pourri derrière la voiture" : attendu ['sonde-lambda', 'catalyseur'], obtenu ['injecteurs', 'turbocompresseur', 'vanne-egr']
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'debitmetre', 'bougies-allumage']
- `dev041` "grincement aigu à l'arrière à chaque arrêt" : attendu ['plaquettes-arriere', 'plaquettes-avant', 'machoires-frein'], obtenu ['roulements-roue', 'amortisseurs', 'flexible-frein']
- `dev043` 'ça patine et ça sent le brûlé quand je démarre en côte' : attendu ['kit-embrayage'], obtenu ['courroie-accessoires', 'amortisseurs', 'etrier-frein']
- `dev051` 'le prix du carburant a encore augmenté cette semaine' : attendu je ne sais pas, obtenu ['pompe-carburant', 'injecteurs', 'turbocompresseur']
- `dev053` 'je voudrais vendre ma voiture, combien elle vaut' : attendu je ne sais pas, obtenu ['support-moteur', 'kit-distribution', 'pompe-direction']
- `dev055` 'comment changer le mot de passe de mon compte' : attendu je ne sais pas, obtenu ['alternateur', 'batterie', 'etrier-frein']

### B-enfr / classifieur seul | demo_cases (6)
- `demo_cases002` "au feu rouge l'aiguille de température grimpe, sur la route ça va" : attendu ['ventilateur-radiateur', 'sonde-temperature'], obtenu ['thermostat', 'radiateur']
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu ['bougies-allumage', 'bobine-allumage', 'courroie-accessoires']
- `demo_cases008` "mon diesel a du mal à partir les matins d'hiver, il fume blanc" : attendu ['bougies-prechauffage'], obtenu ['debitmetre', 'filtre-air', 'pompe-carburant']
- `demo_cases009` "en braquant complètement pour me garer j'entends clac clac" : attendu ['cardans'], obtenu ['flexible-frein', 'bobine-allumage', 'plaquettes-avant']
- `demo_cases011` 'un liquide rose coule sous le moteur et le niveau du bocal baisse' : attendu ['radiateur', 'pompe-eau', 'durite-refroidissement'], obtenu ['thermostat', 'injecteurs', 'rotules-direction']
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu ['thermostat', 'support-moteur', 'joint-culasse']

### B-enfr / D (chaîne complète) | dev_fr_synthetique (10)
- `dev018` 'la voiture se balance longtemps après un ralentisseur et elle penche dans les virages' : attendu ['amortisseurs', 'coupelles', 'ressorts'], obtenu ['rotules-direction', 'debitmetre', 'support-moteur']
- `dev020` "un bourdonnement qui s'amplifie avec la vitesse, il change de ton quand je prends un virag" : attendu ['roulements-roue'], obtenu unknown
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev026` "voyant moteur orange fixe et odeur d'oeuf pourri derrière la voiture" : attendu ['sonde-lambda', 'catalyseur'], obtenu ['injecteurs', 'turbocompresseur', 'vanne-egr']
- `dev027` "la voiture n'a plus de reprise et on dirait que l'échappement est bouché" : attendu ['catalyseur'], obtenu ['silencieux']
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu ['bougies-prechauffage', 'pompe-carburant', 'debitmetre']
- `dev041` "grincement aigu à l'arrière à chaque arrêt" : attendu ['plaquettes-arriere', 'plaquettes-avant', 'machoires-frein'], obtenu ['roulements-roue', 'amortisseurs']
- `dev051` 'le prix du carburant a encore augmenté cette semaine' : attendu je ne sais pas, obtenu ['pompe-carburant', 'injecteurs', 'turbocompresseur']
- `dev053` 'je voudrais vendre ma voiture, combien elle vaut' : attendu je ne sais pas, obtenu ['support-moteur', 'kit-distribution', 'disques-frein']
- `dev055` 'comment changer le mot de passe de mon compte' : attendu je ne sais pas, obtenu ['alternateur', 'batterie', 'etrier-frein']

### B-enfr / D (chaîne complète) | demo_cases (6)
- `demo_cases002` "au feu rouge l'aiguille de température grimpe, sur la route ça va" : attendu ['ventilateur-radiateur', 'sonde-temperature'], obtenu ['thermostat']
- `demo_cases003` 'ce matin tac tac tac en démarrant et le moteur ne voulait pas tourner' : attendu ['batterie', 'demarreur'], obtenu ['bougies-allumage', 'bobine-allumage', 'courroie-accessoires']
- `demo_cases008` "mon diesel a du mal à partir les matins d'hiver, il fume blanc" : attendu ['bougies-prechauffage'], obtenu ['debitmetre', 'pompe-carburant', 'filtre-air']
- `demo_cases009` "en braquant complètement pour me garer j'entends clac clac" : attendu ['cardans'], obtenu unknown
- `demo_cases011` 'un liquide rose coule sous le moteur et le niveau du bocal baisse' : attendu ['radiateur', 'pompe-eau', 'durite-refroidissement'], obtenu ['thermostat', 'injecteurs', 'rotules-direction']
- `demo_cases016` "elle s'arrête quand elle est bien chaude puis repart une fois froide" : attendu ['capteur-vilebrequin'], obtenu ['thermostat', 'support-moteur', 'joint-culasse']
