"""
Environment service for profile management and snapshot & restore feature.
"""

from __future__ import annotations

import json
from typing import List
from uuid import UUID

from src.core.entities.environment import EnvironmentProfile, PackageSnapshot, StackDefinition
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.package_manager.plugin_manager import PluginManager


class EnvironmentService:
    """
    Manages development environment profiles, export/import JSON manifests,
    and welcome screen stack definitions.
    """

    DEFAULT_STACKS = [
        StackDefinition(
            id="python-dev",
            name="Python Development",
            description="Complete Python 3 environment with Git, VS Code, and pip package manager.",
            icon="python.svg",
            packages=[PackageId.of("python"), PackageId.of("git"), PackageId.of("vscode")],
        ),
        StackDefinition(
            id="web-dev",
            name="Web Development",
            description="Modern web stack with Node.js, npm, Git, and VS Code.",
            icon="nodejs.svg",
            packages=[PackageId.of("nodejs"), PackageId.of("git"), PackageId.of("vscode")],
        ),
        StackDefinition(
            id="ai-ml",
            name="AI / Machine Learning",
            description="AI engineering stack with Python, Git, VS Code, and Node.js.",
            icon="ai.svg",
            packages=[PackageId.of("python"), PackageId.of("git"), PackageId.of("vscode"), PackageId.of("nodejs")],
        ),
    ]

    def __init__(self, plugin_manager: PluginManager) -> None:
        self._plugin_manager = plugin_manager
        self._profiles: dict[str, EnvironmentProfile] = {}

    def get_default_stacks(self) -> List[StackDefinition]:
        """Get pre-defined development stack choices for welcome screen."""
        return self.DEFAULT_STACKS

    async def create_profile_from_installed(self, name: str, description: str = "") -> EnvironmentProfile:
        """
        Create a snapshot profile from currently installed plugins.
        """
        profile = EnvironmentProfile(name=name, description=description)
        plugins = self._plugin_manager.get_all_plugins()

        for plugin in plugins:
            ver = await plugin.get_latest_version()
            profile.add_package(plugin.metadata.id, ver)

        self._profiles[str(profile.id)] = profile
        return profile

    def export_profile_json(self, profile: EnvironmentProfile) -> str:
        """
        Export profile as JSON string manifest.
        """
        return profile.model_dump_json(indent=2)

    def import_profile_json(self, json_str: str) -> EnvironmentProfile:
        """
        Import profile from JSON string manifest.
        """
        profile = EnvironmentProfile.model_validate_json(json_str)
        self._profiles[str(profile.id)] = profile
        return profile

    def get_profiles(self) -> List[EnvironmentProfile]:
        """List user environment profiles."""
        return list(self._profiles.values())
