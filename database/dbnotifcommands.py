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
    repeat_day = Column(Boolean, default=False)
    repeat_week = Column(Boolean, default=False)
    repeat_month = Column(Boolean, default=False)
    next_date = Column(db.DateTime(True))
"""


async def add_notification(date: datetime,
                           userid: int, text: str,
                           repeat_day: bool = False,
                           repeat_week: bool = False,
                           repeat_month: bool = False):
    notif = Notification(
        date=date,
        userid=userid,
        text=text,
        repeat_day=repeat_day,
        repeat_week=repeat_week,
        repeat_month=repeat_month,
    )
    await notif.create()
    logger.info(f"Notification {notif.id} was added to the database")


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
                              repeat_day: bool = None,
                              repeat_week: bool = None,
                              repeat_month: bool = None):
    notification = await select_notification(id)
    if date is not None:
        notification.date = date
    if text is not None:
        notification.text = text
    if repeat_day is not None:
        notification.repeat_day = repeat_day
    if repeat_week is not None:
        notification.repeat_week = repeat_week
    if repeat_month is not None:
        notification.repeat_month = repeat_month
    await notification.update()
    logger.info(f"Notification {notification.id} was updated in the database")


async def update_notification_next_date(id: int, repeat_day: bool, repeat_week: bool, repeat_month: bool):
    notification = await select_notification(id)
    if repeat_day:
        notification.date = notification.date + timedelta(days=1)
    elif repeat_week:
        notification.date = notification.date + timedelta(days=7)
    elif repeat_month:
        notification.date = notification.date + timedelta(days=31)  # TODO FIX FOR DIFFERENT MONTHS
    else:
        notification.delete()
    logger.info(f"Notification {notification.id} next_date was updated in the database")


async def delete_notification(id: int):
    notification = await select_notification(id)
    await notification.delete()
    logger.info(f"Notification {notification.id} was deleted from the database")
