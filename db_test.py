"""from database.engine import sessionmaker, create_async_engine
from services import users as dbuser
from services import notifs as dbnotif
from services import keys as dbkey
from database.models import Base
from core.config import settings
from loguru import logger

async def main():
    async_engine = create_async_engine(url=settings.database_url)
    session_maker = sessionmaker(bind=async_engine)

    async with session_maker as session:
        await dbuser.add_user(session, 1337, "testnameXD123", "uk", "eu/uk")
        logger.success(await dbuser.get_user(session, 1123))
        key = await dbkey.add_key(session, 7)
        await dbkey.use_key(session, key, 1337)
        logger.success(await dbuser.get_user(session, 1123))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())"""
from datetime import datetime
import pytz
import asyncio

def lalal(hour: int = 0):
    if hour < 23:
        for index in range(hour+1, 24):
            print(f"{index}:00")
    else:
        print("meow")


lalal(2)

