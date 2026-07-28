"""
Installation queue manager.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List
from uuid import UUID

from src.core.entities.installation import Installation
from src.core.value_objects.package_id import PackageId
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("installer.queue")


class InstallationQueueManager:
    """
    Queue manager for ordering and executing package installation jobs.
    """

    def __init__(self, max_concurrent: int = 1) -> None:
        self._max_concurrent = max_concurrent
        self._queue: asyncio.Queue[Installation] = asyncio.Queue()
        self._active: Dict[str, Installation] = {}
        self._cancelled: set[str] = set()

    def enqueue(self, installation: Installation) -> None:
        """Add an installation operation to the queue."""
        self._queue.put_nowait(installation)
        logger.info(f"Enqueued installation '{installation.id}' for package '{installation.package_id.value}'")

    async def get_next(self) -> Installation:
        """Get next installation from queue."""
        inst = await self._queue.get()
        self._active[str(inst.id)] = inst
        return inst

    def mark_completed(self, installation_id: UUID) -> None:
        """Mark installation as completed and remove from active list."""
        self._active.pop(str(installation_id), None)
        self._queue.task_done()

    def cancel(self, installation_id: UUID) -> bool:
        """Request cancellation of an active or queued installation."""
        inst_str = str(installation_id)
        if inst_str in self._active:
            self._active[inst_str].is_cancelled = True
            self._cancelled.add(inst_str)
            logger.info(f"Requested cancellation for installation '{installation_id}'")
            return True
        return False

    @property
    def pending_count(self) -> int:
        """Number of items waiting in queue."""
        return self._queue.qsize()

    @property
    def active_count(self) -> int:
        """Number of active installations."""
        return len(self._active)
