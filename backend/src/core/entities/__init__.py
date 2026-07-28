"""
Domain entities.

Entities are objects with identity and lifecycle. They are mutable
(their state changes over time) and are identified by a unique ID
rather than by their attribute values.
"""

from src.core.entities.download import Download, DownloadSegment
from src.core.entities.environment import EnvironmentProfile, StackDefinition
from src.core.entities.health_report import HealthCheck, HealthReport
from src.core.entities.installation import Installation, InstallationStep
from src.core.entities.package import Dependency, DownloadInfo, Package, PluginMetadata

__all__ = [
    "Dependency",
    "Download",
    "DownloadInfo",
    "DownloadSegment",
    "EnvironmentProfile",
    "HealthCheck",
    "HealthReport",
    "Installation",
    "InstallationStep",
    "Package",
    "PluginMetadata",
    "StackDefinition",
]
