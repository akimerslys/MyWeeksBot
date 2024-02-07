from asyncpg import UniqueViolationError
from loguru import logger
from database.modules.notifications import Notification
from database.database import db
from datetime import datetime, timedelta

# TODO FIX AND DETERMINE REPEAT FUNCTION

"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(db.DateTime(True))
    userid = Column(BigInteger)
    text = Column(String(20))
    repeat = Column(Boolean, default=False)
    week_repeat = Column(Boolean, default=False)
    next_date = Column(db.DateTime(True))
"""


async def add_notif(date: datetime,
                    userid: int, text: str,
                    repeat: bool = False,
                    week_repeat: bool = False,
                    next_date: datetime = None):

    notif = Notification(
            date=date,
            userid=userid,
            text=text,
            repeat=repeat,
            week_repeat=week_repeat,
            next_date=next_date
    )
    await notif.create()


async def select_all_notifications() -> list[Notification]:
    return await Notification.query.gino.all()


async def count_all_notifications() -> int:
    return await db.func.count(Notification.id).gino.scalar()


async def select_notification(id: int) -> Notification:
    return await Notification.query.where(Notification.id == id).gino.first()


async def get_notification_info(id: int) -> Notification:
    notification = await select_notification(id)
    return notification


async def get_user_notifications(userid: int) -> list[Notification]:
    return await Notification.query.where(Notification.userid == userid).gino.all()


async def count_user_notifications(userid: int) -> int:
    return await db.func.count(Notification.userid == userid).gino.scalar()


async def update_notification(id: int,
                              date: datetime = None,
                              text: str = None,
                              repeat: bool = None,
                              week_repeat: bool = None,
                              next_date: datetime = None):
    notification = await select_notification(id)
    if date is not None:
        notification.date = date
    if text is not None:
        notification.text = text
    if repeat is not None:
        notification.repeat = repeat
    if week_repeat is not None:
        notification.week_repeat = week_repeat
    if next_date is not None:
        notification.next_date = next_date
    await notification.update()
    logger.info(f"Notification {notification.id} was updated in the database")


async def update_notification_next_date(id: int, repeat: bool, week_repeat: bool):
    notification = await select_notification(id)

    if week_repeat:
        notification.next_date = notification.date + timedelta(days=7)
    elif repeat:
        notification.next_date = notification.date + timedelta(days=31)          # TODO FIX FOR DIFFERENT MONTHS
    else:
        notification.delete()
    logger.info(f"Notification {notification.id} next_date was updated in the database")


async def delete_notification(id: int):
    notification = await select_notification(id)
    await notification.delete()
    logger.info(f"Notification {notification.id} was deleted from the database")
