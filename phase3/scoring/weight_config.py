"""
Weight configuration loader for ranking.
Supports YAML and dict-based configuration.
"""

from pathlib import Path
from typing import Optional

from phase3.config import DEFAULT_WEIGHTS, WEIGHTS_CONFIG_PATH


class WeightConfig:
    """Loads and validates ranking weights from config."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        weights: Optional[dict[str, float]] = None,
    ) -> None:
        """
        Initialize weight config.

        Args:
            config_path: Path to YAML config. If None, uses default path.
            weights: Override with dict of weights.
        """
        self.config_path = config_path or WEIGHTS_CONFIG_PATH
        self._weights = weights

    def get_weights(self) -> dict[str, float]:
        """
        Get ranking weights. Loads from YAML if available, else uses defaults.

        Returns:
            Dict of weight name -> value.
        """
        if self._weights is not None:
            return self._weights.copy()

        if self.config_path.exists():
            try:
                import yaml

                with open(self.config_path) as f:
                    config = yaml.safe_load(f)
                weights = config.get("ranking_weights", DEFAULT_WEIGHTS)
                return dict(weights)
            except Exception:
                pass

        return DEFAULT_WEIGHTS.copy()
