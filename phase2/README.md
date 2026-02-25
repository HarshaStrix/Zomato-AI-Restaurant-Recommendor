# Phase 2: Backend REST API with FastAPI

## Overview

Phase 2 implements a RESTful API for restaurant recommendations using FastAPI. It provides filtering, ranking, and recommendation endpoints.

## Folder Structure

```
phase2/
├── api/
│   ├── routes/
│   │   └── recommendations.py    # POST /recommend endpoint
│   ├── schemas/
│   │   ├── request.py           # Request validation schemas
│   │   └── response.py           # Response schemas
│   ├── middleware/               # Middleware (CORS, etc.)
│   ├── utils/
│   │   └── exceptions.py        # Custom exceptions
│   └── main.py                  # FastAPI app
├── services/
│   ├── database_service.py      # Database queries
│   └── recommendation_service.py # Orchestration service
├── filters/
│   └── filter_engine.py         # Filtering logic
├── ranking/
│   └── ranking_engine.py        # Ranking/scoring logic
├── tests/
│   ├── test_api.py              # API endpoint tests
│   ├── test_database_service.py
│   ├── test_filter_engine.py
│   ├── test_ranking_engine.py
│   └── test_recommendation_service.py
├── config.py                    # Configuration
├── main.py                      # Entry point
├── run_tests.sh                 # Test runner
└── run_server.sh                # Server runner
```

## Features

### 1. REST API (`api/`)
- **POST /api/v1/recommend**: Get restaurant recommendations
- Input validation with Pydantic
- Structured JSON responses
- Error handling

### 2. Filtering Engine (`filters/`)
- Location filtering (case-insensitive partial match)
- Cuisine filtering
- Rating filtering (minimum threshold)
- Price range filtering

### 3. Ranking Engine (`ranking/`)
- Multi-factor scoring:
  - Rating score (40% weight)
  - Price match score (20% weight)
  - Cuisine match score (20% weight)
  - Popularity score (15% weight)
  - Proximity score (5% weight)
- Returns top N restaurants sorted by score

### 4. Database Service (`services/`)
- Queries Phase 1 SQLite database
- Supports filtering by multiple criteria
- Handles missing database gracefully

## API Endpoint

### POST /api/v1/recommend

**Request Body:**
```json
{
  "location": {
    "place": "Bangalore",
    "coordinates": {
      "latitude": 12.9716,
      "longitude": 77.5946
    }
  },
  "price_range": {
    "min": 2,
    "max": 3
  },
  "minimum_rating": 4.0,
  "cuisine": "Italian",
  "limit": 5
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "restaurant_id": 1,
        "name": "Restaurant A",
        "location": "Bangalore",
        "cuisine": "Italian",
        "rating": 4.5,
        "price_range": 2,
        "review_count": 500,
        "score": 0.85,
        "explanation": null
      }
    ],
    "summary": {
      "total_found": 10,
      "returned": 5,
      "ai_explanation": null
    }
  },
  "metadata": {
    "query_id": "uuid",
    "processing_time_ms": 45
  }
}
```

## Running Tests

```bash
# From project root
./phase2/run_tests.sh

# Or directly
cd phase2
PYTHONPATH=.. python -m pytest tests/ -v
```

**Test Results:** ✅ All 24 tests pass

## Running Server

```bash
# From project root
./phase2/run_server.sh

# Or directly
cd phase2
PYTHONPATH=.. python main.py
```

Server runs on `http://0.0.0.0:8000`

**API Documentation:** `http://localhost:8000/docs` (Swagger UI)

## Prerequisites

- Phase 1 must be run first to create the database
- Database path: `phase1/data/processed/restaurants.db`

## Test Coverage

✅ API endpoints (7 tests)  
✅ Database service (4 tests)  
✅ Filter engine (5 tests)  
✅ Ranking engine (4 tests)  
✅ Recommendation service (4 tests)  

All tests verified and passing!
