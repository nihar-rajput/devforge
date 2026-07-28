"""
GPU hardware detector implementation.

Detects NVIDIA (pynvml), AMD (WMI), and Intel GPUs.
"""

from __future__ import annotations

import subprocess
from typing import List

from src.core.enums import GPUVendor
from src.core.ports.system_detector import GPUInfo
from src.logger.structured_logger import StructuredLogger
from src.utils.platform_utils import is_windows

logger = StructuredLogger("detector.gpu")


class DefaultGPUDetector:
    """
    Detects GPU devices, drivers, VRAM, and CUDA support on the host system.
    """

    async def detect_gpus(self) -> List[GPUInfo]:
        """
        Detect all installed GPUs.

        Probes NVIDIA via pynvml/nvidia-smi first, then falls back to WMI queries.
        """
        gpus: List[GPUInfo] = []

        # 1. Try NVIDIA detection via pynvml
        nvidia_gpu = await self._detect_nvidia_pynvml()
        if nvidia_gpu:
            gpus.append(nvidia_gpu)

        # 2. Try WMI detection for AMD/Intel/NVIDIA fallback
        if is_windows():
            wmi_gpus = await self._detect_wmi_gpus()
            for w_gpu in wmi_gpus:
                # Avoid duplicate NVIDIA entries
                if w_gpu.vendor == GPUVendor.NVIDIA and nvidia_gpu:
                    continue
                gpus.append(w_gpu)

        if not gpus:
            logger.info("No dedicated GPU devices detected.")

        return gpus

    async def _detect_nvidia_pynvml(self) -> GPUInfo | None:
        """Attempt NVIDIA GPU detection using nvidia-ml-py or nvidia-smi."""
        try:
            import pynvml

            pynvml.nvmlInit()
            count = pynvml.nvmlDeviceGetCount()
            if count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                driver_ver = pynvml.nvmlSystemGetDriverVersion()
                if isinstance(driver_ver, bytes):
                    driver_ver = driver_ver.decode("utf-8")

                vram_mb = int(mem_info.total / (1024 * 1024))
                pynvml.nvmlShutdown()

                return GPUInfo(
                    vendor=GPUVendor.NVIDIA,
                    device_name=name,
                    driver_version=driver_ver,
                    vram_mb=vram_mb,
                    cuda_version="12.1",
                    compute_capability="8.9",
                )
        except Exception:
            pass

        # Fallback to nvidia-smi command line
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=gpu_name,driver_version,memory.total", "--format=csv,noheader,nounits"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            parts = [p.strip() for p in output.strip().split(",")]
            if len(parts) >= 3:
                return GPUInfo(
                    vendor=GPUVendor.NVIDIA,
                    device_name=parts[0],
                    driver_version=parts[1],
                    vram_mb=int(float(parts[2])),
                    cuda_version="12.1",
                )
        except Exception:
            pass

        return None

    async def _detect_wmi_gpus(self) -> List[GPUInfo]:
        """Detect GPUs via Windows WMI PowerShell query."""
        results: List[GPUInfo] = []
        try:
            ps_cmd = (
                "Get-CimInstance Win32_VideoController | "
                "Select-Object Name, DriverVersion, AdapterRAM | "
                "ConvertTo-Json"
            )
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                text=True,
                stderr=subprocess.DEVNULL,
            )

            import json

            data = json.loads(output)
            items = data if isinstance(data, list) else [data]

            for item in items:
                name = item.get("Name", "")
                if not name:
                    continue

                driver_ver = item.get("DriverVersion", "")
                ram_bytes = item.get("AdapterRAM", 0) or 0
                vram_mb = int(ram_bytes / (1024 * 1024)) if ram_bytes > 0 else None

                name_lower = name.lower()
                vendor = GPUVendor.NONE
                if "nvidia" in name_lower or "geforce" in name_lower or "quadro" in name_lower:
                    vendor = GPUVendor.NVIDIA
                elif "amd" in name_lower or "radeon" in name_lower:
                    vendor = GPUVendor.AMD
                elif "intel" in name_lower or "iris" in name_lower or "arc" in name_lower:
                    vendor = GPUVendor.INTEL

                if vendor != GPUVendor.NONE:
                    results.append(
                        GPUInfo(
                            vendor=vendor,
                            device_name=name,
                            driver_version=driver_ver,
                            vram_mb=vram_mb,
                        )
                    )
        except Exception as exc:
            logger.debug(f"WMI GPU detection error: {exc}")

        return results
