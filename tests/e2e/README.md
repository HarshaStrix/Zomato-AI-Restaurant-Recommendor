# E2E Test Suite

## Running E2E Tests

### Prerequisites
1. Phase 1 database must exist: `python phase1/main.py`
2. API running on http://localhost:8000: `./start-api.sh` or `python phase2/api/main.py`
3. (Optional) Web running on http://localhost:3000 for full E2E: `cd web && npm run dev`

### Quick E2E (API only)
```bash
./scripts/e2e-test.sh
```

### Full E2E (API + Web)
```bash
./run-app.sh   # Starts API + Web
# In another terminal:
./scripts/e2e-test.sh
```

### Integration Tests (Python)
```bash
PYTHONPATH=. python -m pytest tests/integration -v
```

## Test Coverage

- **API options**: GET /api/v1/recommend/options returns locations, cuisines, price tiers
- **Recommendations**: POST /api/v1/recommend with location, cuisine, price_tier, minimum_rating
- **Cost in ₹**: Response includes `cost` field (Indian Rupees) when available
- **Min rating**: 0.1 precision (4.2), 0.5 precision (4.5) supported
- **Price tier**: budget (≤₹500), mid (₹500-1500), premium (>₹1500)
