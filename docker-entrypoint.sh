#!/bin/sh

echo "Running Alembic migrations..."
alembic upgrade head

echo "Migrations done. Starting FastAPI application..."
exec fastapi run src/main.py --port 8000
