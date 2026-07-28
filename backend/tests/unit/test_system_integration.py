"""
Unit tests for System Integration and Detection Engine components.
"""

from __future__ import annotations

import pytest

from src.core.enums import Architecture, GPUVendor
from src.core.value_objects.package_id import PackageId
from src.detector.gpu_detector import DefaultGPUDetector
from src.detector.registry_scanner import RegistryScanner
from src.detector.version_detector import VersionDetector
from src.system.admin_elevation import is_admin
from src.system.process_runner import AsyncProcessRunner


@pytest.mark.asyncio
async def test_admin_elevation_check() -> None:
    # is_admin() should return a boolean without crashing
    result = is_admin()
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_async_process_runner() -> None:
    runner = AsyncProcessRunner()
    res = await runner.run(pytest.importorskip("src.core.ports.process_runner").Command(executable="cmd.exe /c echo hello"))
    assert res.success is True
    assert "hello" in res.stdout.lower()


@pytest.mark.asyncio
async def test_gpu_detector() -> None:
    detector = DefaultGPUDetector()
    gpus = await detector.detect_gpus()
    assert isinstance(gpus, list)


@pytest.mark.asyncio
async def test_version_detector() -> None:
    detector = VersionDetector()
    # Test running command that outputs version
    v = await detector.detect_version("cmd.exe /c echo 3.12.1")
    assert v is not None
    assert v.major == 3
    assert v.minor == 12
    assert v.patch == 1
