import pytz

from aiocache import logger
from aiogram import Bot
from aiogram.types import CallbackQuery




async def check_tz(tz, query: Bot | CallbackQuery, id_):
    logger.debug(f"checking tz for user {id_}")
    try:
        pytz.timezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        logger.error(f"Error while getting timezone from payload: {tz}")
        await query.answer("Invalid Timezone\n")
        return False

    return True
