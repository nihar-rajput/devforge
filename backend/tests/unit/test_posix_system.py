"""
Unit tests for PosixPathManager, PosixSoftwareDetector, and SystemFactory.
"""

import tempfile
from pathlib import Path
import pytest

from src.detector.posix_detector import PosixSoftwareDetector
from src.system.posix_path_manager import PosixPathManager
from src.system.system_factory import SystemFactory


def test_posix_path_manager_add_and_remove():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("# bashrc header\n", encoding="utf-8")

        mgr = PosixPathManager(home_dir=tmp_path)
        test_entry = Path("/usr/local/devforge/bin")

        added = mgr.add_to_path(test_entry)
        assert added is True
        assert "/usr/local/devforge/bin" in rc_file.read_text(encoding="utf-8")

        # Adding duplicate should return False
        added_again = mgr.add_to_path(test_entry)
        assert added_again is False

        # Removing entry
        removed = mgr.remove_from_path(test_entry)
        assert removed is True
        assert "/usr/local/devforge/bin" not in rc_file.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_posix_detector_info():
    detector = PosixSoftwareDetector()
    info = await detector.get_system_info()

    assert info.os_name is not None
    assert info.cpu_cores >= 1
    assert info.available_disk_gb >= 0.0


def test_system_factory_dispatch():
    path_mgr = SystemFactory.get_path_manager()
    detector = SystemFactory.get_system_detector()

    assert path_mgr is not None
    assert detector is not None
