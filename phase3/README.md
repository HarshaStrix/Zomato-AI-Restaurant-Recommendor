# Phase 3: Recommendation & Ranking Engine

## Overview

Phase 3 implements a modular, configurable recommendation and ranking engine with sophisticated filtering and scoring algorithms.

## Folder Structure

```
phase3/
├── filters/
│   ├── location_filter.py    # Location filter
│   ├── price_filter.py       # Price range filter
│   ├── rating_filter.py      # Minimum rating filter
│   ├── cuisine_filter.py     # Cuisine filter
│   └── filter_engine.py      # Orchestrates all filters
├── scoring/
│   ├── weight_config.py      # YAML/dict weight configuration
│   └── score_calculator.py   # Multi-factor scoring
├── ranking/
│   └── ranker.py             # Ranking with tie-breaking
├── config/
│   └── weights.yaml          # Configurable ranking weights
├── utils/
├── tests/
├── recommendation_engine.py   # Main orchestration
├── config.py
└── run_tests.sh
```

## Features

### 1. Modular Filters (`filters/`)
- **LocationFilter**: Case-insensitive partial match
- **PriceFilter**: Price range (1-4) mapped to buckets (low/medium/high)
- **RatingFilter**: Minimum rating threshold
- **CuisineFilter**: Cuisine match in cuisine/cuisine_list
- **FilterEngine**: Applies all filters in sequence

### 2. Scoring (`scoring/`)
- **WeightConfig**: Loads weights from YAML or dict
- **ScoreCalculator**: Multi-factor scoring:
  - Rating score (40%): (rating / 5.0) × weight
  - Price match score (20%): Alignment with user preference
  - Cuisine match score (20%): Exact/partial match
  - Popularity score (15%): Normalized review count
  - Proximity score (5%): Distance (placeholder)

### 3. Ranking (`ranking/`)
- **Ranker**: Sorts by score with tie-breaking
- Tie-break order: score → rating → votes → name
- Returns top N results

### 4. Recommendation Engine
- Orchestrates: Filter → Score → Rank → Top N
- Returns (recommendations DataFrame, total_found)

## Usage

```python
from phase3.recommendation_engine import RecommendationEngine
import pandas as pd

engine = RecommendationEngine()
df = pd.read_csv("restaurants.csv")

recommendations, total = engine.get_recommendations(
    df,
    location="Bangalore",
    cuisine="Italian",
    min_rating=4.0,
    price_min=2,
    price_max=3,
    limit=5,
)
```

## Configurable Weights

Edit `phase3/config/weights.yaml`:

```yaml
ranking_weights:
  rating: 0.4
  price_match: 0.2
  cuisine_match: 0.2
  popularity: 0.15
  proximity: 0.05
```

## Running Tests

```bash
# From project root
./phase3/run_tests.sh

# Or directly
PYTHONPATH=. python -m pytest phase3/tests/ -v
```

**Test Results:** ✅ All 22 tests pass

## Test Coverage

- **Filters**: 9 tests (location, price, rating, cuisine, filter engine)
- **Scoring**: 5 tests (weight config, score calculator)
- **Ranking**: 4 tests (ranker, tie-breaking, empty df)
- **Recommendation Engine**: 4 tests (full pipeline)
