from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.settings import settings

async_engine = create_async_engine(
    settings.sqlalchemy_async_engine_url.unicode_string(), future=True
)

AsyncSession = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    bind=async_engine,
    class_=AsyncSessionType,
)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSessionType, None]:
    """
    Asynchronous SQLAlchemy session context manager for
    declarative session connecting in service-level code.
    """
    session = AsyncSession()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
