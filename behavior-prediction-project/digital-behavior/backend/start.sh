#!/bin/bash

# Startup script for Render deployment
set -e

echo "Checking environment variables..."
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set!"
    exit 1
fi

echo "DATABASE_URL is set (length: ${#DATABASE_URL} chars)"
echo "DATABASE_URL starts with: ${DATABASE_URL:0:15}..."

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
