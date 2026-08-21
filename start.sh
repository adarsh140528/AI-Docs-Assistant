#!/usr/bin/env bash
set -e

# Default PORT to 8000 if not provided by host environment
PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

echo "=================================================="
echo " Starting Adorush AI Assistant API Server"
echo " Host: $HOST | Port: $PORT"
echo "=================================================="

# Ensure directories exist
mkdir -p uploads indexes static

# Launch FastAPI via Uvicorn with single worker to conserve memory on free tiers
exec uvicorn server:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers 1 \
    --timeout-keep-alive 75 \
    --access-log
