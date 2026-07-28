"""
Download progress tracking calculator.
"""

from __future__ import annotations

import time


class ProgressTracker:
    """
    Tracks download transfer rates, ETA, and progress percentages.
    """

    def __init__(self, total_bytes: int | None = None) -> None:
        self.total_bytes = total_bytes
        self.downloaded_bytes = 0
        self.start_time = time.monotonic()
        self.last_time = self.start_time
        self.last_bytes = 0
        self.speed = 0.0
        self.eta = None

    def update(self, current_bytes: int) -> tuple[float, float | None, float]:
        """
        Update with current total downloaded bytes.

        Returns:
            Tuple of (progress_percent, eta_seconds, speed_bytes_per_sec).
        """
        now = time.monotonic()
        delta_time = now - self.last_time

        self.downloaded_bytes = current_bytes

        if delta_time >= 0.5:
            delta_bytes = current_bytes - self.last_bytes
            self.speed = delta_bytes / delta_time if delta_time > 0 else 0.0
            self.last_time = now
            self.last_bytes = current_bytes

        # Calculate progress percent
        if self.total_bytes and self.total_bytes > 0:
            percent = min(100.0, (current_bytes / self.total_bytes) * 100)
            remaining_bytes = self.total_bytes - current_bytes
            self.eta = remaining_bytes / self.speed if self.speed > 0 else None
        else:
            percent = 0.0
            self.eta = None

        return percent, self.eta, self.speed
