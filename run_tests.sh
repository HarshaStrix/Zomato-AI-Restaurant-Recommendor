#!/bin/bash
# Run all Phase 1 tests
# Execute from project root: ./run_tests.sh

set -e
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
python -m pytest backend/tests/ -v --tb=short
