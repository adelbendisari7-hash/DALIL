# PostgreSQL 16 + pgvector (image officielle pgvector, Debian récente, dépôt PGDG déjà configuré) + PostGIS (paquet PGDG).
# Avant le 28/11/2026 : postgis/postgis:16-3.4 + postgresql-16-pgvector, dont la construction échouait dans l'intégration
# continue (image sur une Debian ancienne) ; les migrations n'étaient alors plus vérifiées sur PostgreSQL.
FROM pgvector/pgvector:pg16
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-16-postgis-3 postgresql-16-postgis-3-scripts \
 && rm -rf /var/lib/apt/lists/*
