# Résultats 20261124-1204 deux-niveaux-controle

Modèle de langage : `none`. Jeux : audit_ecriture_oran_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-actuel / D (chaîne complète) | tfidf-lr-fault-20261118 | audit_ecriture_oran_controle | 16 | 88% | 100% | 0% | 100% | 1171.5 / 101.3 |
| 2niv-a0.25 / D (chaîne complète) | tfidf-lr-fault-20261118+familles-largus-fort-a0.25-20261124 | audit_ecriture_oran_controle | 16 | 94% | 100% | 0% | 100% | 83.9 / 101.2 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A-actuel / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune

### 2niv-a0.25 / D (chaîne complète) | audit_ecriture_oran_controle (0)
- aucune
