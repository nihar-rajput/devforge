# DevForge Plugin Development Guide

This guide explains how to create, test, and package custom software plugins for DevForge.

## Core Philosophy

Every software package managed by DevForge is represented by a single Python plugin class implementing the `BasePlugin` abstract interface.

Adding support for a new tool (e.g. `Rust`, `Docker`, `PostgreSQL`) requires **only creating a new plugin file** in `src/plugins/`. Zero modification to the core installation engine is needed.

---

## Anatomy of a Plugin

Each plugin must extend `BasePlugin` and implement these key sections:

```python
from src.package_manager.base_plugin import BasePlugin, InstallOptions
from src.core.entities.package import PluginMetadata, DownloadInfo, Dependency
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.core.enums import Category, InstallerType

class MyToolPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("my-tool"),
            name="My Developer Tool",
            description="Short tool description",
            category=Category.UTILITY,
        )

    async def get_latest_version(self) -> Version:
        return Version.parse("1.0.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://example.com/installer.exe",
            file_name="installer.exe",
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path, options: InstallOptions):
        return Command(
            executable=str(installer_path),
            args=["/quiet", "/norestart"],
            requires_admin=self.requires_admin,
        )
```

---

## Quick Scaffolding Command

Generate a new plugin boilerplate using the CLI script:

```bash
python scripts/create_plugin.py my-tool --name "My Tool" --category language
```

This generates `src/plugins/my_tool_plugin.py`.

---

## Testing Your Plugin

Run unit tests on the plugin manager:

```bash
pytest tests/unit/test_plugin_manager.py -v
```

DevForge automatically discovers all `.py` files in `src/plugins/` upon application startup.
