"""
Platform detection utilities.

Detects OS, architecture, and platform-specific capabilities.
Used to select appropriate installer types and system integration.
"""

from __future__ import annotations

import platform
import sys

from src.core.enums import Architecture


def get_os_name() -> str:
    """Get the current operating system name."""
    return platform.system().lower()


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform == "linux"


def is_macos() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"


def get_architecture() -> Architecture:
    """
    Detect the CPU architecture.

    Returns:
        Architecture enum value.
    """
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return Architecture.X86_64
    elif machine in ("aarch64", "arm64"):
        return Architecture.ARM64
    else:
        # Default to x86_64 for unknown architectures
        return Architecture.X86_64


def get_os_version() -> str:
    """Get the OS version string."""
    return platform.version()


def get_os_build_number() -> int:
    """
    Get the Windows build number.

    Returns:
        Build number (e.g., 19041 for Windows 10 2004).
        Returns 0 on non-Windows platforms.
    """
    if not is_windows():
        return 0
    try:
        version = platform.version()
        # Windows version format: "10.0.19041"
        parts = version.split(".")
        if len(parts) >= 3:
            return int(parts[2])
        return 0
    except (ValueError, IndexError):
        return 0


def get_cpu_name() -> str:
    """Get the CPU processor name."""
    return platform.processor() or "Unknown"


def get_python_version() -> str:
    """Get the current Python version."""
    return platform.python_version()


def get_platform_summary() -> dict[str, str]:
    """
    Get a summary of the current platform.

    Returns:
        Dict with os, version, architecture, python_version, and cpu.
    """
    return {
        "os": get_os_name(),
        "version": get_os_version(),
        "architecture": get_architecture().value,
        "python_version": get_python_version(),
        "cpu": get_cpu_name(),
        "build_number": str(get_os_build_number()),
    }
