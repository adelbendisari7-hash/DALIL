# Étape 11 : essais à Oran (protocole et compte rendu)

Critère de fin de l'étape 11 (section 11 du cahier) : un retour « pièce trouvée » modifie le score (vérifié par
`backend/tests/test_retours.py`) et un **compte rendu des essais**. Ce document dit comment mener les essais pour
que leurs résultats soient utilisables dans le mémoire, puis donne le modèle du compte rendu (section 6).

## 1. Ce que les essais doivent mesurer

| Mesure | Exigence du cahier | Comment la relever |
| --- | --- | --- |
| Diagnostic juste (top-1 et top-3 sur la pièce) | Chiffre principal du mémoire (section 6.2) | Jeu de test d'Oran : fiches des mécaniciens (section 3.A) |
| Taux de « je ne sais pas » à tort | Le plus bas possible ; « je ne sais pas » reste l'erreur sûre | Même jeu |
| Choix du véhicule | Moins de 20 s (F1) | Chronomètre, automobilistes (3.C) |
| Diagnostic | Moins de 10 s | Chronomètre, ou colonne « ms » de `ml/evaluate.py` |
| Inscription d'un magasin | Moins de 3 min | Chronomètre, magasins (3.B) |
| Ajout d'un produit | Moins de 30 s | Chronomètre, magasins (3.B) |
| Pièce trouvée après un contact | Taux à suivre | Page d'indicateurs (admin > Indicateurs) |
| Utilité perçue | Avis des utilisateurs | Questionnaire (section 5) |

## 2. Avant les essais

- **Participants.**
  - 3 à 5 mécaniciens partenaires : ils fournissent les cas réels du jeu de test (objectif : 200 cas sur plusieurs semaines).
  - 5 à 10 magasins de pièces, dans plusieurs communes.
  - 10 à 20 automobilistes.
- **Consentement et données (loi 18-07, section 10).**
  - Expliquer le but de l'essai et demander l'accord oral.
  - Ne noter **aucun nom** dans les fiches, seulement des codes : M1, M2… pour les mécaniciens, G1… pour les magasins, A1… pour les automobilistes. La correspondance reste sur papier, chez l'équipe.
  - Les numéros de téléphone utilisés pour se connecter restent dans la base, et peuvent être supprimés à la demande (bouton de suppression du compte).
- **Matériel.**
  - Le PC avec `DEMARRER-DALIL.bat`.
  - Un téléphone par testeur sur le même Wi-Fi : le lanceur affiche l'adresse.
  - Pour la dictée et l'installation de l'application, faire le réglage de Chrome décrit dans `docs/test-telephone.md`.
- **Données.** Les magasins de démonstration, marqués [DÉMO], restent visibles. Les retirer avant un essai avec de vrais magasins : `cd backend && .venv/Scripts/python -m app.seed --purge-demo`.
- **Version.** Noter le commit utilisé (`git log --oneline -1`) : les résultats doivent pouvoir être reliés à une version précise.

## 3. Déroulé

### A. Mécaniciens : constituer le jeu de test (le plus important)

1. Remplir `data/test/modele_annotation_oran.csv` (une copie par mécanicien), **un cas réel par ligne, après réparation**. Pour chaque cas, noter :
   - le symptôme **dans les mots du client**, tel quel, sans reformuler ;
   - le véhicule (marque, modèle, motorisation, année) ;
   - les codes OBD lus ;
   - la cause trouvée ;
   - la ou les pièces changées.
2. Ne pas montrer DALIL aux mécaniciens pendant qu'ils remplissent les fiches : le jeu doit rester indépendant de l'outil.
3. Convertir et contrôler :
   `backend/.venv/Scripts/python ml/oran_csv_to_jsonl.py fiches.csv --check`.
   - Corriger les lignes refusées.
   - Relire les avertissements : pièces écrites de façon approchée, véhicules inconnus du référentiel.
4. Produire `data/test/oran_test.jsonl` (même commande sans `--check`), **le commiter tel quel et noter son empreinte SHA-256** (affichée par le script). Ensuite, ne plus le modifier, ne jamais entraîner ni régler un seuil avec lui.
5. Mesurer :
   `backend/.venv/Scripts/python ml/evaluate.py --model A=ml/artifacts/baseline_tfidf_lr.joblib --modes classifier,retrieval,full --test data/test/oran_test.jsonl --tag oran`.
   - Recommencer avec `DALIL_RETRIEVAL_MODE=hybrid` devant la commande, pour la recherche hybride.
   - Les résultats s'écrivent dans `ml/results/`.

### B. Magasins (environ 15 min chacun, sur leur propre téléphone)

1. **Inscription chronométrée**, de l'ouverture de « Espace magasin » jusqu'au message « En attente de validation ». Ne pas aider ; noter les blocages.
2. **Ajout d'un produit au formulaire, chronométré.**
3. **Import du catalogue.** Télécharger le modèle Excel, y mettre 20 produits réels (ou les saisir avec le gérant), puis importer. Noter les lignes en erreur et leur cause.
4. L'équipe valide la fiche (admin > À valider), puis le gérant vérifie que sa fiche publique montre ses produits.
5. Questionnaire (section 5).

### C. Automobilistes (environ 10 min chacun)

1. Choisir son véhicule (chronométré).
2. Décrire une panne réelle ou récente avec ses mots, au clavier ou à la voix. Noter si la cause proposée correspond à ce que le mécanicien a trouvé, quand c'est connu.
3. Aller jusqu'aux magasins, contacter un magasin réel (pas [DÉMO]), puis répondre à « Pièce trouvée ? » quand la réponse est connue.
4. Questionnaire (section 5).

## 4. Fiches de relevé

**Magasins**

| Code | Commune | Téléphone (modèle) | Inscription (min:s) | 1 produit (s) | Import : lignes OK / erreurs | Blocages observés |
| --- | --- | --- | --- | --- | --- | --- |
| G1 | | | | | | |

**Automobilistes**

| Code | Véhicule | Choix du véhicule (s) | Diagnostic (s) | Cause proposée | Cause réelle (si connue) | Magasin contacté | Pièce trouvée ? | Remarques |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | | | | | | | | |

## 5. Questionnaire (1 à 5, de « pas du tout » à « tout à fait »)

1. J'ai compris ce que l'application me proposait.
2. Le résultat m'a paru utile.
3. J'utiliserais l'application la prochaine fois que j'ai une panne (pour un magasin : pour recevoir des clients).
4. L'application était rapide.
5. Une question ouverte : qu'est-ce qui vous a gêné ou manqué ?

## 6. Modèle de compte rendu

```markdown
# Compte rendu des essais DALIL à Oran

Dates : … ; lieux : … ; version : commit … ; équipe : …

## Participants
- Mécaniciens : N (cas fournis : N) ; magasins : N (communes : …) ; automobilistes : N.

## Résultats
| Mesure | Exigence | Résultat | Atteint ? |
| --- | --- | --- | --- |
| Top-1 / top-3 sur le jeu d'Oran (N cas, empreinte …) | — | … % / … % | — |
| « Je ne sais pas » à tort | bas | … % | |
| Choix du véhicule (médiane) | < 20 s | … s | |
| Diagnostic (médiane / max) | < 10 s | … s / … s | |
| Inscription d'un magasin (médiane) | < 3 min | … | |
| Ajout d'un produit (médiane) | < 30 s | … s | |
| Pièce trouvée après contact | — | … % (N retours) | |
| Questionnaire (moyenne par question) | — | … | |

## Ce qui a marché

## Problèmes observés (par gravité, avec le nombre de participants touchés)

## Décisions et corrections qui en découlent

## Limites des essais (taille de l'échantillon, biais de recrutement, …)
```

Mettre le compte rendu dans `docs/compte-rendu-essais.md`, puis mettre à jour `docs/SUIVI.md` (étape 11).
