"""
System-wide constants.

Immutable values used across the application. These are NOT
configuration (which can be overridden via env vars) — these
are fixed system constants.
"""

from __future__ import annotations

# --- Version ---
APP_VERSION = "0.1.0"
APP_NAME = "DevForge"

# --- API ---
API_V1_PREFIX = "/api/v1"
WEBSOCKET_PROGRESS_PATH = "/ws/progress"
WEBSOCKET_EVENTS_PATH = "/ws/events"

# --- Download ---
DEFAULT_CHUNK_SIZE = 8192  # 8 KB read chunk for downloads and checksums
PROGRESS_UPDATE_INTERVAL_SECONDS = 0.5  # How often to emit progress events

# --- Installation ---
INSTALL_PIPELINE_STAGES = [
    "resolving_dependencies",
    "downloading",
    "verifying_checksum",
    "extracting",
    "installing",
    "configuring_path",
    "configuring_env",
    "installing_dependencies",
    "verifying",
]

# --- Health Check ---
HEALTH_WEIGHT_BINARY_EXISTS = 25
HEALTH_WEIGHT_VERSION_MATCH = 25
HEALTH_WEIGHT_PATH_CONFIGURED = 20
HEALTH_WEIGHT_DEPS_SATISFIED = 20
HEALTH_WEIGHT_RECENT_VERIFY = 10

HEALTH_THRESHOLD_HEALTHY = 80
HEALTH_THRESHOLD_DEGRADED = 40

# --- Registry (Windows) ---
UNINSTALL_REGISTRY_PATHS = [
    (r"HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (r"HKLM", r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (r"HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]

# --- File Patterns ---
INSTALLER_EXTENSIONS = {".exe", ".msi", ".zip", ".msix"}
PROGRESS_FILE_SUFFIX = ".devforge.progress"

# --- Retry ---
MAX_RETRY_DELAY_SECONDS = 60
RETRY_JITTER_FACTOR = 0.1
