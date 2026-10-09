#!/usr/bin/env bash
# CrisisGuard — Enterprise Web Application & API Launcher
# Author: B.SIVASAI (Roll Number: 2023BCS0228)
# Course: CSE412 — Big Data & Large-Scale Computing
#
# Launches the FastAPI REST API and serves the production-built React frontend.
# Access URL: http://localhost:8080

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

PYTHON_BIN="python3"
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
fi

PORT="${PORT:-8080}"

echo "============================================================"
echo "CRISISGUARD — DECISION SUPPORT WEB APP & API"
echo "Author: B.SIVASAI (Roll Number: 2023BCS0228)"
echo "Course: CSE412 — Big Data & Large-Scale Computing"
echo "============================================================"
echo "Host: 0.0.0.0 | Port: $PORT"
echo "Web Application URL: http://localhost:$PORT"
echo "API Documentation:   http://localhost:$PORT/docs"
echo "============================================================"
echo "Starting Uvicorn server..."

exec "$PYTHON_BIN" -m uvicorn src.api.server:app --host 0.0.0.0 --port "$PORT"
