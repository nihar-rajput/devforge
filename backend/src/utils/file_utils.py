"""
File utility functions.

Safe file operations with proper error handling for the
download cache, installer storage, and log management.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import aiofiles


async def safe_write_bytes(path: Path, data: bytes) -> None:
    """
    Write bytes to a file atomically.

    Writes to a temporary file first, then renames to prevent
    corrupt files from partial writes on crash.

    Args:
        path: Target file path.
        data: Bytes to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(data)
        temp_path.replace(path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


async def safe_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Write text to a file atomically.

    Args:
        path: Target file path.
        content: Text content to write.
        encoding: Text encoding.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        async with aiofiles.open(temp_path, "w", encoding=encoding) as f:
            await f.write(content)
        temp_path.replace(path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


async def safe_read_text(path: Path, encoding: str = "utf-8") -> str | None:
    """
    Read text from a file, returning None if it doesn't exist.

    Args:
        path: File path.
        encoding: Text encoding.

    Returns:
        File contents, or None if the file doesn't exist.
    """
    if not path.exists():
        return None
    async with aiofiles.open(path, "r", encoding=encoding) as f:
        return await f.read()


def safe_delete(path: Path) -> bool:
    """
    Delete a file or directory safely.

    Args:
        path: Path to delete.

    Returns:
        True if something was deleted, False if it didn't exist.
    """
    if not path.exists():
        return False
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink(missing_ok=True)
    return True


def get_directory_size(path: Path) -> int:
    """
    Calculate total size of a directory in bytes.

    Args:
        path: Directory path.

    Returns:
        Total size in bytes. 0 if directory doesn't exist.
    """
    if not path.exists() or not path.is_dir():
        return 0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def ensure_directory(path: Path) -> Path:
    """
    Create a directory if it doesn't exist.

    Args:
        path: Directory path.

    Returns:
        The directory path (for chaining).
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
