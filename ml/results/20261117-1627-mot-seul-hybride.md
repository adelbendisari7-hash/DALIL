# Résultats 20261117-1627 mot-seul-hybride

Modèle de langage : `none`. Jeux : dev_fr_synthetique, demo_cases.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A / D (chaîne complète) | tfidf-lr-fault-20261114 | dev_fr_synthetique | 50 | 90% | 96% | 4% | 100% | 4046.2 / 4342.1 |
| A / D (chaîne complète) | tfidf-lr-fault-20261114 | demo_cases | 17 | 88% | 100% | 0% | 100% | 3724.1 / 4675.4 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A / D (chaîne complète) | dev_fr_synthetique (2)
- `dev025` 'la troisième craque et refuse parfois de rentrer' : attendu ['boite-vitesses', 'kit-embrayage'], obtenu unknown
- `dev029` 'le moteur cliquette fort au ralenti et sent le gasoil' : attendu ['injecteurs'], obtenu unknown

### A / D (chaîne complète) | demo_cases (0)
- aucune
