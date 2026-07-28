"""
Unit tests for SQLite concrete repository implementations.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.installation import Installation
from src.core.entities.package import Package
from src.core.enums import Category, InstallationStage, PackageStatus
from src.core.events.download_events import DownloadStarted
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.database.repositories.sqlite_event_log_repo import SqliteEventLogRepository
from src.database.repositories.sqlite_installation_repo import SqliteInstallationRepository
from src.database.repositories.sqlite_package_repo import SqlitePackageRepository


@pytest.mark.asyncio
async def test_sqlite_package_repository_crud(
    db_session: AsyncSession,
    sample_package: Package,
) -> None:
    repo = SqlitePackageRepository(db_session)

    # Initially empty
    all_packages = await repo.get_all()
    assert len(all_packages) == 0

    # Save package
    await repo.save(sample_package)

    # Get by ID
    retrieved = await repo.get_by_id(sample_package.id)
    assert retrieved is not None
    assert retrieved.id == sample_package.id
    assert retrieved.metadata.name == "Python"
    assert retrieved.metadata.category == Category.LANGUAGE
    assert len(retrieved.dependencies) == 1
    assert retrieved.dependencies[0].package_id == PackageId.of("git")

    # Update status
    retrieved.mark_installed(Version.parse("3.12.1"), install_path=retrieved.install_path or pytest.importorskip("pathlib").Path("C:/Python312"))
    await repo.save(retrieved)

    installed_packages = await repo.get_installed()
    assert len(installed_packages) == 1
    assert installed_packages[0].status == PackageStatus.INSTALLED

    # Search
    search_results = await repo.search("Pyth")
    assert len(search_results) == 1

    # Count
    count = await repo.count()
    assert count == 1

    # Delete
    await repo.delete(sample_package.id)
    assert await repo.get_by_id(sample_package.id) is None


@pytest.mark.asyncio
async def test_sqlite_installation_repository_crud(
    db_session: AsyncSession,
) -> None:
    repo = SqliteInstallationRepository(db_session)

    installation = Installation(
        package_id=PackageId.of("vscode"),
        target_version=Version.parse("1.85.0"),
    )
    installation.add_step(InstallationStage.DOWNLOADING, "Downloading installer...")

    await repo.save(installation)

    retrieved = await repo.get_by_id(installation.id)
    assert retrieved is not None
    assert retrieved.package_id == PackageId.of("vscode")
    assert len(retrieved.steps) == 1
    assert retrieved.steps[0].stage == InstallationStage.DOWNLOADING

    active = await repo.get_active()
    assert len(active) == 1
    assert active[0].id == installation.id

    installation.complete()
    await repo.save(installation)

    active_after = await repo.get_active()
    assert len(active_after) == 0


@pytest.mark.asyncio
async def test_sqlite_event_log_repository(
    db_session: AsyncSession,
) -> None:
    repo = SqliteEventLogRepository(db_session)

    event = DownloadStarted(
        package_id=PackageId.of("git"),
        download_id=pytest.importorskip("uuid").uuid4(),
        url="https://git-scm.com/download/win",
        file_name="Git-installer.exe",
    )

    await repo.save_event(event)

    recent = await repo.get_recent(limit=10)
    assert len(recent) == 1
    assert recent[0].event_type == "DownloadStarted"
    assert recent[0].message == "Download started"
