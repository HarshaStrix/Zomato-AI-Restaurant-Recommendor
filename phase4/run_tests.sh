#!/bin/bash
# Run Phase 4 tests (excludes Groq integration unless GROQ_API_KEY is set)
# With API key: GROQ_API_KEY=xxx ./phase4/run_tests.sh
# Include Groq tests: GROQ_API_KEY=xxx ./phase4/run_tests.sh  (no -m "not groq_integration")

set -e
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
source .venv/bin/activate 2>/dev/null || true
# Exclude groq_integration by default so tests pass without API key
python -m pytest phase4/tests/ -v --tb=short -m "not groq_integration"
