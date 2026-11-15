# Jeux de test

| Fichier | Contenu | Usage |
| --- | --- | --- |
| `oran_test.jsonl` | **Jeu de test figé** : 200 cas réels d'Oran annotés par des mécaniciens partenaires (à constituer) | Seule mesure valable pour le mémoire. Jamais utilisé pour entraîner ni pour régler un seuil |
| `dev_fr_synthetique.jsonl` | 55 cas rédigés par l'équipe (50 pannes, 5 hors sujet), formulations absentes des exemples d'entraînement | Réglage des seuils et comparaison rapide des variantes pendant le développement. **Synthétique** : jamais présenté comme un résultat |
| `../seed/demo_cases.json` | 20 cas de démonstration | Critère de l'étape 8, test automatique |

## Constituer le jeu de test d'Oran (section 5, couche 3)

1. Remplir `modele_annotation_oran.csv` avec les mécaniciens partenaires : un cas par ligne, **le symptôme
   dans les mots du client** (pas reformulé), le véhicule, les codes OBD lus, la cause trouvée et la ou les
   pièces changées. Viser 200 cas, sur plusieurs mécaniciens et plusieurs semaines.
2. Convertir : `python ml/oran_csv_to_jsonl.py data/test/modele_annotation_oran.csv` produit `oran_test.jsonl`.
3. **Le figer avant tout entraînement** : le commiter, ne plus le modifier, noter son empreinte dans le mémoire.

Format JSONL (une ligne par cas) :

```json
{"id": "oran001", "text": "...", "variant": ["Dacia", "Logan", "1.5 dCi", 2015], "dtc": [], "expect": ["plaquettes-avant"], "mechanic": "M1", "date": "2027-02-10"}
```

`expect` liste les sous-familles de `data/seed/part_categories.json` acceptées comme bonne réponse ;
`expect_status: "unknown"` marque une entrée hors sujet, à laquelle l'outil doit répondre « je ne sais pas ».
