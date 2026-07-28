"""
Version detector utility for extracting version from executable output.
"""

from __future__ import annotations

import re

from src.core.ports.process_runner import Command
from src.core.value_objects.version import Version
from src.system.process_runner import AsyncProcessRunner


class VersionDetector:
    """
    Runs executable commands like `python --version` or `git --version`
    and parses semantic version strings from standard output.
    """

    def __init__(self, runner: AsyncProcessRunner | None = None) -> None:
        self._runner = runner or AsyncProcessRunner()

    async def detect_version(self, command_str: str) -> Version | None:
        """
        Execute command and parse semantic version from output.
        """
        cmd = Command(executable=command_str, timeout_seconds=10)
        res = await self._runner.run(cmd)

        if not res.success and not res.stdout:
            return None

        output = f"{res.stdout}\n{res.stderr}"
        match = re.search(r"(\d+\.\d+(?:\.\d+)?)", output)
        if match:
            v_raw = match.group(1)
            if v_raw.count(".") == 1:
                v_raw += ".0"
            try:
                return Version.parse(v_raw)
            except ValueError:
                return None

        return None
