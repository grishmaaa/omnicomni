#!/bin/sh
set -e

# Default to 8000 if PORT is not set
PORT="${PORT:-8000}"

echo "Starting app on port $PORT"
exec uvicorn api_server:app --host 0.0.0.0 --port "$PORT"
