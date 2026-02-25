#!/bin/bash
# Run Phase 3 tests
# Execute from project root: ./phase3/run_tests.sh

set -e
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
source .venv/bin/activate 2>/dev/null || true
python -m pytest phase3/tests/ -v --tb=short
