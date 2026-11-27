"""Configuration centrale, lue depuis les variables d'environnement (fichier .env accepté)."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DALIL_", extra="ignore")

    # Base : PostgreSQL en Docker ; SQLite en repli pour le portable et les tests.
    database_url: str = f"sqlite:///{(REPO_ROOT / 'backend' / 'dalil.db').as_posix()}"

    jwt_secret: str = "dev-only-secret-change-me-in-production-0123456789"
    jwt_ttl_hours: int = 24 * 30
    otp_ttl_minutes: int = 10
    # Numéros qui deviennent administrateurs à leur première connexion (séparés par des virgules).
    admin_phones: str = ""
    # Fournisseur SMS : "console" écrit le code dans le journal (développement).
    sms_provider: str = "console"
    # Code fixe pour les tests de bout en bout (Playwright). Ignoré sauf avec sms_provider = "console".
    otp_test_code: str = ""

    # Modèle de langage derrière une interface unique : none | anthropic | openai_compat
    llm_provider: str = "none"
    llm_model: str = "claude-sonnet-5-5"
    llm_base_url: str = ""  # pour openai_compat (llama.cpp, Ollama, vLLM servant le modèle affiné)
    llm_api_key: str = ""
    llm_monthly_call_cap: int = 2000
    # Au-delà de ce délai (secondes) la chaîne rend le classement du classifieur. 120 s : le modèle affiné sert
    # un diagnostic en 20 à 45 s sur processeur, et la précision passe avant la vitesse (décision du 15/11/2026).
    llm_timeout: float = 120.0
    llm_cache_ttl: int = 7 * 24 * 3600  # durée de vie du cache des réponses du modèle de langage (secondes)

    # Diagnostic
    confidence_threshold: float = 0.15  # sous ce seuil : « je ne sais pas »
    clarify_margin: float = 0.12  # écart top1/top2 sous lequel on pose des questions
    classifier_path: str = str(REPO_ROOT / "ml" / "artifacts" / "baseline_tfidf_lr.joblib")
    model_version: str = "baseline-tfidf-lr-v0"

    # Recherche : "keyword" (TF-IDF, sans modèle à charger) ou "hybrid" (mots-clés + vecteurs Qwen3-Embedding,
    # reclassés par bge-reranker-v2-m3). Les modèles et vecteurs viennent du carnet Kaggle 05_vecteurs
    # (`python ml/load_vectors.py`). Si un fichier manque, la recherche retombe sur « keyword ».
    retrieval_mode: str = "keyword"
    embedding_model_path: str = str(REPO_ROOT / "ml" / "artifacts" / "qwen3-embedding-0.6b")
    reranker_model_path: str = str(REPO_ROOT / "ml" / "artifacts" / "bge-reranker-v2-m3")
    vectors_path: str = str(REPO_ROOT / "ml" / "artifacts" / "vectors")
    # Reclassement sur processeur (mesuré le 17/11/2026 sur le portable, 4 requêtes) : 20 passages x 512 jetons en
    # float32 = 23,5 s par diagnostic ; 10 x 256 en int8 = 2,9 s. Précision vérifiée avec ml/evaluate.py (ml/README.md).
    rerank_pool: int = 10
    rerank_max_len: int = 256
    rerank_int8: bool = True
    # Textes longs (vrais messages de 800 à 900 caractères : jusqu'à 10,5 s, 26/11/2026). La recherche ne lit que le
    # début du texte (le symptôme y est presque toujours) ; le classifieur lit tout. 0 = texte entier.
    retrieval_query_chars: int = 0
    embed_int8: bool = False  # modèle des vecteurs de la requête en int8, comme le reclassement

    diagnosis_rate_per_minute: int = 20
    otp_rate_per_minute: int = 5
    feedback_rate_per_minute: int = 30  # retours et contacts, par adresse IP
    # Charge les modèles de diagnostic au démarrage (en arrière-plan) : le premier diagnostic ne paie pas
    # ~1 min de chargement de la recherche hybride.
    warmup: bool = True
    # Index des mots-clés (TF-IDF sur ~9 600 passages : 60 à 120 s à recalculer sur le portable) gardé sur disque,
    # reconnu par une empreinte du contenu de la base. Vide = pas de cache.
    index_cache_dir: str = str(REPO_ROOT / "data" / "processed" / "index_cache")
    cors_origins: str = "http://localhost:3000"

    data_dir: str = str(REPO_ROOT / "data")


@lru_cache
def get_settings() -> Settings:
    return Settings()
