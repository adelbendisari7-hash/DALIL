# Étape 8 : chaîne de diagnostic, plan proposé (à valider avant de coder)

Le cahier des charges (section 11) demande un plan validé avant de coder les étapes 5 à 8.

**Critère de fin (section 11)** : 20 cas de démonstration passent ; une entrée hors sujet reçoit « je ne sais pas » ; aucune référence n'est générée.

## 1. Ce qui existe déjà (étapes 3 à 7)

| Exigence | État | Où |
| --- | --- | --- |
| `POST /diagnosis`, `POST /diagnosis/{id}/answers`, `GET /diagnosis/{id}` | Fait, limité en débit | `backend/app/routers/public.py` |
| Chaîne normalisation, recherche, classifieur, modèle de langage, sûreté | Fait | `services/diagnosis/pipeline.py` |
| Sortie JSON du modèle de langage validée (slugs candidats seulement, au plus 3) | Fait | `llm.py`, `rerank_with_llm` |
| Seuil de confiance, puis « je ne sais pas » ; garde-fou hors sujet | Fait (seuil 0,15 réglé sur le jeu dev) | `pipeline.py` |
| « Ne roulez pas » en premier (freinage, direction, carburant, surchauffe) ; avertissement « aide, pas diagnostic certifié » | Fait | `pipeline.py` |
| Questions de précision (banque de questions, une à trois) | Fait | `question_bank`, `_pick_questions` |
| Trois niveaux de référence, lus en table, jamais générés | Fait, données « FICTIF- » | `_references`, `part_references` |
| Traçabilité (version du modèle, passages utilisés, réponse) | Fait | `diagnosis_sessions` |
| Plafond d'appels au modèle de langage | Fait | `llm.py`, `_CallBudget` |
| 20 cas de démonstration, hors sujet, références jamais générées | Tests en place | `tests/test_demo_cases.py`, `tests/test_api.py` |

Le critère de fin est donc **déjà vérifié avec le modèle A** (TF-IDF, sans modèle de langage). L'étape 8 consiste surtout à brancher la variante D et à combler les manques ci-dessous.

## 2. Ce qui manque, par ordre de priorité

1. **Brancher le modèle affiné (variante D) et le mesurer.** Le fichier GGUF est servi par `llama-server` et appelé par `DALIL_LLM_PROVIDER=openai_compat`. On lance ensuite `ml/evaluate.py --modes retrieval,full` et on compare D à A sur le jeu dev et sur les 20 cas.
   - *Risque à mesurer d'abord* : temps de réponse sur le processeur du portable. Le cahier exige un diagnostic en moins de 10 s, et le message envoyé au modèle fait environ 1 500 jetons.
   - *Si c'est trop lent* : réduire les passages envoyés (de 5 à 2 ou 3, plus courts), ou garder A seul pour la démonstration et ne présenter D que dans le mémoire.
2. **Repli automatique.** Si le serveur du modèle de langage ne répond pas dans le délai, la chaîne rend le résultat du classifieur au lieu d'échouer. Le délai sera configurable (`DALIL_LLM_TIMEOUT`). Un test simulera une panne du serveur.
3. **Cache des réponses** pour les codes OBD et les questions fréquentes (section 10, « Coût ») : même texte normalisé, même véhicule, même version de modèle, donc même réponse. Cache en table, avec durée de vie.
4. **Indicateur de progression** côté application (section 10 : diagnostic en moins de 10 s *avec indicateur de progression*). Côté API, renvoyer les étapes franchies ; l'affichage relève de l'étape 9.
5. **Recherche hybride** (vecteurs multilingues dans pgvector et reclassement). Elle est prévue en section 6.1 mais pas indispensable au critère de fin. *Proposition* : la reporter après l'étape 9 et la présenter dans le mémoire comme une variante mesurée, pas comme un prérequis.

## 3. Hors périmètre de l'étape 8

- Darija et arabe : V2 (section 10 : première version en français). Le texte en lettres arabes est déjà détecté et reçoit une réponse « je ne sais pas » polie.
- Saisie vocale : étape 9 (F13).

## 4. Tests ajoutés

- Repli quand le modèle de langage est lent ou absent.
- Cache : deux appels identiques donnent une seule inférence.
- Une réponse du modèle de langage qui cite un slug hors candidats ou une « référence » est ignorée (test existant, à étendre avec un faux fournisseur).
- Les 20 cas de démonstration rejoués en mode `full` avec un faux fournisseur déterministe.

## 5. Décisions demandées à l'équipe

1. Accepter le report de la recherche hybride (point 5) ?
2. Si D dépasse 10 s sur le portable : garder A en démonstration et D dans le mémoire, ou réduire le contexte de D ?
