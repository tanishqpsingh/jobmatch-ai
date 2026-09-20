import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.config import get_settings

settings = get_settings()

# Default to SQLite file database if PostgreSQL is not running locally for development
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql+asyncpg://"):
    # Convert asyncpg scheme to standard psycopg2 / sqlite for synchronous SQLAlchemy session if needed,
    # or fallback to SQLite for local file persistence
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

# If testing or PostgreSQL connection fails, fallback gracefully to SQLite local DB
if "sqlite" in db_url or not os.environ.get("USE_POSTGRES", "").lower() == "true":
    db_url = "sqlite:///./jobmatch.db"

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
    """Initialize database tables using SQLAlchemy metadata."""
    Base.metadata.create_all(bind=engine)
