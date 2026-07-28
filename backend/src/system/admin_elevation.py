"""
UAC Administrator elevation utilities for Windows.
"""

from __future__ import annotations

import ctypes
import sys
from typing import Tuple

from src.utils.platform_utils import is_windows


def is_admin() -> bool:
    """
    Check if the current process is running with administrator privileges.

    Returns:
        True if running as admin / elevated on Windows, or True on non-Windows.
    """
    if not is_windows():
        return True
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


async def run_as_admin(executable: str, args: list[str]) -> Tuple[int, str]:
    """
    Relaunch a command with administrator elevation using ShellExecuteW ('runas').

    Args:
        executable: Executable path or command name.
        args: Arguments list.

    Returns:
        Tuple of (exit_code, output_message).
    """
    if not is_windows():
        return 0, "Non-Windows platform"

    params = " ".join(args)
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        params,
        None,
        1,  # SW_SHOWNORMAL
    )

    # ShellExecuteW returns > 32 on success
    if ret > 32:
        return 0, "Elevated process launched successfully."
    else:
        return int(ret), f"ShellExecuteW failed with error code {ret}"
