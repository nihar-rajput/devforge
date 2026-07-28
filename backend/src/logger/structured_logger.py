"""
Structured logger wrapper.

Provides a thin convenience layer over structlog with context
binding for operation tracking (correlation IDs, package IDs).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from src.config.logging_config import get_logger


class StructuredLogger:
    """
    Structured logger with automatic context binding.

    Wraps structlog to provide consistent field naming across
    the application. Each log entry includes the component name,
    and can be enriched with correlation IDs for request tracing.

    Usage:
        logger = StructuredLogger("installer.engine")
        logger.info("Installation started", package_id="python", version="3.12.1")
        logger.with_context(correlation_id=uuid).info("Step completed")
    """

    def __init__(self, component: str) -> None:
        """
        Initialize logger for a specific component.

        Args:
            component: Dot-separated component name (e.g., 'downloader.manager').
        """
        self._logger: structlog.stdlib.BoundLogger = get_logger(component)
        self._component = component

    def with_context(self, **kwargs: Any) -> StructuredLogger:
        """
        Create a child logger with additional bound context.

        Args:
            **kwargs: Key-value pairs to bind to all subsequent log entries.

        Returns:
            New logger instance with the additional context.
        """
        new_logger = StructuredLogger(self._component)
        new_logger._logger = self._logger.bind(**kwargs)
        return new_logger

    def bind_correlation(self, correlation_id: UUID) -> StructuredLogger:
        """Bind a correlation ID for request/operation tracing."""
        return self.with_context(correlation_id=str(correlation_id))

    def bind_package(self, package_id: str) -> StructuredLogger:
        """Bind a package ID to all subsequent log entries."""
        return self.with_context(package_id=package_id)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log at DEBUG level."""
        self._logger.debug(message, component=self._component, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log at INFO level."""
        self._logger.info(message, component=self._component, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log at WARNING level."""
        self._logger.warning(message, component=self._component, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log at ERROR level."""
        self._logger.error(message, component=self._component, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log at CRITICAL level."""
        self._logger.critical(message, component=self._component, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log at ERROR level with exception traceback."""
        self._logger.exception(message, component=self._component, **kwargs)
