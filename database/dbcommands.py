from asyncpg import UniqueViolationError
from loguru import logger
from database.schemas.users import User
from database.database import db


async def add_user(userid: int, name: str, language: str = None, timezone: str = None):
    try:
        user = User(userid=userid, name=name, language=language, timezone=timezone)
        await user.create()
    except UniqueViolationError:
        logger.error(f"User {userid} wasn't added to the database because it already exists??")


async def select_all_users() -> list[User]:
    return await User.query.gino.all()


async def count_users() -> int:
    return await db.func.count(User.id).gino.scalar()


async def select_user(userid: int) -> User:
    return await User.query.where(User.userid == userid).gino.first()


async def get_user_info(userid: int) -> dict:
    user = await select_user(userid)
    return {
        "id": user.id,
        "userid": user.userid,
        "name": user.name,
        "language": user.language,
        "timezone": user.timezone,
    }

async def update_user_lang(userid: int, lang: str):
    user = await select_user(userid)
    await user.update(language=lang).apply()


async def update_user_tz(userid: int, tz: str):
    user = await select_user(userid)
    await user.update(timezone=tz).apply()



