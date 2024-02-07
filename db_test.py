from database.database import db
from database import dbcommands as dc
from datetime import datetime, timedelta
import asyncio
from core.config import settings


async def db_test():
    await db.set_bind(settings.database_url)
    await db.gino.drop_all()
    await db.gino.create_all()
    await dc.add_user(1123456789, "Test User", "en", "Europe/Kiev", 1, True, datetime.utcnow() + timedelta(days=30))
    await dc.add_user(2298765432, "Test User 2", "uk", "Europe/London")
    await dc.add_user(3312345678, "Test User 3", "ru", "Europe/Kyiv")

    print(await dc.get_user_info(2298765432))

    await dc.update_user_premium(2298765432, True, datetime.utcnow() + timedelta(days=30))

    print(await dc.get_user_info(2298765432))



loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
loop.close()
