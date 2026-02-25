"""
Base interface for LLM clients.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseLLMClient(ABC):
    """Abstract base class for LLM API clients."""

    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 600,
    ) -> str:
        """
        Send prompt to LLM and return raw text response.

        Args:
            system_prompt: System/instruction prompt.
            user_prompt: User message content.
            temperature: Sampling temperature (0-1).
            max_tokens: Maximum tokens to generate.

        Returns:
            Raw response text from the model.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the client is configured and can make calls."""
        pass
