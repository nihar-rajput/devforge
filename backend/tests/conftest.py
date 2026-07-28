"""
Shared pytest fixtures for backend tests.
"""

from __future__ import annotations

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.core.entities.package import Category, Dependency, Package, PluginMetadata
from src.core.enums import PackageStatus
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.database.session import Base


@pytest_asyncio.fixture
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """In-memory SQLite async engine for unit testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Async session fixture connected to in-memory SQLite DB."""
    session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
def sample_package() -> Package:
    """Fixture returning a sample Package domain entity."""
    return Package(
        id=PackageId.of("python"),
        metadata=PluginMetadata(
            id=PackageId.of("python"),
            name="Python",
            description="Python Programming Language",
            category=Category.LANGUAGE,
            website="https://www.python.org",
        ),
        status=PackageStatus.AVAILABLE,
        latest_version=Version.parse("3.12.1"),
        dependencies=[
            Dependency(package_id=PackageId.of("git"), optional=True)
        ],
    )
