import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.db.database import init_db
from backend.app.routers import resumes, jobs, matching, applications, career, auth

# ---------------------------------------------------------------------------
# Logging — safe startup info, no secrets
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

logger.info("Starting %s (environment=%s)", settings.APP_NAME, settings.ENVIRONMENT)

# ---------------------------------------------------------------------------
# Database initialisation
# Only runs create_all() in non-production environments (local dev convenience).
# Production schema is managed exclusively by: alembic upgrade head
# ---------------------------------------------------------------------------
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    description="API for JobMatch AI — Resume and Job Description Matcher",
    version="0.1.0",
    # Disable interactive docs in production to reduce attack surface
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# ---------------------------------------------------------------------------
# CORS — configured from environment, never allows arbitrary origins
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# API Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(matching.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(career.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Lightweight liveness probe — used by Railway to detect if the service is alive.
    Returns 200 OK immediately. Does not query the database.
    """
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness probe — verifies the database is reachable before accepting traffic.
    Safe to call from Railway health checks.
    Does NOT expose credentials or internal configuration.
    """
    from sqlalchemy import text
    from backend.app.db.database import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "reachable"}
    except Exception:
        from fastapi import Response
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "unreachable"},
        )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing service metadata."""
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.ENVIRONMENT != "production" else "disabled",
    }
