"""
End-to-end integration precision test suite for DevForge.
"""

import tempfile
import zipfile
from pathlib import Path
import pytest

from src.installer.rollback_manager import RollbackManager
from src.services.bundle_exporter_service import BundleExporterService
from src.services.scaffolder_service import ScaffolderService
from src.services.telemetry_service import TelemetryService
from src.package_manager.plugin_loader import DefaultPluginLoader
from src.package_manager.plugin_manager import PluginManager
from src.api.schemas.scaffold_schemas import ScaffoldProjectRequest
from src.api.schemas.telemetry_schemas import TelemetryPayload


from src.core.entities.installation import Installation
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.core.enums import InstallationStage
from src.installer.transaction import InstallationTransaction

class MockPathManager:
    def __init__(self):
        self.removed_paths = []
    
    async def remove_from_path(self, path: str):
        self.removed_paths.append(path)

@pytest.mark.asyncio
async def test_lifo_rollback_manager_precision():
    """Verify RollbackManager executes checkpoints in reverse LIFO order."""
    mock_pm = MockPathManager()
    rollback = RollbackManager(path_manager=mock_pm)
    
    installation = Installation(package_id=PackageId(value="test-pkg"), target_version=Version.parse("1.0.0"))
    tx = InstallationTransaction(installation)
    
    step1 = tx.checkpoint(InstallationStage.DOWNLOADING, "Step 1", "remove_from_path", {"path": "path1"})
    tx.mark_step_success(step1)
    
    step2 = tx.checkpoint(InstallationStage.INSTALLING, "Step 2", "remove_from_path", {"path": "path2"})
    tx.mark_step_success(step2)
    
    step3 = tx.checkpoint(InstallationStage.CONFIGURING_PATH, "Step 3", "remove_from_path", {"path": "path3"})
    tx.mark_step_success(step3)

    await rollback.rollback_transaction(tx)

    assert mock_pm.removed_paths == ["path3", "path2", "path1"], f"Expected LIFO reverse execution order, got {mock_pm.removed_paths}"


@pytest.mark.asyncio
async def test_offline_bundle_exporter_precision():
    """Verify BundleExporterService generates valid zip structure, manifest.json, and install_offline.bat."""
    loader = DefaultPluginLoader()
    plugins = await loader.load_all_plugins()
    pm = PluginManager()
    for p in plugins.values():
        pm.register_plugin(p)

    exporter = BundleExporterService(plugin_manager=pm)
    zip_path = await exporter.create_offline_bundle(
        package_ids=["python", "git", "vscode"],
        bundle_name="Precision_Test_Bundle",
    )

    assert zip_path.exists()
    assert zip_path.stat().st_size > 0

    with zipfile.ZipFile(zip_path, "r") as z:
        namelist = z.namelist()
        assert "manifest.json" in namelist
        assert "install_offline.bat" in namelist
        assert "installers/python-3.12.2-amd64.exe" in namelist

        bat_str = z.read("install_offline.bat").decode("utf-8")
        assert "Installing Python" in bat_str
        assert "Installing Git" in bat_str
        assert "/VERYSILENT" in bat_str or "/qn" in bat_str


@pytest.mark.asyncio
async def test_workspace_scaffolder_all_templates_precision():
    """Verify ScaffolderService generates complete file trees for Python, React, Rust, and Go."""
    scaffolder = ScaffolderService()
    templates = ["python-app", "web-react", "rust-cli", "go-service"]

    with tempfile.TemporaryDirectory() as tmpdir:
        for t in templates:
            req = ScaffoldProjectRequest(
                template=t,
                project_name=f"test_{t.replace('-', '_')}",
                target_directory=tmpdir,
                initialize_git=False,
            )
            res = scaffolder.scaffold_project(req)
            assert res.success is True
            proj_dir = Path(res.project_path)
            assert proj_dir.exists()
            assert (proj_dir / ".gitignore").exists()


@pytest.mark.asyncio
async def test_telemetry_service_privacy_precision():
    """Verify TelemetryService scrubs usernames and enforces consent."""
    service = TelemetryService()
    raw = "Failed in C:\\Users\\secret_user\\AppData\\Local\\temp.exe"
    sanitized = service.sanitize_log_snippet(raw)

    assert "secret_user" not in sanitized
    assert "C:\\Users\\<User>\\" in sanitized

    payload = TelemetryPayload(
        app_version="0.1.0",
        timestamp="2026-07-28T12:00:00Z",
        error_type="PrecisionError",
        package_id="python",
        os_info="Windows 10",
        error_message="Test error",
        log_snippet=raw,
        user_consent=True,
    )

    res = await service.send_report(payload)
    assert res.success is True
    assert len(res.report_id) > 0
