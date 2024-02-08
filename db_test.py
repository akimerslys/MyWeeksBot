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


loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
loop.close()
