# Phase 1: Data Ingestion & Preprocessing

## Overview

Phase 1 implements the complete data pipeline for ingesting, cleaning, and storing restaurant data from Hugging Face.

## Folder Structure

```
phase1/
├── data/
│   ├── raw/              # Raw CSV from Hugging Face
│   └── processed/        # Processed CSV + SQLite DB
├── ingestion/
│   ├── __init__.py
│   └── dataset_loader.py # Loads dataset from Hugging Face
├── preprocessing/
│   ├── __init__.py
│   ├── cleaner.py        # Data cleaning and normalization
│   └── feature_engineering.py  # Feature creation
├── database/
│   ├── __init__.py
│   └── db_manager.py     # SQLite database operations
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Test fixtures
│   ├── test_dataset_loader.py
│   └── test_preprocessing.py
├── config.py             # Configuration constants
├── main.py               # Pipeline entry point
├── run_tests.sh          # Test runner script
└── run_pipeline.sh       # Pipeline runner script
```

## Features

### 1. Dataset Loader (`ingestion/dataset_loader.py`)
- Loads Zomato dataset from Hugging Face
- Maps columns automatically (handles different naming conventions)
- Saves raw CSV for backup

### 2. Data Cleaner (`preprocessing/cleaner.py`)
- Parses ratings from various formats (`"4.2/5"`, `"NEW"`, etc.)
- Normalizes cuisines to lists
- Handles missing values
- Removes duplicates

### 3. Feature Engineer (`preprocessing/feature_engineering.py`)
- Creates `price_bucket` (low/medium/high)
- Creates `normalized_rating` (0-1 scale)
- Ensures proper data types

### 4. Database Manager (`database/db_manager.py`)
- Creates SQLite database
- Inserts processed data
- Creates indexes on location, cuisine, rating

## Running Tests

```bash
# From project root
./phase1/run_tests.sh

# Or directly
cd phase1
PYTHONPATH=.. python -m pytest tests/ -v -m "not integration"
```

**Test Results:** ✅ All 12 tests pass

## Running Pipeline

```bash
# From project root
./phase1/run_pipeline.sh

# Or directly
cd phase1
PYTHONPATH=.. python main.py
```

**Note:** First run downloads ~574MB from Hugging Face. Cache stored in `phase1/data/.hf_cache/`.

## Output

After successful pipeline run:
- **Raw data:** `phase1/data/raw/zomato_raw.csv`
- **Processed data:** `phase1/data/processed/zomato_processed.csv`
- **Database:** `phase1/data/processed/restaurants.db`

The pipeline prints:
- Number of rows processed
- Number of rows inserted into database
- Sample processed rows (first 5)

## Test Coverage

✅ Dataset loading and column mapping  
✅ Data cleaning (nulls, duplicates, normalization)  
✅ Feature engineering (price_bucket, normalized_rating)  
✅ Database insertion and row count validation  

All tests verified and passing!
