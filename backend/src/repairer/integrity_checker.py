"""
Integrity checker implementation.
"""

from __future__ import annotations

from src.package_manager.base_plugin import BasePlugin
from src.system.process_runner import AsyncProcessRunner


class IntegrityChecker:
    """
    Checks package installation integrity by running verification commands.
    """

    def __init__(self, runner: AsyncProcessRunner | None = None) -> None:
        self._runner = runner or AsyncProcessRunner()

    async def verify_plugin(self, plugin: BasePlugin) -> list[str]:
        """
        Run verification commands for plugin.

        Returns:
            List of failed verification command descriptions.
        """
        failed: list[str] = []
        cmds = plugin.get_verify_commands()

        for v_cmd in cmds:
            ok = await self._runner.verify_installation(v_cmd)
            if not ok:
                failed.append(v_cmd.command)

        return failed
