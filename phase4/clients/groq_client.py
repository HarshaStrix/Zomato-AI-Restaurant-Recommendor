"""
Groq API client for LLM completion.
Uses official Groq Python SDK.
"""

import logging
import time
from typing import Optional

from phase4.clients.base_client import BaseLLMClient
from phase4.config import (
    GROQ_API_KEY,
    GROQ_MAX_RETRIES,
    GROQ_MAX_TOKENS,
    GROQ_MODEL,
    GROQ_RETRY_BACKOFF_FACTOR,
    GROQ_TEMPERATURE,
    GROQ_TIMEOUT_SECONDS,
    LOG_FORMAT,
    LOG_LEVEL,
)

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class GroqClient(BaseLLMClient):
    """Client for Groq API (Llama models)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = GROQ_TEMPERATURE,
        max_tokens: int = GROQ_MAX_TOKENS,
        timeout: int = GROQ_TIMEOUT_SECONDS,
        max_retries: int = GROQ_MAX_RETRIES,
    ) -> None:
        """
        Initialize Groq client.

        Args:
            api_key: Groq API key. Defaults to GROQ_API_KEY env var.
            model: Model name. Defaults to config.
            temperature: Default temperature.
            max_tokens: Default max tokens.
            timeout: Request timeout in seconds.
            max_retries: Number of retries on failure.
        """
        self.api_key = api_key or GROQ_API_KEY
        self.model = model or GROQ_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = None

    def _get_client(self):
        """Lazy-init Groq client."""
        if self._client is None:
            try:
                from groq import Groq

                self._client = Groq(api_key=self.api_key, timeout=self.timeout)
            except Exception as e:
                logger.warning("Failed to create Groq client: %s", e)
                raise
        return self._client

    def is_available(self) -> bool:
        """Return True if API key is set and client can be created."""
        if not self.api_key or not self.api_key.strip():
            return False
        try:
            self._get_client()
            return True
        except Exception:
            return False

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Call Groq API for chat completion.

        Args:
            system_prompt: System message.
            user_prompt: User message.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.

        Returns:
            Content of the assistant reply.

        Raises:
            Exception: On API or network errors after retries.
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        client = self._get_client()
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temp,
                    max_tokens=max_tok,
                )
                content = response.choices[0].message.content
                if not content:
                    return ""
                return content.strip()
            except Exception as e:
                last_error = e
                logger.warning("Groq API attempt %d failed: %s", attempt + 1, e)
                if attempt < self.max_retries - 1:
                    time.sleep(GROQ_RETRY_BACKOFF_FACTOR ** attempt)
                else:
                    raise last_error

        raise last_error or RuntimeError("Groq API failed")
