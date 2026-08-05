"""Application settings loaded from .env file."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://chunker:chunker_pass@localhost:5432/chunking_playground"
    cors_origins: str = "http://localhost:5173"
    max_upload_size_mb: int = 10

    # Qdrant Cloud Configuration (admin / .env defaults)
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "multimodal_rag_playground"

    # OpenRouter LLM API Configuration (admin / .env defaults)
    openrouter_api_key: str = ""

    # ── Auth & Security ──────────────────────────────────────────────────────
    # JWT signing secret — set a strong random value in .env
    jwt_secret: str = "changeme-please-use-a-strong-secret"

    # Fernet encryption key for user API keys — generate once with:
    #   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    encryption_key: str = ""

    # ── Google OAuth (optional — email/password works without these) ─────────
    google_client_id: str = ""
    google_client_secret: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def google_oauth_enabled(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret)


settings = Settings()
