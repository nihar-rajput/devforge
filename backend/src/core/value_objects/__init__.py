"""
Domain value objects.

Value objects are immutable, equality-by-value types that carry
domain meaning beyond their primitive representation.
"""

from src.core.value_objects.checksum import Checksum
from src.core.value_objects.file_size import FileSize
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.system_requirements import SystemRequirements
from src.core.value_objects.version import Version

__all__ = [
    "Checksum",
    "FileSize",
    "PackageId",
    "SystemRequirements",
    "Version",
]
