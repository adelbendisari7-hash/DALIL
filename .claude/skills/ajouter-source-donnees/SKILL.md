---
name: ajouter-source-donnees
description: Ajouter une nouvelle source de données au pipeline DALIL (data/pipeline) avec sa licence vérifiée, sa fiche, son module de collecte, sa correspondance avec la taxonomie des pièces et ses tests. À utiliser dès qu'on parle d'intégrer, collecter, télécharger ou importer un jeu de données, un corpus, une API, un forum, des rappels, des plaintes, des données de contrôle technique ou des cas de mécaniciens dans DALIL, même si le mot « source » n'est pas prononcé (par exemple « on pourrait prendre les données de l'ADEME », « ajoute les rappels du KBA », « importe les cas des mécaniciens partenaires »).
---

# Ajouter une source de données à DALIL

Le cahier des charges (section 8) pose une règle simple : **aucune donnée sans licence connue n'entre
dans la base**. Le pipeline l'applique mécaniquement : le chargement refuse un enregistrement dont la
licence diffère du registre, et les tests échouent si une source n'a pas de fiche. Ce skill suit l'ordre
qui évite de coder pour rien : on vérifie d'abord qu'on a le droit et que la source apporte quelque chose.

## 1. Vérifier avant d'écrire du code

1. **La licence, lue à la source** : métadonnées du portail (data.gouv, Mendeley, CKAN…), page « conditions
   d'utilisation », en-tête des fichiers. Noter le nom exact et l'URL de la licence. Pas de licence claire,
   ou une licence qui interdit la réutilisation (forums, Reddit, catalogues commerciaux comme TecDoc) :
   s'arrêter et le dire à l'utilisateur ; proposer de demander un accord écrit.
2. **L'accès réel** : appeler l'API ou lire l'en-tête des fichiers (`curl -sI`, lecture des 2 premiers Ko,
   lecture à distance de l'index d'un zip) pour connaître le format, les champs et le volume. Ne jamais
   supposer une URL : les archives changent de chemin (l'export Stack Exchange est dans un sous-dossier).
3. **Ce que la source apporte vraiment** : regarder un échantillon. Données générées par gabarit, marques
   anonymisées, hors parc algérien, hors périmètre de la taxonomie ? Le dire franchement dans la fiche et
   marquer `synthetic=True` si les textes sont générés (exemple : `cvffad`). Une source décevante se
   documente quand même : c'est un résultat pour le mémoire.

## 2. Déclarer la source

- `data/pipeline/sources/__init__.py` : ajouter un `SourceSpec` (identifiant court en minuscules, licence
  **exactement** telle qu'elle sera écrite dans chaque enregistrement, URL de licence, attribution, langue).
- `data/sources/<id>.md` : la fiche, sur le modèle des fiches existantes (producteur, accès, licence avec
  URL, attribution, langue, date de vérification, contenu, usage dans DALIL, étiquetage, limites, commande).
  La fiche doit citer la licence mot pour mot : le test le vérifie.
- `data/SOURCES.md` : une ligne avec l'identifiant entre accents graves et un lien vers la fiche.

## 3. Écrire le module de collecte

Fichier `data/pipeline/sources/<module>.py`, fonction `collect(ctx: Context) -> Iterator[Record]`, puis
l'enregistrer dans `collectors()` de `data/pipeline/run.py`. Principes, tous déjà en place dans les modules
existants (à imiter plutôt qu'à réinventer) :

- **Rejouable** : téléchargements via `download()` (cache dans `data/raw/`), réponses d'API gardées en JSON,
  agrégats lourds mis en cache ; `ctx.refresh` force le retéléchargement, `ctx.limit` sert aux essais.
- **Gros fichiers** : lire en flux plutôt que stocker (`ZipMemberStream`, avec reprise après coupure ;
  `pandas.read_csv(..., chunksize=...)`), filtrer tôt, garder des tableaux `numpy` compacts (exemple : `mot.py`).
- **Un `Record` par élément**, `id` stable préfixé par la source, texte d'origine jamais modifié dans `text`,
  `url` et `attribution` pour chaque élément quand la licence l'exige (CC BY, CC BY-SA).
- **`kind`** juste : `complaint` et `qa` décrivent des symptômes et alimentent l'entraînement ; `recall`
  et `stat` vont seulement dans la base de connaissances.

## 4. Relier à la taxonomie

Utiliser `data/pipeline/taxonomy_map.py` : `categories_en`, `categories_fr`, `family_fr`, `reconcile`,
`fault_for`. Si la source a son propre champ de composant, l'exploiter comme `nhtsa_family` pour que
`reconcile` ne garde que les pièces cohérentes avec lui (`label_quality = keyword+component`).
N'attribuer une panne type (`fault`) que si l'étiquette est sûre ; sinon laisser `None` et garder la famille.
Pour une source en langue rare ou au vocabulaire fermé (35 types de pannes chinois), une table faite à la
main (`label_quality = manual`) vaut mieux que des règles.

**Toujours regarder un échantillon aléatoire d'une dizaine d'étiquettes** avant de valider : c'est ainsi
qu'on a trouvé les voyants pris pour des ampoules et les questions de procédure prises pour des pannes.
Corriger les règles plutôt que filtrer à la main.

## 5. Tester, charger, mesurer

1. Ajouter des cas à `data/pipeline/tests/test_pipeline.py` : quelques textes réels de la source avec la
   pièce attendue, et le cas « hors taxonomie » qui ne doit rien produire. Le test des fiches couvre la
   nouvelle source automatiquement.
2. `cd backend && .venv/Scripts/python -m pytest -q ../data/pipeline/tests`
3. `python data/pipeline/run.py all --sources <id>` puis vérifier `data/processed/report.md`.
4. **Non-régression du diagnostic** : rejouer les 20 cas de démonstration sur la base chargée
   (`data/seed/demo_cases.json`) ; les passages en français entrent dans la recherche par mots-clés et
   peuvent déplacer les résultats ou le seuil « je ne sais pas ».
5. Si la source n'est pas en français : traduction sur Kaggle (`ml/kaggle/README.md`).

## Ce qu'il ne faut pas faire

- Collecter une source avant d'avoir lu sa licence, ou « pour voir ».
- Mettre des exemples synthétiques ou à étiquettes faibles dans le jeu de test d'Oran : il ne contient que
  des cas réels annotés par des mécaniciens.
- Écrire une référence de pièce, un prix ou un magasin tirés d'une source non vérifiée dans les tables métier.
