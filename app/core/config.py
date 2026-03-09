from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration — every setting the app needs lives here.
    Values are read from environment variables (or a .env file).
    """

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "Fraud Alert API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fraud_db"

    # ── JWT Auth (Sprint 2) ──────────────────────────────
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # ── Azure Data Explorer (Sprint 3) ───────────────────
    ADX_CLUSTER_URL: str = ""
    ADX_DATABASE: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Singleton — import this everywhere: `from app.core.config import settings`
settings = Settings()
