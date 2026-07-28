"""
Windows environment variables manager.
"""

from __future__ import annotations

import os

from src.logger.structured_logger import StructuredLogger
from src.system.registry_manager import WindowsRegistryAccessor

logger = StructuredLogger("system.env_vars")


class EnvironmentVarsManager:
    """
    Manages custom environment variables (e.g. JAVA_HOME, CUDA_PATH).
    """

    def __init__(self, registry: WindowsRegistryAccessor | None = None) -> None:
        self._registry = registry or WindowsRegistryAccessor()

    async def get_var(self, name: str, scope: str = "user") -> str | None:
        hive, key_path = self._get_scope_key(scope)
        val = await self._registry.get_value(hive, key_path, name)
        return str(val) if val is not None else None

    async def set_var(self, name: str, value: str, scope: str = "user") -> None:
        hive, key_path = self._get_scope_key(scope)
        await self._registry.set_value(hive, key_path, name, value, value_type="REG_SZ")
        os.environ[name] = value
        logger.info(f"Set environment variable {name}={value} ({scope})")

    async def remove_var(self, name: str, scope: str = "user") -> bool:
        # In registry, setting to empty or deleting
        hive, key_path = self._get_scope_key(scope)
        if await self._registry.get_value(hive, key_path, name) is not None:
            await self._registry.set_value(hive, key_path, name, "", value_type="REG_SZ")
            os.environ.pop(name, None)
            logger.info(f"Removed environment variable {name} ({scope})")
            return True
        return False

    def _get_scope_key(self, scope: str) -> tuple[str, str]:
        if scope.lower() == "system":
            return "HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        return "HKCU", "Environment"
