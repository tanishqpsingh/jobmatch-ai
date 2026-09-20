import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text
from alembic import context

# Ensure project root is on path so backend imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.app.db.database import Base  # noqa: E402
import backend.app.db.models  # noqa: E402, F401 — registers all ORM models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_db_url() -> str:
    """
    Resolve the database URL for migrations.

    Priority:
      1. DATABASE_URL environment variable (Railway / CI / production)
      2. backend.app.config settings
      3. alembic.ini sqlalchemy.url fallback
    """
    # 1. Railway / explicit env override
    raw = os.environ.get("DATABASE_URL", "")

    if not raw:
        # 2. App config
        try:
            from backend.app.config import get_settings
            raw = get_settings().DATABASE_URL
        except Exception:
            pass

    if not raw:
        # 3. alembic.ini fallback
        return config.get_main_option("sqlalchemy.url", "")

    # Normalise Railway's legacy postgres:// scheme
    if raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql://", 1)

    # Strip asyncpg driver — use psycopg2 for sync migrations
    if raw.startswith("postgresql+asyncpg://"):
        raw = raw.replace("postgresql+asyncpg://", "postgresql://", 1)

    # Local dev fallback: if URL still points at Postgres but we're in dev, use SQLite
    environment = os.environ.get("ENVIRONMENT", "development")
    if environment != "production" and raw.startswith("postgresql"):
        root = os.path.join(os.path.dirname(__file__), "..", "..")
        sqlite_path = os.path.abspath(os.path.join(root, "jobmatch.db"))
        return f"sqlite:///{sqlite_path}"

    return raw


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection needed)."""
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # SQLite-compatible batch mode
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with a live DB connection."""
    url = get_db_url()

    # Override the URL from alembic.ini with the resolved value
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # SQLite-compatible batch mode
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
