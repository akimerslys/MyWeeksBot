from database.database import db
from database import dbcommands as dc
import asyncio
from core.config import settings


async def db_test():
    await db.set_bind(settings.database_url)
    await db.gino.create_all()

    await dc.add_user(123, "ahahhad", "en", "Europe/London")
    await dc.add_user(2535, "Tbebe")
    await dc.add_user(125125, "Tesasdar 3", "ru", "GMT+3")

    print(await dc.get_user_info(1))
    await dc.update_user_lang(1, "uk")
    print(await dc.get_user_info(1))
    print("2")
    print(await dc.get_user_info(228))
    await dc.update_user_lang(228, "ukr")
    await dc.update_user_tz(228, "Europe/Kiev")

    print(await dc.get_user_info(228))
    print(await dc.count_users())


loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
loop.close()
