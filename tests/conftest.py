# tests/conftest.py
import pytest_asyncio

from app.db.base import Base
from app.db.session import engine
import app.db.models  # noqa: F401  -- ensures all tables are registered on Base.metadata


@pytest_asyncio.fixture(autouse=True)
async def _setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Critical: drop pooled asyncpg connections so the next test's
    # (new) event loop doesn't reuse a connection bound to this one.
    await engine.dispose()