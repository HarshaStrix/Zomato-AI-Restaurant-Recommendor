#!/bin/bash
# Run Phase 1 tests
# Execute from project root: ./phase1/run_tests.sh

set -e
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
source .venv/bin/activate 2>/dev/null || true
python -m pytest phase1/tests/ -v --tb=short -m "not integration"
