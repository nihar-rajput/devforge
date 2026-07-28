"""
System Factory for cross-platform OS dispatching.
"""

from __future__ import annotations

import sys
from src.core.ports.path_manager import PathManager
from src.core.ports.system_detector import SystemDetector
from src.detector.posix_detector import PosixSoftwareDetector
from src.detector.software_detector import DefaultSoftwareDetector
from src.system.path_manager import WindowsPathManager
from src.system.posix_path_manager import PosixPathManager


class SystemFactory:
    """Factory creating appropriate PathManager and SystemDetector for the host OS."""

    @staticmethod
    def get_path_manager() -> PathManager:
        """Return host OS PathManager."""
        if sys.platform == "win32":
            return WindowsPathManager()
        return PosixPathManager()

    @staticmethod
    def get_system_detector() -> SystemDetector:
        """Return host OS SystemDetector."""
        if sys.platform == "win32":
            return DefaultSoftwareDetector()
        return PosixSoftwareDetector()
