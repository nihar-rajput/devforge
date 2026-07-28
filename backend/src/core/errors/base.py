"""
Base error types for DevForge.

All custom exceptions inherit from DevForgeError, providing a
consistent error hierarchy for structured error handling.
"""

from __future__ import annotations


class DevForgeError(Exception):
    """
    Base exception for all DevForge errors.

    All custom exceptions inherit from this class to enable
    catch-all handling at API boundaries while preserving
    specific error types for targeted handling.
    """

    def __init__(
        self,
        message: str,
        *,
        details: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        self.message = message
        self.details = details
        self.cause = cause
        super().__init__(message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.details:
            parts.append(f"Details: {self.details}")
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        return " | ".join(parts)
