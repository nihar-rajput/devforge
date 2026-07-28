"""Installation-related errors."""

from __future__ import annotations

from src.core.enums import InstallationStage
from src.core.errors.base import DevForgeError
from src.core.value_objects.package_id import PackageId


class InstallationError(DevForgeError):
    """Base error for installation failures."""

    def __init__(
        self,
        message: str,
        *,
        package_id: PackageId | None = None,
        stage: InstallationStage | None = None,
        details: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        self.package_id = package_id
        self.stage = stage
        super().__init__(message, details=details, cause=cause)


class InstallerExecutionError(InstallationError):
    """Raised when the installer process exits with a non-zero code."""

    def __init__(
        self,
        package_id: PackageId,
        return_code: int,
        stderr: str,
    ) -> None:
        self.return_code = return_code
        self.stderr = stderr
        super().__init__(
            f"Installer for '{package_id}' exited with code {return_code}",
            package_id=package_id,
            stage=InstallationStage.INSTALLING,
            details=stderr[:500] if stderr else None,
        )


class RollbackError(InstallationError):
    """Raised when a rollback operation fails."""

    def __init__(
        self,
        package_id: PackageId,
        original_error: str,
        rollback_error: str,
    ) -> None:
        self.original_error = original_error
        self.rollback_error = rollback_error
        super().__init__(
            f"Rollback failed for '{package_id}'",
            package_id=package_id,
            details=f"Original: {original_error} | Rollback: {rollback_error}",
        )


class UninstallationError(InstallationError):
    """Raised when uninstallation fails."""

    def __init__(
        self,
        package_id: PackageId,
        reason: str,
    ) -> None:
        super().__init__(
            f"Failed to uninstall '{package_id}': {reason}",
            package_id=package_id,
        )
