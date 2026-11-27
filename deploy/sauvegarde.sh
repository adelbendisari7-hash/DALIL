#!/bin/sh
# Sauvegarde quotidienne de DALIL (base + photos), rejouable. À lancer depuis deploy/ par le planificateur :
#   0 3 * * * cd /srv/dalil/deploy && ./sauvegarde.sh >> sauvegardes/journal.txt 2>&1
# Garde 14 jours ; copier aussi le dossier sauvegardes/ ailleurs (autre machine), sinon une panne du disque emporte tout.
# Restauration : gunzip -c base-AAAAMMJJ.sql.gz | docker compose -f docker-compose.prod.yml exec -T db psql -U dalil dalil
set -eu
cd "$(dirname "$0")"
mkdir -p sauvegardes
jour=$(date +%Y%m%d-%H%M)
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U dalil --no-owner dalil | gzip > "sauvegardes/base-$jour.sql.gz"
docker compose -f docker-compose.prod.yml exec -T api tar -C /app/uploads -czf - . > "sauvegardes/photos-$jour.tar.gz"
find sauvegardes -name "*.gz" -mtime +14 -delete
echo "$(date) : sauvegarde $jour faite"
