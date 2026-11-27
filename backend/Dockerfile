FROM python:3.12-slim
WORKDIR /app/backend
COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Recherche hybride (vecteurs + reclassement) : torch CPU et transformers. WITH_ML=0 pour une image légère (mots-clés).
ARG WITH_ML=1
RUN if [ "$WITH_ML" = "1" ]; then \
      pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-ml.txt; \
    fi
COPY . .
EXPOSE 8000
# Migrations, référentiels (rejouables ; DALIL_SEED_ARGS=--no-demo en production : aucun magasin fictif), puis l'API
ENV DALIL_SEED_ARGS=""
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed $DALIL_SEED_ARGS && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
