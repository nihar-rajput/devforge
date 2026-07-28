"""
Unit tests for InstallationEngine, Transactions, and RollbackManager.
"""

from __future__ import annotations

import pytest

from src.core.entities.installation import Installation
from src.core.enums import InstallationStage
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.installer.transaction import InstallationTransaction


def test_installation_transaction_checkpoints() -> None:
    inst = Installation(
        package_id=PackageId.of("python"),
        target_version=Version.parse("3.12.1"),
    )
    tx = InstallationTransaction(inst)

    step1 = tx.checkpoint(InstallationStage.DOWNLOADING, "Downloading file...")
    tx.mark_step_success(step1)

    step2 = tx.checkpoint(InstallationStage.CONFIGURING_PATH, "Updating PATH...", rollback_command="remove_from_path")
    tx.mark_step_success(step2)

    completed = tx.completed_checkpoints
    assert len(completed) == 2
    # LIFO order
    assert completed[0].stage == InstallationStage.CONFIGURING_PATH
    assert completed[1].stage == InstallationStage.DOWNLOADING
