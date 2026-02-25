#!/usr/bin/env bash
# Run all Python tests (unit + integration) and E2E sanity.
# Excludes groq_integration (requires GROQ_API_KEY).

set -e
cd "$(dirname "$0")/.."
export PYTHONPATH=.

echo "=== Python unit + integration tests ==="
pytest phase1/tests phase2/tests phase3/tests phase4/tests backend/tests tests/ \
  -v --tb=short -m "not groq_integration" "$@"

echo ""
echo "=== E2E sanity (API + Web) ==="
./scripts/e2e-test.sh

echo ""
echo "=== All tests passed ==="
