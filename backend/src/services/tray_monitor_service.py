"""
System Tray Background Health Monitor & Notification Engine implementation.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Dict, Any, List

from src.logger.structured_logger import StructuredLogger
from src.package_manager.plugin_manager import PluginManager
from src.detector.software_detector import DefaultSoftwareDetector

logger = StructuredLogger("services.tray_monitor")


class TrayMonitorService:
    """Background service running periodic system health audits and update checks."""

    def __init__(self, plugin_manager: PluginManager, interval_seconds: int = 300) -> None:
        self._plugin_manager = plugin_manager
        self._interval_seconds = interval_seconds
        self._is_running = False
        self._task: asyncio.Task | None = None
        self._last_audit_time: str | None = None
        self._last_audit_results: Dict[str, Any] = {}
        self._warnings: List[str] = []

    async def run_health_audit(self) -> Dict[str, Any]:
        """Execute comprehensive system health audit."""
        detector = DefaultSoftwareDetector()
        sys_info = await detector.get_system_info()

        warnings: List[str] = []
        plugins = self._plugin_manager.get_all_plugins()

        healthy_count = 0
        degraded_count = 0

        for plugin in plugins:
            try:
                report = await plugin.health_check()
                if report.overall_score >= 80:
                    healthy_count += 1
                else:
                    degraded_count += 1
                    warnings.append(f"Tool '{plugin.metadata.name}' health score is {report.overall_score}/100.")
            except Exception as e:
                degraded_count += 1
                warnings.append(f"Check failed for '{plugin.metadata.name}': {e}")

        # Disk space check
        if sys_info.available_disk_gb < 10.0:
            warnings.append(f"Low disk space warning: Only {sys_info.available_disk_gb:.1f} GB available.")

        self._last_audit_time = datetime.utcnow().isoformat() + "Z"
        self._warnings = warnings
        self._last_audit_results = {
            "timestamp": self._last_audit_time,
            "total_packages": len(plugins),
            "healthy_count": healthy_count,
            "degraded_count": degraded_count,
            "warnings_count": len(warnings),
            "warnings": warnings,
            "available_disk_gb": sys_info.available_disk_gb,
        }

        logger.info(f"Background health audit complete: {healthy_count} healthy, {degraded_count} degraded, {len(warnings)} warnings.")
        return self._last_audit_results

    async def start(self) -> None:
        """Start periodic background monitor task."""
        if self._is_running:
            return
        self._is_running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info(f"TrayMonitorService started (interval: {self._interval_seconds}s).")

    async def stop(self) -> None:
        """Stop periodic background monitor task."""
        if not self._is_running:
            return
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("TrayMonitorService stopped.")

    async def _monitor_loop(self) -> None:
        """Periodic background monitoring loop."""
        while self._is_running:
            try:
                await self.run_health_audit()
            except Exception as e:
                logger.error(f"Error in background health monitor loop: {e}")
            await asyncio.sleep(self._interval_seconds)

    def get_status(self) -> Dict[str, Any]:
        """Return current status of background monitor."""
        return {
            "is_running": self._is_running,
            "interval_seconds": self._interval_seconds,
            "last_audit_time": self._last_audit_time,
            "last_audit_results": self._last_audit_results,
            "active_warnings": self._warnings,
        }
