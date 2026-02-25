"""
Phase 1: Data Ingestion & Preprocessing Pipeline.
Runs the full pipeline: Load -> Clean -> Engineer -> Store.
"""

import logging
import os
import sys
from pathlib import Path

# Ensure project root is on path when run as script
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Use project-local Hugging Face cache (avoid permission issues)
_hf_cache = _project_root / "phase1" / "data" / ".hf_cache"
os.environ.setdefault("HF_HOME", str(_hf_cache))
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(_hf_cache))

from phase1.config import (
    PROCESSED_DATA_DIR,
    PROCESSED_CSV_FILENAME,
    LOG_FORMAT,
    LOG_LEVEL,
)
from phase1.ingestion.dataset_loader import DatasetLoader
from phase1.preprocessing.cleaner import DataCleaner
from phase1.preprocessing.feature_engineering import FeatureEngineer
from phase1.database.db_manager import DatabaseManager

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def run_pipeline() -> tuple[int, int]:
    """
    Run the full Phase 1 pipeline end-to-end.

    Returns:
        Tuple of (rows_processed, rows_inserted).
    """
    logger.info("Starting Phase 1 pipeline")

    # 1. Load dataset
    loader = DatasetLoader()
    df_raw = loader.load_and_save()
    logger.info("Loaded %d raw rows", len(df_raw))

    # 2. Clean data
    cleaner = DataCleaner()
    df_clean = cleaner.clean(df_raw)
    logger.info("Cleaned to %d rows", len(df_clean))

    # 3. Feature engineering
    engineer = FeatureEngineer()
    df_processed = engineer.transform(df_clean)
    logger.info("Engineered features for %d rows", len(df_processed))

    # 4. Save processed CSV
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    processed_path = PROCESSED_DATA_DIR / PROCESSED_CSV_FILENAME
    df_processed.to_csv(processed_path, index=False)
    logger.info("Saved processed data to %s", processed_path)

    # 5. Store in SQLite
    db = DatabaseManager()
    db.create_table()
    rows_inserted = db.insert_dataframe(df_processed)
    db.close()

    logger.info("Pipeline complete. %d rows inserted into database", rows_inserted)
    return len(df_processed), rows_inserted


def main() -> None:
    """Entry point: run pipeline and print results."""
    try:
        rows_processed, rows_inserted = run_pipeline()

        print("\n" + "=" * 60)
        print("PHASE 1 PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Rows processed:  {rows_processed}")
        print(f"Rows inserted:   {rows_inserted}")
        print("=" * 60 + "\n")

        # Print sample rows
        import pandas as pd
        from phase1.config import PROCESSED_DATA_DIR, PROCESSED_CSV_FILENAME
        sample_path = PROCESSED_DATA_DIR / PROCESSED_CSV_FILENAME
        if sample_path.exists():
            df = pd.read_csv(sample_path, nrows=5)
            print("Sample processed rows (first 5):")
            print(df.to_string())
            print()

    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
