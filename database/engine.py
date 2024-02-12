from __future__ import annotations
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine as create_async_engine_
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker

from core.config import settings

if TYPE_CHECKING:
    from sqlalchemy.engine.url import URL


def create_async_engine(url: URL | str = settings.database_url) -> AsyncEngine:
    logger.info(f"Starting Postgre async engine")
    return create_async_engine_(
        url=url,
        echo=settings.DEBUG,
        pool_size=20,
        pool_pre_ping=True
    )


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    logger.success(f"Engine started successfully.")
    logger.info(f"Initializing sessionmaker")
    return async_sessionmaker(bind=engine,
                              autoflush=False,
                              class_=AsyncSession,
                              expire_on_commit=False,
                              future=True)


engine = create_async_engine(url=settings.database_url)
sessionmaker = create_sessionmaker(engine)
