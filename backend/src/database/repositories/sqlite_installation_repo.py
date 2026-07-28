"""
SQLite implementation of InstallationRepository port interface.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.installation import Installation
from src.core.enums import InstallationStage
from src.core.ports.installation_repository import InstallationRepository
from src.core.value_objects.package_id import PackageId
from src.database.models.installation_model import InstallationModel


class SqliteInstallationRepository(InstallationRepository):
    """
    Concrete SQLite repository implementing InstallationRepository interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, installation_id: UUID) -> Installation | None:
        stmt = select(InstallationModel).where(InstallationModel.id == str(installation_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_package(self, package_id: PackageId) -> list[Installation]:
        stmt = (
            select(InstallationModel)
            .where(InstallationModel.package_id == package_id.value)
            .order_by(InstallationModel.started_at.desc())
        )
        result = await self._session.execute(stmt)
        models: Sequence[InstallationModel] = result.scalars().all()
        return [model.to_domain() for model in models]

    async def get_active(self) -> list[Installation]:
        completed_stages = [
            InstallationStage.COMPLETED.value,
            InstallationStage.FAILED.value,
            InstallationStage.ROLLED_BACK.value,
        ]
        stmt = (
            select(InstallationModel)
            .where(InstallationModel.current_stage.notin_(completed_stages))
            .order_by(InstallationModel.started_at.asc())
        )
        result = await self._session.execute(stmt)
        models: Sequence[InstallationModel] = result.scalars().all()
        return [model.to_domain() for model in models]

    async def get_recent(self, limit: int = 50) -> list[Installation]:
        stmt = (
            select(InstallationModel)
            .order_by(InstallationModel.started_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models: Sequence[InstallationModel] = result.scalars().all()
        return [model.to_domain() for model in models]

    async def save(self, installation: Installation) -> None:
        model = InstallationModel.from_domain(installation)
        await self._session.merge(model)
        await self._session.commit()

    async def delete_older_than_days(self, days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = delete(InstallationModel).where(InstallationModel.started_at < cutoff)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount or 0
