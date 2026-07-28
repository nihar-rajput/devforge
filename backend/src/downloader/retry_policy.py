"""
Retry policy implementation.

Provides exponential backoff with decorrelated jitter for resilient downloads.
"""

from __future__ import annotations

import asyncio
import random
from typing import Any, Callable, Coroutine, TypeVar

from src.config.constants import MAX_RETRY_DELAY_SECONDS, RETRY_JITTER_FACTOR
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("downloader.retry")

T = TypeVar("T")


class ExponentialBackoffRetry:
    """
    Resilient retry policy with exponential backoff and decorrelated jitter.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = MAX_RETRY_DELAY_SECONDS,
        jitter_factor: float = RETRY_JITTER_FACTOR,
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter_factor = jitter_factor

    def compute_delay(self, attempt: int) -> float:
        """Calculate backoff delay for attempt number (0-indexed)."""
        temp = min(self.max_delay, self.base_delay * (2 ** attempt))
        jitter = temp * self.jitter_factor * random.random()
        return temp + jitter

    async def execute(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Execute an async function with retries on failure.
        """
        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                if attempt >= self.max_retries:
                    logger.error(f"Function {func.__name__} failed after {self.max_retries} retries: {exc}")
                    break

                delay = self.compute_delay(attempt)
                logger.warning(
                    f"Retry attempt {attempt + 1}/{self.max_retries} for {func.__name__} after {delay:.2f}s delay. Error: {exc}"
                )
                await asyncio.sleep(delay)

        raise last_exc  # type: ignore[misc]
