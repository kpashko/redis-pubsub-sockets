import asyncio
import logging
from typing import AsyncGenerator
from unittest.mock import patch

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from fakeredis import FakeRedis as FakeSyncRedis
from fakeredis.aioredis import FakeRedis
from httpx import AsyncClient
from rq import Queue
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_async_session
from app.main import app
from app.models.base import Base
from app.settings import settings

database_url = settings.sqlalchemy_async_engine_url
async_test_engine = create_async_engine(
    database_url.unicode_string(), echo=True, future=True
)

TestingSessionLocal = async_sessionmaker(
    bind=async_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

pytest_plugins = (
    "tests.fixtures.entities",
    "tests.fixtures.models",
)


@pytest.fixture(autouse=True)
def suppress_sqlalchemy_logs():
    """Suppresses SQLAlchemy logs during tests."""
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


@pytest.fixture(scope="session")
def event_loop():
    """Create a new event loop for the entire session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def run_test_migrations():
    """Run migrations on test database connection."""
    cfg = Config("alembic.ini")
    async with async_test_engine.begin() as connection:
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """Fixture that sets up the database schema before running tests."""
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def client(setup_database) -> AsyncGenerator[AsyncClient, None]:
    """Yields a httpx test client."""

    async def _override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    # Override dependency
    app.dependency_overrides[get_async_session] = _override_get_async_session
    async with AsyncClient(app=app, base_url="http://testserver") as test_client:
        yield test_client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_database():
    """Fixture that runs migrations before tests start."""
    await run_test_migrations()


@pytest_asyncio.fixture(scope="session")
async def fake_redis() -> FakeRedis:
    """Provides a fake Redis instance for testing."""
    return FakeRedis(decode_responses=True)


@pytest_asyncio.fixture(autouse=True)
async def patch_redis(fake_redis):
    """Patches the Redis client to use the fake Redis instance during tests."""
    with patch("app.redis.get_redis", return_value=fake_redis):
        yield


@pytest_asyncio.fixture(scope="session")
async def fake_sync_redis():
    """Provides a fake synchronous Redis instance for testing."""
    return FakeSyncRedis(decode_responses=False)


@pytest_asyncio.fixture(autouse=True)
async def patch_sync_redis(fake_sync_redis):
    """Patches the synchronous Redis connection and queue for testing."""
    with patch("app.redis.get_sync_redis", return_value=fake_sync_redis):
        # Patch the queue to use the fake Redis connection
        with patch(
            "app.redis.get_task_queue",
            return_value=Queue("test_queue", connection=fake_sync_redis),
        ):
            yield
