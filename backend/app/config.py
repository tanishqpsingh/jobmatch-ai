import os
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Application settings
    APP_NAME: str = "JobMatch AI API"
    ENVIRONMENT: str = "development"    # "development" | "production"
    DEBUG: bool = False                 # Never True in production
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS — comma-separated origins in env, e.g.:
    #   CORS_ORIGINS=http://localhost:3000,https://your-frontend.railway.app
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database — Railway injects DATABASE_URL automatically for linked Postgres service.
    # Local dev falls back to SQLite if this points at PostgreSQL without a running server.
    POSTGRES_USER: str = "jobmatch_user"
    POSTGRES_PASSWORD: str = "jobmatch_password"
    POSTGRES_DB: str = "jobmatch_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://jobmatch_user:jobmatch_password@localhost:5432/jobmatch_db"

    # File Upload Settings
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB limit
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",  # Fallback for some browsers/clients
    ]

    # Google Gemini — MUST be set via environment variable; no default
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # JWT / Auth — MUST be overridden via environment variable in production
    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    JWT_SECRET: str = "change-me-in-production-use-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"

    # Cookie Security Settings
    # COOKIE_SAMESITE must be "none" for cross-origin deployments (e.g. frontend and backend
    # on different Railway subdomains). SameSite=none requires Secure=true (enforced by
    # is_cookie_secure in production). For purely same-site deployments, use "lax".
    # Override via environment variable: COOKIE_SAMESITE=none
    COOKIE_SAMESITE: str = "none"
    COOKIE_SECURE: Optional[bool] = None
    COOKIE_DOMAIN: Optional[str] = None

    @property
    def is_cookie_secure(self) -> bool:
        """Enforce secure HTTPS-only cookies in production unless explicitly overridden."""
        if self.COOKIE_SECURE is not None:
            return self.COOKIE_SECURE
        return self.ENVIRONMENT == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
