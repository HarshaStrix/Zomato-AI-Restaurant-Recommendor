#!/usr/bin/env bash
# Start the Restaurant Recommendation API (Phase 2).
# API will be at http://localhost:8000
# Docs at http://localhost:8000/docs

set -e
cd "$(dirname "$0")"
export PYTHONPATH=.
echo "Starting API at http://localhost:8000 (Ctrl+C to stop)"
exec python phase2/api/main.py
