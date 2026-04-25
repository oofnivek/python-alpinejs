#!/usr/bin/env bash
# scripts/render_start.sh
# ─────────────────────────────────────────────────────────────────────────────
# Render injects DATABASE_URL as:  postgresql://user:pass@host/db
# SQLAlchemy async needs:          postgresql+asyncpg://user:pass@host/db
# This script rewrites it, runs Alembic migrations, then starts the server.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

echo "▶  Ensuring data directory exists..."
mkdir -p data

echo "▶  Rewriting DATABASE_URL if MySQL..."
# If DATABASE_URL starts with mysql://, replace it with mysql+aiomysql://
export DATABASE_URL="${DATABASE_URL/mysql:\/\//mysql+aiomysql://}"

echo "▶  Running database migrations..."
alembic upgrade head

echo "▶  Starting server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 2
