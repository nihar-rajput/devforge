"""
SystemRequirements value object.

Defines hardware and OS requirements for a package, used by the
dependency resolver and detection engine to check compatibility.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.core.enums import Architecture, GPUVendor
from src.core.value_objects.file_size import FileSize


class SystemRequirements(BaseModel):
    """
    Hardware and OS requirements for a package.

    Used during pre-install checks to verify the system can
    support the package before downloading.

    Examples:
        - CUDA Toolkit requires NVIDIA GPU + specific driver version
        - Docker Desktop requires Hyper-V / WSL2
        - Most packages just need disk space
    """

    model_config = {"frozen": True}

    min_disk_space: FileSize = Field(
        default_factory=FileSize.zero,
        description="Minimum free disk space required.",
    )
    min_ram_mb: int = Field(
        default=0,
        ge=0,
        description="Minimum RAM in megabytes.",
    )
    supported_architectures: list[Architecture] = Field(
        default_factory=lambda: [Architecture.X86_64, Architecture.ARM64],
        description="CPU architectures this package supports.",
    )
    requires_gpu: bool = Field(
        default=False,
        description="Whether a GPU is required.",
    )
    required_gpu_vendors: list[GPUVendor] = Field(
        default_factory=list,
        description="Specific GPU vendors required (e.g., NVIDIA for CUDA).",
    )
    min_gpu_vram_mb: int = Field(
        default=0,
        ge=0,
        description="Minimum GPU VRAM in megabytes.",
    )
    requires_admin: bool = Field(
        default=False,
        description="Whether administrator privileges are needed.",
    )
    requires_reboot: bool = Field(
        default=False,
        description="Whether a system reboot is needed after installation.",
    )
    requires_wsl: bool = Field(
        default=False,
        description="Whether WSL (Windows Subsystem for Linux) is required.",
    )
    requires_hyperv: bool = Field(
        default=False,
        description="Whether Hyper-V is required.",
    )
    min_windows_build: int | None = Field(
        default=None,
        description="Minimum Windows build number (e.g., 19041 for Windows 10 2004).",
    )
    additional_notes: str | None = Field(
        default=None,
        description="Human-readable notes about requirements.",
    )

    def is_gpu_compatible(self, detected_vendor: GPUVendor) -> bool:
        """Check if the detected GPU vendor satisfies the requirement."""
        if not self.requires_gpu:
            return True
        if not self.required_gpu_vendors:
            return detected_vendor != GPUVendor.NONE
        return detected_vendor in self.required_gpu_vendors
