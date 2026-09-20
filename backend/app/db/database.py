import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# Resolve database URL
# ---------------------------------------------------------------------------
# Priority:
#   1. DATABASE_URL env var (Railway injects this for PostgreSQL service)
#   2. Settings.DATABASE_URL from .env / config
#   3. SQLite fallback ONLY for local development (never in production)
# ---------------------------------------------------------------------------
_raw_url: str = os.environ.get("DATABASE_URL", settings.DATABASE_URL)

# Railway sometimes provides postgres:// (older scheme) — normalise to postgresql://
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql://", 1)

# Strip asyncpg driver suffix — we use synchronous SQLAlchemy sessions
if _raw_url.startswith("postgresql+asyncpg://"):
    _raw_url = _raw_url.replace("postgresql+asyncpg://", "postgresql://", 1)

# Determine effective URL:
#   - In production (ENVIRONMENT != "development") always use the configured URL.
#   - In development, fall back to SQLite if URL still points at PostgreSQL
#     (i.e. local dev without a running Postgres).
ENVIRONMENT = os.environ.get("ENVIRONMENT", settings.ENVIRONMENT)

if ENVIRONMENT == "production":
    db_url = _raw_url
    if "sqlite" in db_url:
        raise RuntimeError(
            "DATABASE_URL resolves to SQLite in a production environment. "
            "Set DATABASE_URL to a valid PostgreSQL URL on Railway."
        )
    logger.info("Database: PostgreSQL (production)")
else:
    # Local development — fall back to SQLite if no real Postgres URL
    if _raw_url.startswith("postgresql"):
        db_url = "sqlite:///./jobmatch.db"
        logger.info("Database: SQLite fallback (local dev — no Postgres configured)")
    else:
        db_url = _raw_url
        logger.info("Database: %s (local dev)", db_url.split("://")[0])

connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency generator providing a database session for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.

    IMPORTANT: In production, schema management is handled exclusively by
    Alembic migrations (alembic upgrade head). This function uses create_all()
    only as a development convenience for SQLite local environments.
    It is a no-op when the database already has up-to-date tables.
    """
    if ENVIRONMENT != "production":
        # Local dev convenience only — does not replace Alembic in production
        Base.metadata.create_all(bind=engine)
