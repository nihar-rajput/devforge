"""Detection engine package."""

from src.detector.filesystem_scanner import FilesystemScanner
from src.detector.gpu_detector import DefaultGPUDetector
from src.detector.path_scanner import PathScanner
from src.detector.registry_scanner import RegistryScanner
from src.detector.software_detector import DefaultSoftwareDetector
from src.detector.version_detector import VersionDetector

__all__ = [
    "DefaultGPUDetector",
    "DefaultSoftwareDetector",
    "FilesystemScanner",
    "PathScanner",
    "RegistryScanner",
    "VersionDetector",
]
