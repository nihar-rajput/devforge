"""
Application settings.

Centralized configuration using Pydantic BaseSettings.
Values are loaded from environment variables with fallback to defaults.
Hierarchy: defaults → .env file → environment variables → CLI overrides.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    model_config = SettingsConfigDict(env_prefix="DEVFORGE_")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./devforge.db",
        description="SQLAlchemy async database URL.",
    )


class ServerSettings(BaseSettings):
    """HTTP server settings."""

    model_config = SettingsConfigDict(env_prefix="DEVFORGE_")

    host: str = Field(default="127.0.0.1", description="Server bind address.")
    port: int = Field(default=8000, ge=1024, le=65535, description="Server port.")


class DownloadSettings(BaseSettings):
    """Download manager settings."""

    model_config = SettingsConfigDict(env_prefix="DEVFORGE_DOWNLOAD_")

    max_concurrent_downloads: int = Field(
        default=3, ge=1, le=10, description="Maximum parallel downloads."
    )
    segment_count: int = Field(
        default=4, ge=1, le=16, description="Segments per file for parallel download."
    )
    segment_threshold_mb: int = Field(
        default=50, ge=1, description="Minimum file size (MB) to trigger segmented download."
    )
    timeout_seconds: int = Field(
        default=300, ge=30, description="Per-download timeout."
    )
    retry_max: int = Field(
        default=3, ge=0, le=10, description="Maximum retry attempts."
    )
    retry_base_delay: float = Field(
        default=1.0, ge=0.1, description="Base delay for exponential backoff (seconds)."
    )


class InstallSettings(BaseSettings):
    """Installation engine settings."""

    model_config = SettingsConfigDict(env_prefix="DEVFORGE_INSTALL_")

    timeout_seconds: int = Field(
        default=600, ge=60, description="Per-installation timeout."
    )
    max_concurrent_installs: int = Field(
        default=1, ge=1, le=3, description="Maximum parallel installations."
    )


class PathSettings(BaseSettings):
    """File path settings."""

    model_config = SettingsConfigDict(env_prefix="DEVFORGE_")

    cache_dir: Path = Field(
        default=Path("./cache"), description="Download cache directory."
    )
    download_dir: Path = Field(
        default=Path("./downloads"), description="Active download directory."
    )
    log_dir: Path = Field(
        default=Path("./logs"), description="Log file directory."
    )
    plugin_dir: Path = Field(
        default=Path("./src/plugins"), description="Plugin directory."
    )


class AppSettings(BaseSettings):
    """
    Root application settings.

    Composes all setting groups into a single injectable object.
    Load via: `settings = AppSettings()`
    """

    model_config = SettingsConfigDict(
        env_prefix="DEVFORGE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="DevForge", description="Application name.")
    app_version: str = Field(default="0.1.0", description="Application version.")
    debug: bool = Field(default=False, description="Enable debug mode.")
    log_level: str = Field(default="INFO", description="Logging level.")

    # Composed settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    download: DownloadSettings = Field(default_factory=DownloadSettings)
    install: InstallSettings = Field(default_factory=InstallSettings)
    paths: PathSettings = Field(default_factory=PathSettings)

    def ensure_directories(self) -> None:
        """Create all configured directories if they don't exist."""
        for dir_path in [
            self.paths.cache_dir,
            self.paths.download_dir,
            self.paths.log_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
