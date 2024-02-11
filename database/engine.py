from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import create_async_engine as create_async_engine_
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker

from core.config import settings

if TYPE_CHECKING:
    from sqlalchemy.engine.url import URL


def create_async_engine(url: URL | str = settings.database_url) -> AsyncEngine:
    return create_async_engine_(
        url=url,
        echo=settings.DEBUG,
        pool_size=20,
        pool_pre_ping=True
    )


async def process_schemas(engine: AsyncEngine, metadata) -> None:
    async with engine.connect() as conn:
        await conn.run_sync(metadata.create_all)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine,
                              autoflush=False,
                              class_=AsyncSession,
                              expire_on_commit=False,
                              future=True)


engine = create_async_engine(url=settings.database_url)
sessionmaker = create_sessionmaker(engine)

