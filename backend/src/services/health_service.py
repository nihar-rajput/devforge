"""
Health service implementation for aggregate environment health scoring.
"""

from __future__ import annotations

from typing import Dict

from src.core.enums import HealthStatus
from src.core.ports.package_repository import PackageRepository
from src.package_manager.plugin_manager import PluginManager


class HealthService:
    """
    Computes overall system health scores and collects per-package health reports.
    """

    def __init__(
        self,
        plugin_manager: PluginManager,
        package_repo: PackageRepository | None = None,
    ) -> None:
        self._plugin_manager = plugin_manager
        self._package_repo = package_repo

    async def get_system_health_score(self) -> dict:
        """
        Compute overall environment health score (0-100) across all installed packages.

        Returns:
            Dict with score, status, healthy_count, degraded_count, unhealthy_count.
        """
        plugins = self._plugin_manager.get_all_plugins()
        if not plugins:
            return {
                "score": 100,
                "status": HealthStatus.HEALTHY.value,
                "healthy_count": 0,
                "degraded_count": 0,
                "unhealthy_count": 0,
                "total_installed": 0,
            }

        scores: list[int] = []
        healthy = 0
        degraded = 0
        unhealthy = 0

        for plugin in plugins:
            try:
                report = await plugin.health_check()
                if report.overall_score >= 0:
                    scores.append(report.overall_score)
                    if report.status == HealthStatus.HEALTHY:
                        healthy += 1
                    elif report.status == HealthStatus.DEGRADED:
                        degraded += 1
                    else:
                        unhealthy += 1
            except Exception:
                unhealthy += 1
                scores.append(0)

        total = len(scores)
        overall_score = int(sum(scores) / total) if total > 0 else 100

        status = HealthStatus.HEALTHY
        if overall_score < 40:
            status = HealthStatus.UNHEALTHY
        elif overall_score < 80:
            status = HealthStatus.DEGRADED

        return {
            "score": overall_score,
            "status": status.value,
            "healthy_count": healthy,
            "degraded_count": degraded,
            "unhealthy_count": unhealthy,
            "total_installed": total,
        }
