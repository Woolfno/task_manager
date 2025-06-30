from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

engine = create_async_engine(get_settings().DATABASE_URL)
session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with session() as s:
        yield s


class Base(AsyncAttrs, DeclarativeBase):
    pass
