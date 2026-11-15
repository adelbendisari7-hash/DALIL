# Fiche source : contrôle technique britannique, données MOT anonymisées (`mot_uk`)

| | |
| --- | --- |
| Producteur | Driver and Vehicle Standards Agency (DVSA), Royaume-Uni |
| Accès | https://open.data.dvsa.gov.uk/mot-anonymised/index.html : `dft_test_result_<année>.zip` (1,2 Go, compression Deflate64), `dft_test_item_<année>.zip` (460 Mo), tables `dft_item_detail_extract.csv` et `dft_item_group_extract.csv` |
| Licence | Open Government Licence v3.0, https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ |
| Attribution | Contains public sector information licensed under the Open Government Licence v3.0 (DVSA) |
| Langue | Anglais (données codées, sans texte libre) |
| Vérifiée le | 14/11/2026 |

**Contenu.** Chaque contrôle (marque, modèle, kilométrage, résultat) et chaque motif de défaut (`rfr_id`).

**Traitement.** Lecture en flux, sans stocker les archives ; véhicules particuliers (classe 4), contrôles normaux ; 19 modèles du parc algérien vendus au Royaume-Uni (Sandero, Duster, Logan, Clio, Kangoo, i10, Picanto, Rio, 206, 208, 500, Tipo, Doblo, Golf, Polo, Octavia, Hilux, Corsa, MG5). Un contrôle compte une fois par famille de pièces. Trois tranches de kilométrage : moins de 100 000 km, 100 000 à 160 000 km, plus de 160 000 km.

**Sorties.** `data/processed/priors/mot_<année>.csv` : taux d'échec par modèle, tranche et famille, a priori par véhicule pour la chaîne de diagnostic. Une fiche en français par modèle dans la base de connaissances. Agrégat en cache : `data/raw/mot/agg_<année>.csv`.

**Limites.** Dit quelle pièce lâche, pas comment le client décrit la panne. Les modèles non vendus au Royaume-Uni (Symbol, 301, Accent récente) n'y sont pas : utiliser ceux de mécanique proche (Logan pour la Symbol). Une partie des défauts reste au niveau de la famille (« Freinage » pour une efficacité de freinage insuffisante).

**Commande.** `python data/pipeline/run.py all --sources mot_uk [--mot-year 2022] [--refresh]` (environ 4 minutes, 1,6 Go lus en flux).
