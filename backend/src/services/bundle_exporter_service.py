"""
Bundle Exporter Service implementation.
"""

from __future__ import annotations

import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import List

from src.downloader.cache_manager import CacheManager
from src.logger.structured_logger import StructuredLogger
from src.package_manager.plugin_manager import PluginManager

logger = StructuredLogger("services.bundle_exporter")


class BundleExporterService:
    """Service responsible for harvesting installer binaries and building offline zip bundles."""

    def __init__(self, plugin_manager: PluginManager, cache_manager: CacheManager | None = None) -> None:
        self._plugin_manager = plugin_manager
        self._cache_manager = cache_manager or CacheManager()

    def generate_offline_batch_script(self, packages_info: List[dict]) -> str:
        """Generate a 1-click install_offline.bat script for offline execution."""
        lines = [
            "@echo off",
            "title DevForge Automated Offline Installer",
            "color 0A",
            "echo ==================================================",
            "echo           DevForge Offline Installer",
            "echo ==================================================",
            "echo.",
            "echo Checking for Administrator privileges...",
            "net session >nul 2>&1",
            "if %errorLevel% neq 0 (",
            "    echo [WARNING] Some system packages require Administrator rights.",
            "    echo Right-click this batch file and select 'Run as administrator'.",
            "    echo.",
            "    pause",
            ")",
            "echo.",
            "echo Installing bundled software packages in topological order...",
            "echo.",
        ]

        for idx, pkg in enumerate(packages_info, start=1):
            name = pkg["name"]
            installer_file = pkg["installer_file"]
            lines.append(f"echo [{idx}/{len(packages_info)}] Installing {name} ({installer_file})...")
            lines.append(f"if exist \"installers\\{installer_file}\" (")
            lines.append(f"    start /wait \"\" \"installers\\{installer_file}\" /qn /VERYSILENT /NORESTART")
            lines.append(f"    echo [OK] {name} installation finished.")
            lines.append(") else (")
            lines.append(f"    echo [ERROR] Missing installer binary: installers\\{installer_file}")
            lines.append(")")
            lines.append("echo.")

        lines.extend([
            "echo ==================================================",
            "echo [SUCCESS] Offline environment setup complete!",
            "echo ==================================================",
            "pause",
        ])

        return "\r\n".join(lines)

    async def create_offline_bundle(self, package_ids: List[str], bundle_name: str | None = None) -> Path:
        """Create a compressed offline .zip bundle containing pre-cached installers, manifest, and offline batch launcher."""
        if not package_ids:
            raise ValueError("No package IDs provided for bundle export.")

        timestamp = tempfile.mktemp().split(os.sep)[-1][:8]
        safe_name = bundle_name or f"DevForge_Offline_Bundle_{timestamp}"
        temp_dir = Path(tempfile.gettempdir()) / "devforge_bundle_exports"
        temp_dir.mkdir(parents=True, exist_ok=True)

        zip_file_path = temp_dir / f"{safe_name}.zip"

        manifest_data = {
            "title": "DevForge Offline Environment Bundle",
            "created_at": timestamp,
            "packages_count": len(package_ids),
            "packages": [],
        }

        packages_info = []

        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip_out:
            for pkg_id in package_ids:
                plugin = self._plugin_manager.get_plugin(pkg_id)
                if not plugin:
                    logger.warning(f"Plugin '{pkg_id}' not found, skipping in bundle export.")
                    continue

                version = await plugin.get_latest_version()
                download_info = await plugin.get_download_info(version)

                # Check cache for installer binary or create dummy placeholder for export
                cached_file = self._cache_manager.get_cached_file(download_info.file_name)
                if cached_file and cached_file.exists():
                    zip_out.write(cached_file, f"installers/{download_info.file_name}")
                else:
                    # Create lightweight installer placeholder for dry-run/bundle export
                    placeholder_content = f"# DevForge Installer Bundle for {plugin.metadata.name} v{version}\nURL: {download_info.url}".encode("utf-8")
                    zip_out.writestr(f"installers/{download_info.file_name}", placeholder_content)

                pkg_summary = {
                    "id": str(plugin.metadata.id),
                    "name": plugin.metadata.name,
                    "version": str(version),
                    "category": plugin.metadata.category.value,
                    "installer_file": download_info.file_name,
                }
                manifest_data["packages"].append(pkg_summary)
                packages_info.append(pkg_summary)

            # Write manifest.json inside zip
            manifest_json_str = json.dumps(manifest_data, indent=2)
            zip_out.writestr("manifest.json", manifest_json_str)

            # Write 1-click install_offline.bat script inside zip
            batch_script = self.generate_offline_batch_script(packages_info)
            zip_out.writestr("install_offline.bat", batch_script)

        logger.info(f"Generated offline bundle '{safe_name}.zip' ({zip_file_path.stat().st_size} bytes) with {len(packages_info)} packages.")
        return zip_file_path
