"""Download-related errors."""

from __future__ import annotations

from src.core.errors.base import DevForgeError


class DownloadError(DevForgeError):
    """Base error for download failures."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        details: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        self.url = url
        super().__init__(message, details=details, cause=cause)


class DownloadTimeoutError(DownloadError):
    """Raised when a download exceeds the configured timeout."""

    def __init__(self, url: str, timeout_seconds: int) -> None:
        super().__init__(
            f"Download timed out after {timeout_seconds}s",
            url=url,
            details=f"URL: {url}",
        )


class ChecksumMismatchError(DownloadError):
    """Raised when a downloaded file's checksum doesn't match expected."""

    def __init__(
        self,
        url: str,
        expected: str,
        actual: str,
    ) -> None:
        self.expected = expected
        self.actual = actual
        super().__init__(
            "Checksum verification failed",
            url=url,
            details=f"Expected: {expected}, Got: {actual}",
        )


class DownloadResumeError(DownloadError):
    """Raised when a download cannot be resumed (server doesn't support Range)."""

    def __init__(self, url: str) -> None:
        super().__init__(
            "Cannot resume download: server does not support Range requests",
            url=url,
        )
