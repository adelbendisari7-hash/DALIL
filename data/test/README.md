# Jeux de test

| Fichier | Contenu | Usage |
| --- | --- | --- |
| `oran_test.jsonl` | **Jeu de test figé** : 200 cas réels d'Oran annotés par des mécaniciens partenaires (à constituer) | Seule mesure valable pour le mémoire. Jamais utilisé pour entraîner ni pour régler un seuil |
| `dev_fr_synthetique.jsonl` | 55 cas rédigés par l'équipe (50 pannes, 5 hors sujet), formulations absentes des exemples d'entraînement | Réglage des seuils et comparaison rapide des variantes pendant le développement. **Synthétique** : jamais présenté comme un résultat |
| `../seed/demo_cases.json` | 20 cas de démonstration | Critère de l'étape 8, test automatique |
| `audit_ecriture_oran.jsonl` | 48 cas écrits comme à Oran : français fautif ou SMS (20), darija en lettres latines (20), arabe (5), hors sujet (3) | **Synthétique**, rédigé le 18/11/2026. A servi à écrire le lexique de darija (`backend/app/services/diagnosis/darija.py`) : mesure de réglage, pas un résultat |
| `audit_ecriture_oran_controle.jsonl` | 20 cas du même genre, écrits **avant** le lexique et jamais utilisés pour l'écrire | **Synthétique**. Contrôle : dit si le gain tient sur des phrases nouvelles. Même auteur que le lexique : biais possible, seul le jeu d'Oran tranchera |

## Constituer le jeu de test d'Oran (section 5, couche 3)

1. Remplir `modele_annotation_oran.csv` avec les mécaniciens partenaires : un cas par ligne, **le symptôme
   dans les mots du client** (pas reformulé), le véhicule, les codes OBD lus, la cause trouvée et la ou les
   pièces changées. Viser 200 cas, sur plusieurs mécaniciens et plusieurs semaines.
2. Contrôler puis convertir : `python ml/oran_csv_to_jsonl.py fiches.csv --check` liste les lignes refusées (pièce inconnue, symptôme vide, doublon) et les avertissements à relire (pièce écrite de façon approchée, véhicule absent du référentiel) ; sans `--check`, le script écrit `oran_test.jsonl` et affiche son empreinte.
   Protocole complet des essais : `docs/essais-oran.md`.
3. **Le figer avant tout entraînement** : le commiter, ne plus le modifier, noter son empreinte dans le mémoire.

Format JSONL (une ligne par cas) :

```json
{"id": "oran001", "text": "...", "variant": ["Dacia", "Logan", "1.5 dCi", 2015], "dtc": [], "expect": ["plaquettes-avant"], "mechanic": "M1", "date": "2027-02-10"}
```

`expect` liste les sous-familles de `data/seed/part_categories.json` acceptées comme bonne réponse ;
`expect_status: "unknown"` marque une entrée hors sujet, à laquelle l'outil doit répondre « je ne sais pas ».
