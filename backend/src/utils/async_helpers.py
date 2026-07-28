"""
Async utility functions.

Helpers for common async patterns: timeouts, retries,
concurrency limiting, and callback-based progress tracking.
"""

from __future__ import annotations

import asyncio
import random
from typing import Any, Callable, Coroutine, TypeVar

from src.config.constants import MAX_RETRY_DELAY_SECONDS, RETRY_JITTER_FACTOR

T = TypeVar("T")


async def run_with_timeout(
    coro: Coroutine[Any, Any, T],
    timeout_seconds: float,
    error_message: str = "Operation timed out",
) -> T:
    """
    Run a coroutine with a timeout.

    Args:
        coro: Coroutine to execute.
        timeout_seconds: Maximum time to wait.
        error_message: Error message if timeout occurs.

    Returns:
        The coroutine's return value.

    Raises:
        TimeoutError: If the coroutine doesn't complete in time.
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(error_message) from None


async def retry_with_backoff(
    func: Callable[..., Coroutine[Any, Any, T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = MAX_RETRY_DELAY_SECONDS,
    jitter_factor: float = RETRY_JITTER_FACTOR,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception], Coroutine[Any, Any, None]] | None = None,
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Retry an async function with exponential backoff and jitter.

    Implements the "decorrelated jitter" strategy recommended by AWS
    for distributed systems, preventing thundering herd on retries.

    Args:
        func: Async function to call.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay between retries (seconds).
        max_delay: Maximum delay cap (seconds).
        jitter_factor: Randomness factor (0.0 = no jitter, 1.0 = full jitter).
        retryable_exceptions: Exception types that trigger a retry.
        on_retry: Optional callback invoked before each retry.
        *args: Positional arguments for func.
        **kwargs: Keyword arguments for func.

    Returns:
        The function's return value on success.

    Raises:
        The last exception if all retries are exhausted.
    """
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except retryable_exceptions as exc:
            last_exception = exc

            if attempt == max_retries:
                break

            # Exponential backoff with decorrelated jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = delay * jitter_factor * random.random()
            actual_delay = delay + jitter

            if on_retry:
                await on_retry(attempt + 1, exc)

            await asyncio.sleep(actual_delay)

    raise last_exception  # type: ignore[misc]


class ConcurrencyLimiter:
    """
    Limit concurrent execution of async tasks.

    Uses asyncio.Semaphore to control how many tasks run
    simultaneously, preventing resource exhaustion.

    Usage:
        limiter = ConcurrencyLimiter(max_concurrent=3)
        async with limiter:
            await do_work()
    """

    def __init__(self, max_concurrent: int) -> None:
        """
        Args:
            max_concurrent: Maximum number of concurrent tasks.
        """
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._max = max_concurrent
        self._active = 0

    @property
    def active_count(self) -> int:
        """Number of currently active tasks."""
        return self._active

    @property
    def available_slots(self) -> int:
        """Number of available slots."""
        return self._max - self._active

    async def __aenter__(self) -> ConcurrencyLimiter:
        await self._semaphore.acquire()
        self._active += 1
        return self

    async def __aexit__(self, *args: Any) -> None:
        self._active -= 1
        self._semaphore.release()


async def gather_with_concurrency(
    max_concurrent: int,
    *coros: Coroutine[Any, Any, T],
) -> list[T]:
    """
    Run multiple coroutines with a concurrency limit.

    Like asyncio.gather() but with a maximum number of concurrent tasks.

    Args:
        max_concurrent: Maximum concurrent tasks.
        *coros: Coroutines to execute.

    Returns:
        List of results in the same order as the input coroutines.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited(coro: Coroutine[Any, Any, T]) -> T:
        async with semaphore:
            return await coro

    return await asyncio.gather(*(limited(c) for c in coros))
