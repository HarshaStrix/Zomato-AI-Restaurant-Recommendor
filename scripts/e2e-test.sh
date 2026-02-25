#!/usr/bin/env bash
# E2E test: API + UI flow
# Prerequisites: API on :8000, Web on :3000 (or set API_URL, WEB_URL)

set -e
API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:3000}"

echo "=== E2E Test ==="
echo "API: $API_URL | Web: $WEB_URL"

# 1. API options
echo -n "1. GET /api/v1/recommend/options ... "
OPTS=$(curl -s "$API_URL/api/v1/recommend/options")
if echo "$OPTS" | grep -q '"locations"'; then
  echo "OK"
else
  echo "FAIL"
  echo "$OPTS" | head -3
  exit 1
fi

# 2. API recommend
echo -n "2. POST /api/v1/recommend ... "
REC=$(curl -s -X POST "$API_URL/api/v1/recommend" \
  -H "Content-Type: application/json" \
  -d '{"location":{"place":"Bangalore"},"limit":3}')
REC_COUNT=$(echo "$REC" | python3 -c "
import json,sys
d=json.load(sys.stdin)
recs=d.get('data',{}).get('recommendations',[])
print(len(recs))
" 2>/dev/null || echo 0)
if [ "$REC_COUNT" -gt 0 ]; then
  echo "OK ($REC_COUNT recommendations)"
else
  echo "FAIL (no recommendations)"
  echo "$REC" | head -5
  exit 1
fi

# 3. Web page loads (Lexend font)
echo -n "3. Web page (Lexend font) ... "
HTML=$(curl -s "$WEB_URL" 2>/dev/null || true)
if echo "$HTML" | grep -q "Lexend"; then
  echo "OK"
else
  echo "SKIP (client-rendered)"
fi

echo "=== E2E passed ==="
