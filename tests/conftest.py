from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from alembic import command, config
from httpx import AsyncClient
from httpx_ws.transport import ASGIWebSocketTransport
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import NullPool

from app.api.schemas.user import UserIn
from app.core.config import Settings, get_settings
from app.core.security import create_access_token, get_password_hash
from app.db import models
from app.db.database import get_session
from main import app


def override_settings():
    class TestSettings(Settings):
        model_config = SettingsConfigDict(env_file='./test/.env')
    return TestSettings()  # type: ignore


app.dependency_overrides[get_settings] = override_settings

app_cfg = override_settings()
DATABASE_URL = f"postgresql+asyncpg://{app_cfg.DB_USER}:{app_cfg.DB_PASSWORD}@{app_cfg.DB_HOST}:{app_cfg.DB_PORT}/{app_cfg.DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)


@pytest_asyncio.fixture(scope="session")
async def async_db_engine():
    alembic_cfg = config.Config('./alembic.ini')
    async with engine.begin() as conn:
        alembic_cfg.attributes['connection'] = conn
        command.upgrade(alembic_cfg, "head")

    yield engine

    async with engine.begin() as conn:
        alembic_cfg.attributes['connection'] = conn
        command.downgrade(alembic_cfg, "base")


@pytest_asyncio.fixture(scope="function", autouse=True)
async def client(session):
    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    async with AsyncClient(transport=ASGIWebSocketTransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def session(async_db_engine):
    async_session = async_sessionmaker(async_db_engine,
                                       expire_on_commit=False,
                                       autoflush=False,
                                       autocommit=False)

    async with async_session() as session:
        await session.begin()
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def task(session: AsyncSession) -> AsyncGenerator[models.Task, Any]:
    t = models.Task(title="title", description="test task",
                    status=models.Status.OPEN)
    session.add(t)
    await session.commit()
    yield t

    await session.delete(t)
    await session.commit()


@pytest_asyncio.fixture(scope='function')
async def user(session: AsyncSession) -> AsyncGenerator[UserIn, Any]:
    u = UserIn(username='test_user', password='123')
    user = models.User(username=u.username,
                       password=get_password_hash(u.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    yield u
    await session.delete(user)
    await session.commit()


@pytest.fixture
def access_token(user: UserIn) -> str:
    return create_access_token(data={'sub': user.username})
