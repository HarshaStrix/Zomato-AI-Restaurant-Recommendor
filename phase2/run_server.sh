#!/bin/bash
# Run Phase 2 API server
# Execute from project root: ./phase2/run_server.sh

set -e
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
source .venv/bin/activate 2>/dev/null || true
python phase2/main.py
