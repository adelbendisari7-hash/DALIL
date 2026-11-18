# Résultats 20261118-1802 controle-avant-hybrid

Modèle de langage : `none`. Jeux : audit_ecriture_oran_controle.

| Variante | Modèle | Jeu | n | Top-1 | Top-3 | Abstention | Hors sujet refusé | ms (moy. / p95) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A / D (chaîne complète) | tfidf-lr-fault-20261114 | audit_ecriture_oran_controle | 16 | 19% | 38% | 56% | 100% | 4006.1 / 3796.3 |

## Erreurs (pièce attendue absente du top-3, ou hors sujet accepté)

### A / D (chaîne complète) | audit_ecriture_oran_controle (10)
- `ctl01` 'loto ma theza9ch ki ndir contact, ghir tak tak' : attendu ['batterie', 'demarreur'], obtenu unknown
- `ctl04` 'siyara t3ayi f la monté w ma tetla3ch' : attendu ['kit-embrayage', 'turbocompresseur', 'filtre-carburant', 'injecteurs', 'filtre-air'], obtenu unknown
- `ctl05` 'kayen tak tak f la roue ki ndour' : attendu ['cardans', 'rotules-direction', 'roulements-roue'], obtenu unknown
- `ctl07` 'el moteur yakel zit bezaf' : attendu ['joint-culasse', 'turbocompresseur', 'huile-moteur', 'joint-cache-culbuteurs'], obtenu ['injecteurs', 'bobine-allumage', 'debitmetre']
- `ctl11` 'السيارة تسخن في الطريق' : attendu ['thermostat', 'radiateur', 'pompe-eau', 'ventilateur-radiateur', 'durite-refroidissement', 'vase-expansion'], obtenu unknown
- `ctl12` 'الفران يصفر بزاف' : attendu ['plaquettes-avant', 'plaquettes-arriere', 'disques-frein'], obtenu unknown
- `ctl13` 'الباطري ماتشارجيش' : attendu ['batterie', 'alternateur'], obtenu unknown
- `ctl14` 'دخان كحل من الشكمان' : attendu ['injecteurs', 'turbocompresseur', 'filtre-air', 'debitmetre', 'vanne-egr'], obtenu unknown
- `ctl15` 'الكليماتيزور ما يبردش' : attendu ['compresseur-clim', 'condenseur'], obtenu unknown
- `ctl16` 'ريحة ليسانس في الطوموبيل' : attendu ['injecteurs', 'pompe-carburant', 'filtre-carburant'], obtenu unknown
