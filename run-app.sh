#!/usr/bin/env bash
# Run DB (Phase 1 if needed), API, then Frontend. Opens at http://localhost:3000
# Usage: ./run-app.sh

set -e
cd "$(dirname "$0")"
export PYTHONPATH=.

# 1. Load .env so GROQ_API_KEY is available for the API process
if [ -f .env ]; then
  set -a
  source .env
  set +a
  echo "Loaded .env (GROQ_API_KEY is set for API)"
fi

# 2. Ensure Phase 1 DB exists
DB_PATH="phase1/data/processed/restaurants.db"
if [ ! -f "$DB_PATH" ]; then
  echo "Database not found. Running Phase 1 pipeline (this may take a minute)..."
  python phase1/main.py
  echo "Phase 1 done. Database ready."
else
  echo "Database found at $DB_PATH"
fi

# 3. Start API in background if not already running
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q 200; then
  echo "Starting API on http://localhost:8000 ..."
  python phase2/api/main.py &
  API_PID=$!
  # Wait for API to be ready (up to 15 seconds)
  for i in $(seq 1 15); do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q 200; then
      echo "API is ready."
      break
    fi
    if [ $i -eq 15 ]; then
      echo "API failed to start. Check errors above."
      exit 1
    fi
    sleep 1
  done
else
  echo "API already running at http://localhost:8000"
fi

# 4. Start frontend and show URL
echo ""
echo "=============================================="
echo "  WORKING URL:  http://localhost:3000"
echo "  Open this in your browser once the frontend is ready."
echo "=============================================="
echo ""
cd web && npm run dev
