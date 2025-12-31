import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.settings import settings
from src.infrastructure.db.models.base import Base
from src.main import app

TEST_DATABASE_URL = settings.TEST_DATABASE_URL.get_secret_value()

@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create an async engine for tests."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    yield engine

    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def session(db_engine):
    """Create an async session for tests."""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
def app_fixture():
    """Create a fixture for app."""
    app.dependency_overrides = {}
    return app
