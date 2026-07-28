"""Windows System Integration package."""

from src.system.admin_elevation import is_admin, run_as_admin
from src.system.environment_vars import EnvironmentVarsManager
from src.system.path_manager import WindowsPathManager
from src.system.process_runner import AsyncProcessRunner
from src.system.registry_manager import WindowsRegistryAccessor

__all__ = [
    "AsyncProcessRunner",
    "EnvironmentVarsManager",
    "WindowsPathManager",
    "WindowsRegistryAccessor",
    "is_admin",
    "run_as_admin",
]
