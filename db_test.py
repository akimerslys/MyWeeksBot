"""import asyncio

from database.engine import sessionmaker, create_async_engine

from database.models import Base
from core.config import settings


async_engine = create_async_engine(url=settings.database_url)
session_maker = sessionmaker(bind=async_engine)


async def main():
    # Создаем таблицы на основе определенных моделей данных
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(main())"""

