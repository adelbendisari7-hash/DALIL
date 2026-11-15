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

    # Modèle de langage derrière une interface unique : none | anthropic | openai_compat
    llm_provider: str = "none"
    llm_model: str = "claude-sonnet-5-5"
    llm_base_url: str = ""  # pour openai_compat (llama.cpp, Ollama, vLLM servant le modèle affiné)
    llm_api_key: str = ""
    llm_monthly_call_cap: int = 2000
    llm_timeout: float = 60.0  # secondes, pour openai_compat (modèle servi sur le portable)

    # Diagnostic
    confidence_threshold: float = 0.15  # sous ce seuil : « je ne sais pas »
    clarify_margin: float = 0.12  # écart top1/top2 sous lequel on pose des questions
    classifier_path: str = str(REPO_ROOT / "ml" / "artifacts" / "baseline_tfidf_lr.joblib")
    model_version: str = "baseline-tfidf-lr-v0"

    diagnosis_rate_per_minute: int = 20
    otp_rate_per_minute: int = 5
    cors_origins: str = "http://localhost:3000"

    data_dir: str = str(REPO_ROOT / "data")


@lru_cache
def get_settings() -> Settings:
    return Settings()
