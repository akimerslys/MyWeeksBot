from database.database import db
from database import dbnotifcommands as dbnc
from database import dbusercommands as dbuc
from datetime import datetime, timedelta
import asyncio
from core.config import settings

"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(db.DateTime(True))
    userid = Column(BigInteger)
    text = Column(String(20))
    repeat = Column(Boolean, default=False)
    week_repeat = Column(Boolean, default=False)
    next_date = Column(db.DateTime(True))
"""


async def db_test():
    await db.set_bind(settings.database_url)
    await db.gino.drop_all()
    await db.gino.create_all()
    await dbuc.add_user(1234567890, "Test user")
    await dbnc.add_notif(datetime.now(), 1234567890, "Test notification")
    await dbnc.add_notif(datetime.now()+timedelta(minutes=50), 1234567890, "Test notification2", True, False)
    await dbnc.add_notif(datetime.now()+timedelta(minutes=100), 1234567890, "Test notification3", False, True)
    await dbnc.add_notif(datetime.now()+timedelta(minutes=150), 19888, "Test notification4")
    for notif in await dbnc.get_user_notifications(1234567890):
        print(notif.date, notif.text, notif.repeat, notif.week_repeat)




loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
loop.close()
