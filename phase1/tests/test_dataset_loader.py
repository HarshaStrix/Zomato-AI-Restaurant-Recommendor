"""
Tests for DatasetLoader.
Validates dataset loading, column mapping, and raw save.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from phase1.ingestion.dataset_loader import DatasetLoader
from phase1.config import REQUIRED_COLUMNS, RAW_DATA_DIR, RAW_CSV_FILENAME


class TestDatasetLoader:
    """Test suite for DatasetLoader."""

    def test_required_columns_defined(self) -> None:
        """Validate that required columns are defined in config."""
        assert "name" in REQUIRED_COLUMNS
        assert "cuisine" in REQUIRED_COLUMNS
        assert "location" in REQUIRED_COLUMNS
        assert "rating" in REQUIRED_COLUMNS
        assert "cost" in REQUIRED_COLUMNS

    @patch("datasets.load_dataset")
    def test_load_maps_columns_correctly(
        self, mock_load_dataset: MagicMock, sample_raw_dataframe: pd.DataFrame
    ) -> None:
        """Test that load maps Hugging Face columns to expected names."""
        from datasets import Dataset

        mock_load_dataset.return_value = {
            "train": Dataset.from_pandas(sample_raw_dataframe)
        }

        loader = DatasetLoader()
        df = loader.load()

        assert df is not None
        assert len(df) == 5
        assert "name" in df.columns
        assert "cuisine" in df.columns
        assert "location" in df.columns
        assert "rating" in df.columns
        assert "cost" in df.columns

    @patch("datasets.load_dataset")
    def test_load_and_save_raw(
        self, mock_load_dataset: MagicMock, sample_raw_dataframe: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Test that load_and_save saves raw data to file."""
        from datasets import Dataset

        raw_dir = tmp_path / "data" / "raw"
        mock_load_dataset.return_value = {
            "train": Dataset.from_pandas(sample_raw_dataframe)
        }

        loader = DatasetLoader(raw_dir=raw_dir)
        df = loader.load_and_save()

        raw_path = raw_dir / RAW_CSV_FILENAME
        assert raw_path.exists()
        loaded = pd.read_csv(raw_path)
        assert len(loaded) == len(df)

    @pytest.mark.integration
    def test_load_real_dataset(self) -> None:
        """Integration test: load real dataset from Hugging Face (requires network)."""
        loader = DatasetLoader()
        df = loader.load()
        assert df is not None
        assert len(df) > 0
        for col in REQUIRED_COLUMNS:
            assert col in df.columns, f"Missing required column: {col}"
