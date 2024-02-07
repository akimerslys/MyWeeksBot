from asyncpg import UniqueViolationError
from loguru import logger
from database.schemas.users import User
from database.database import db
from datetime import datetime, timedelta


"""userid = Column(Integer, unique=True)
name = Column(String(20))
language = Column(String(5))
timezone = Column(String(32))
notifications = Column(SmallInteger, default=0)
is_premium = Column(Boolean, default=False)
premium_until = Column(db.DateTime(True), nullable=True)"""


async def add_user(userid: int, name: str, language: str = "en",
                   timezone: str = "UTC", notifications: int = 0,
                   is_premium: bool = False, premium_until: datetime = None):
    if await user_exists(userid):
        return

    user = User(
            userid=userid,
            name=name,
            language=language,
            timezone=timezone,
            notifications=notifications,
            is_premium=is_premium,
            premium_until=premium_until
    )
    await user.create()


async def user_exists(userid: int) -> bool:
    user = await select_user(userid)
    return user is not None


async def select_all_users() -> list[User]:
    return await User.query.gino.all()


async def count_users() -> int:
    return await db.func.count(User.id).gino.scalar()


async def select_user(userid: int) -> User:
    return await User.query.where(User.userid == userid).gino.first()


async def get_user_info(userid: int) -> User:
    user = await select_user(userid)
    return user


# NAME
async def get_user_name(userid: int) -> str:
    user = await select_user(userid)
    return user.name


async def update_user_name(userid: int, name: str):
    user = await select_user(userid)
    await user.update(name=name).apply()


# LANGUAGE
async def get_user_lang(userid: int) -> str:
    user = await select_user(userid)
    return user.language


async def update_user_lang(userid: int, lang: str):
    user = await select_user(userid)
    await user.update(language=lang).apply()


# TIMEZONE
async def get_user_tz(userid: int) -> str:
    user = await select_user(userid)
    return user.timezone


async def update_user_tz(userid: int, tz: str):
    user = await select_user(userid)
    await user.update(timezone=tz).apply()


# NOTIFICATIONS
async def get_notifications(userid: int) -> int:
    user = await select_user(userid)
    return user.notifications


async def inc_notifications(userid: int):
    user = await select_user(userid)
    await user.update(notifications=user.notifications + 1).apply()


async def dec_notifications(userid: int):
    user = await select_user(userid)
    await user.update(notifications=user.notifications - 1).apply()


# PREMIUM
async def get_user_premium(userid: int) -> bool:
    user = await select_user(userid)
    return user.is_premium


async def update_user_premium(userid: int, premium: bool, until: datetime = None):
    user = await select_user(userid)
    await user.update(is_premium=premium, premium_until=until).apply()


# IDK why I need that
async def delete_user(userid: int):
    user = await select_user(userid)
    await user.delete()
    logger.info(f"User {userid} was deleted from the database")
