import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ensure project root is on path so backend imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.app.db.database import Base  # noqa: E402
import backend.app.db.models  # noqa: E402, F401 — registers all ORM models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point alembic at our model metadata for autogenerate support
target_metadata = Base.metadata

# Override sqlalchemy.url from environment / app settings if available
try:
    from backend.app.config import get_settings
    _settings = get_settings()
    db_url = _settings.DATABASE_URL
    # Strip async driver; replace postgresql with sqlite for local dev if psycopg2 unavailable
    if db_url.startswith("postgresql"):
        # Use local SQLite dev file when PostgreSQL is not configured locally
        import os as _os
        _root = _os.path.join(_os.path.dirname(__file__), "..", "..")
        db_url = f"sqlite:///{_os.path.join(_root, 'jobmatch.db')}"
    else:
        db_url = db_url.replace("+asyncpg", "")
    config.set_main_option("sqlalchemy.url", db_url)
except Exception:
    pass  # Fall back to alembic.ini value

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
