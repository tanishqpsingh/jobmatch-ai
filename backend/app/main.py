from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import get_settings
from backend.app.db.database import init_db
from backend.app.routers import resumes, jobs, matching, applications, career, auth

settings = get_settings()

# Initialize DB tables
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    description="API for JobMatch AI - Resume and Job Description Matcher",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(matching.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(career.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend service status."""
    return {"status": "ok"}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing service metadata."""
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "docs_url": "/docs",
    }
