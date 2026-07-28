"""
POSIX Path Manager implementation for macOS and Linux.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List

from src.core.ports.path_manager import PathManager
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("system.posix_path")


class PosixPathManager(PathManager):
    """PathManager implementation for POSIX systems (macOS and Linux)."""

    def __init__(self, home_dir: Path | None = None) -> None:
        self._home_dir = home_dir or Path.home()

    def get_user_path(self) -> List[Path]:
        """Get list of paths from PATH environment variable."""
        raw_path = os.environ.get("PATH", "")
        return [Path(p) for p in raw_path.split(":") if p.strip()]

    def get_system_path(self) -> List[Path]:
        """Get list of system paths."""
        return self.get_user_path()

    def add_to_path(self, entry: Path, user_scope: bool = True) -> bool:
        """Add an entry to user's shell rc file (~/.zshrc or ~/.bashrc)."""
        entry_str = entry.as_posix()
        rc_file = self._home_dir / ".zshrc" if (self._home_dir / ".zshrc").exists() else self._home_dir / ".bashrc"

        export_line = f'export PATH="{entry_str}:$PATH"\n'

        if rc_file.exists():
            content = rc_file.read_text(encoding="utf-8")
            if entry_str in content:
                logger.info(f"Path '{entry_str}' already present in '{rc_file.name}'.")
                return False

        with open(rc_file, "a", encoding="utf-8") as f:
            f.write(f"\n# Added by DevForge\n{export_line}")

        logger.info(f"Added '{entry_str}' to '{rc_file.name}'.")
        return True

    def remove_from_path(self, entry: Path, user_scope: bool = True) -> bool:
        """Remove an entry from shell rc file."""
        entry_str = entry.as_posix()
        rc_files = [self._home_dir / ".zshrc", self._home_dir / ".bashrc", self._home_dir / ".profile"]

        removed_any = False
        for rc_file in rc_files:
            if not rc_file.exists():
                continue
            lines = rc_file.read_text(encoding="utf-8").splitlines()
            new_lines = [l for l in lines if entry_str not in l and "# Added by DevForge" not in l]

            if len(new_lines) != len(lines):
                rc_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                removed_any = True
                logger.info(f"Removed '{entry_str}' from '{rc_file.name}'.")

        return removed_any

    def backup_path(self) -> Path:
        """Create a backup of the primary shell rc file."""
        rc_file = self._home_dir / ".zshrc" if (self._home_dir / ".zshrc").exists() else self._home_dir / ".bashrc"
        backup_file = self._home_dir / f"{rc_file.name}.devforge_bak"
        if rc_file.exists():
            shutil.copy(rc_file, backup_file)
        return backup_file

    def restore_path(self, backup_file: Path) -> bool:
        """Restore shell rc file from backup."""
        if backup_file.exists():
            rc_name = backup_file.name.replace(".devforge_bak", "")
            target_rc = self._home_dir / rc_name
            shutil.copy(backup_file, target_rc)
            return True
        return False

    def find_conflicts(self, entry: Path) -> List[Path]:
        """Find duplicate entries in user PATH."""
        entry_str = str(entry).lower()
        return [p for p in self.get_user_path() if str(p).lower() == entry_str]

    def broadcast_change(self) -> None:
        """No-op on POSIX systems (shell sources config on startup)."""
        pass
