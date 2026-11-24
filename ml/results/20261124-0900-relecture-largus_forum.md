# Relecture des étiquettes : largus_forum (2026-11-24 09:00)

Justesse de la pièce, repondérée par la taille de chaque niveau : **29%**

| Niveau | Relus | Pièce juste | Intervalle 95 % | Famille juste | Population | Décision | Poids conseillé |
| --- | ---: | ---: | --- | ---: | ---: | --- | ---: |
| auteur | 18 | 6% | 1%–26% | 11% | 7493 | écarter | 0.0 |
| auteur+component | 16 | 62% | 39%–82% | 75% | 2566 | garder avec un poids réduit | 0.62 |
| component | 19 | 0% | 0%–17% | 90% | 3704 | écarter | 0.0 |
| question | 18 | 11% | 3%–33% | 44% | 14768 | écarter | 0.0 |
| question+component | 20 | 65% | 43%–82% | 85% | 8520 | garder avec un poids réduit | 0.65 |
| reponses | 17 | 29% | 13%–53% | 47% | 25481 | écarter | 0.0 |
| reponses+component | 20 | 45% | 26%–66% | 85% | 9747 | écarter | 0.0 |
| solution | 18 | 22% | 9%–45% | 67% | 3317 | écarter | 0.0 |
| solution+component | 18 | 39% | 20%–61% | 78% | 1006 | écarter | 0.0 |

Règle : pièce juste ≥ 80 % -> garder ; 60 à 80 % -> garder avec un poids égal à la justesse ; moins de 60 % -> écarter. Reporter les poids dans ml/build_training_set.py (QUALITY_WEIGHT).
Avec une dizaine de lectures par niveau, l'intervalle est large : relire plus (--n 200) si une décision tient à quelques points.

Corrections les plus fréquentes : Joint de culasse (3), Pompe d'injection (2), Commodo (2), Antidémarrage (2), Calculateur d'injection (2), Batterie ou masse (1), Module de commande du motoventilateur (1), Pompe d'injection (calage) (1), Servofrein (mastervac) (1), Huile de boîte (1)
