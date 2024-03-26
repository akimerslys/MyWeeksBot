import pytz
from datetime import datetime

from aiocache import logger
from aiogram import Bot
from aiogram.types import CallbackQuery
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.services.notifs import get_notif
from src.bot.utils import time_localizer as tl


async def check_date(date: str, bot, id_):
    logger.debug("checking date for user {id}")
    try:
        dt = datetime.strptime(date, '%Y-%m-%d-%H-%M')
    except ValueError:
        logger.error(f"Error while getting date from payload:{id_} : {date}")
        await bot.send_message(id_, "Invalid Date\n")
        return False

    return True


async def check_tz(tz, query: Bot | CallbackQuery, id_):
    logger.debug(f"checking tz for user {id_}")
    try:
        pytz.timezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        logger.error(f"Error while getting timezone from payload: {tz}")
        await query.answer("Invalid Timezone\n")
        return False

    return True


async def check_date_ranges(dt, bot, id_, tz: str = 'UTC'):
    logger.debug(f"checking date ranges for user {id_}")
    if tl.is_future(dt) or tl.is_past(dt, tz):
        logger.error(f"Invalid range from user {id_} : {dt}")
        await bot.send_message(id_, "Date Passed\n")
        return False
    return True


async def check_notif(session: AsyncSession, bot: Bot, id_: int, notif_id: int):
    logger.debug(f"checking notif for user {id_}")
    try:

        shared_notif = await get_notif(session, notif_id)

        if not shared_notif:
            logger.error(f"Error while getting notif from payload: {notif_id}")
            await bot.send_message(id_, "Error, notification does not exist")
            return False

    except (IntegrityError, ProgrammingError) as e:

        logger.error(f"Error while getting notif from payload: {e}")
        await bot.send_message(id_, "Error, notification does not exist")
        return False

    return shared_notif