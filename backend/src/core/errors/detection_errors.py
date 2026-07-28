"""Detection-related errors."""

from __future__ import annotations

from src.core.errors.base import DevForgeError


class DetectionError(DevForgeError):
    """Base error for detection failures."""


class DetectionTimeoutError(DetectionError):
    """Raised when a detection probe exceeds the configured timeout."""

    def __init__(self, probe_name: str, timeout_seconds: int) -> None:
        super().__init__(
            f"Detection probe '{probe_name}' timed out after {timeout_seconds}s"
        )


class GPUDetectionError(DetectionError):
    """Raised when GPU detection fails (e.g., NVML not available)."""

    def __init__(self, vendor: str, reason: str) -> None:
        super().__init__(
            f"Failed to detect {vendor} GPU: {reason}",
            details="Ensure GPU drivers are installed.",
        )
