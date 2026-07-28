"""
SQLite implementation of PackageRepository port interface.
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.package import Package
from src.core.enums import Category, PackageStatus
from src.core.ports.package_repository import PackageRepository
from src.core.value_objects.package_id import PackageId
from src.database.models.package_model import PackageModel


class SqlitePackageRepository(PackageRepository):
    """
    Concrete SQLite repository implementing PackageRepository interface.
    Uses async SQLAlchemy session for non-blocking I/O.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, package_id: PackageId) -> Package | None:
        stmt = select(PackageModel).where(PackageModel.id == package_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_all(self) -> list[Package]:
        stmt = select(PackageModel).order_by(PackageModel.name)
        result = await self._session.execute(stmt)
        models: Sequence[PackageModel] = result.scalars().all()
        return [model.to_domain() for model in models]

    async def get_by_status(self, status: PackageStatus) -> list[Package]:
        stmt = (
            select(PackageModel)
            .where(PackageModel.status == status.value)
            .order_by(PackageModel.name)
        )
        result = await self._session.execute(stmt)
        models: Sequence[PackageModel] = result.scalars().all()
        return [model.to_domain() for model in models]

    async def get_by_category(self, category: Category) -> list[Package]:
        stmt = (
            select(PackageModel)
            .where(PackageModel.category == category.value)
            .order_by(PackageModel.name)
        )
        result = await self._session.execute(stmt)
        models: Sequence[PackageModel] = result.scalars().all()
        return [model.to_domain() for model in models]

    async def get_installed(self) -> list[Package]:
        installed_statuses = [
            PackageStatus.INSTALLED.value,
            PackageStatus.BROKEN.value,
            PackageStatus.UPDATING.value,
            PackageStatus.REPAIRING.value,
        ]
        stmt = (
            select(PackageModel)
            .where(PackageModel.status.in_(installed_statuses))
            .order_by(PackageModel.name)
        )
        result = await self._session.execute(stmt)
        models: Sequence[PackageModel] = result.scalars().all()
        return [model.to_domain() for model in models]

    async def save(self, package: Package) -> None:
        model = PackageModel.from_domain(package)
        merged_model = await self._session.merge(model)
        await self._session.commit()

    async def delete(self, package_id: PackageId) -> None:
        stmt = delete(PackageModel).where(PackageModel.id == package_id.value)
        await self._session.execute(stmt)
        await self._session.commit()

    async def search(self, query: str) -> list[Package]:
        search_pattern = f"%{query}%"
        stmt = (
            select(PackageModel)
            .where(
                (PackageModel.name.ilike(search_pattern))
                | (PackageModel.description.ilike(search_pattern))
                | (PackageModel.id.ilike(search_pattern))
            )
            .order_by(PackageModel.name)
        )
        result = await self._session.execute(stmt)
        models: Sequence[PackageModel] = result.scalars().all()
        return [model.to_domain() for model in models]

    async def count(self, status: PackageStatus | None = None) -> int:
        stmt = select(func.count(PackageModel.id))
        if status:
            stmt = stmt.where(PackageModel.status == status.value)
        result = await self._session.execute(stmt)
        return result.scalar_one() or 0
