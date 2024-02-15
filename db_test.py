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
from datetime import datetime


now = datetime.now()

year = now.year
month = now.month
day = now.day
hour = now.hour
minute = now.minute
desired_datetime = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
# Вывод: 2024, 2, 14, 20, 34
print(desired_datetime)
print(now.ctime())


# Вывод: 2024, 02, 14, 20, 34

