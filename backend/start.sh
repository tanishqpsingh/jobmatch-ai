#!/bin/sh
set -e

echo "[Startup] Running database migrations (alembic upgrade head)..."
alembic upgrade head

echo "[Startup] Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers
