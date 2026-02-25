"""
Dataset Loader for Zomato Restaurant Recommendation data.
Loads data from Hugging Face, converts to DataFrame, and saves raw copy.
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from phase1.config import (
    COLUMN_MAPPING,
    HUGGINGFACE_DATASET,
    HUGGINGFACE_SPLIT,
    RAW_DATA_DIR,
    RAW_CSV_FILENAME,
    REQUIRED_COLUMNS,
    LOG_FORMAT,
    LOG_LEVEL,
)

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class DatasetLoader:
    """Loads Zomato dataset from Hugging Face and prepares it for processing."""

    def __init__(
        self,
        dataset_name: str = HUGGINGFACE_DATASET,
        split: str = HUGGINGFACE_SPLIT,
        raw_dir: Path = RAW_DATA_DIR,
    ) -> None:
        """
        Initialize the dataset loader.

        Args:
            dataset_name: Hugging Face dataset identifier.
            split: Dataset split to load (e.g., 'train').
            raw_dir: Directory to save raw data.
        """
        self.dataset_name = dataset_name
        self.split = split
        self.raw_dir = Path(raw_dir)
        self._df: Optional[pd.DataFrame] = None
        self._column_map: dict[str, str] = {}

    def _resolve_columns(self, available_columns: list[str]) -> dict[str, str]:
        """
        Map expected column names to actual dataset column names.

        Args:
            available_columns: List of column names in the dataset.

        Returns:
            Dict mapping our expected names to actual column names.
        """
        column_map: dict[str, str] = {}
        available_lower = {c.lower(): c for c in available_columns}

        for expected, candidates in COLUMN_MAPPING.items():
            for candidate in candidates:
                cand_lower = candidate.lower()
                if cand_lower in available_lower:
                    column_map[expected] = available_lower[cand_lower]
                    break
            else:
                # Partial match for columns like approx_cost(for_two)
                for candidate in candidates:
                    cand_lower = candidate.lower()
                    for avail_lower, avail_orig in list(available_lower.items()):
                        if cand_lower in avail_lower:
                            column_map[expected] = avail_orig
                            break
                    if expected in column_map:
                        break

        return column_map

    def load(self) -> pd.DataFrame:
        """
        Load dataset from Hugging Face and convert to DataFrame.

        Returns:
            pandas DataFrame with the dataset.

        Raises:
            ValueError: If required columns are not found after mapping.
        """
        logger.info("Loading dataset from Hugging Face: %s", self.dataset_name)

        from datasets import load_dataset

        # Use project-local cache to avoid permission issues
        cache_dir = self.raw_dir.parent / ".hf_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        dataset = load_dataset(
            self.dataset_name,
            cache_dir=str(cache_dir),
        )

        # Handle different split structures
        if self.split in dataset:
            hf_split = dataset[self.split]
        else:
            # Use first available split
            first_split = list(dataset.keys())[0]
            hf_split = dataset[first_split]
            logger.warning(
                "Split '%s' not found, using '%s'", self.split, first_split
            )

        df = hf_split.to_pandas()
        logger.info("Loaded %d rows, %d columns", len(df), len(df.columns))

        # Resolve column mapping
        self._column_map = self._resolve_columns(list(df.columns))
        logger.info("Column mapping: %s", self._column_map)

        # Validate required columns
        missing = [c for c in REQUIRED_COLUMNS if c not in self._column_map]
        if missing:
            raise ValueError(
                f"Required columns not found: {missing}. "
                f"Available columns: {list(df.columns)}"
            )

        # Rename columns to our standard names
        rename_map = {v: k for k, v in self._column_map.items()}
        df = df.rename(columns=rename_map)

        # Keep only mapped columns (expected names)
        keep_cols = list(self._column_map.keys())
        df = df[[c for c in keep_cols if c in df.columns]]

        self._df = df
        logger.info("Dataset prepared with columns: %s", list(df.columns))
        return df

    def save_raw(self) -> Path:
        """
        Save raw DataFrame to CSV in raw data directory.

        Returns:
            Path to the saved file.

        Raises:
            RuntimeError: If load() was not called first.
        """
        if self._df is None:
            raise RuntimeError("Call load() before save_raw()")

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.raw_dir / RAW_CSV_FILENAME
        self._df.to_csv(output_path, index=False)
        logger.info("Saved raw data to %s (%d rows)", output_path, len(self._df))
        return output_path

    def load_and_save(self) -> pd.DataFrame:
        """
        Load dataset and save raw copy. Convenience method.

        Returns:
            DataFrame with loaded data.
        """
        df = self.load()
        self.save_raw()
        return df

    @property
    def dataframe(self) -> Optional[pd.DataFrame]:
        """Return the loaded DataFrame, or None if not yet loaded."""
        return self._df

    @property
    def column_map(self) -> dict[str, str]:
        """Return the resolved column mapping."""
        return self._column_map.copy()
