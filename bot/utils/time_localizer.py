from datetime import datetime, timedelta
import pytz
from loguru import logger


async def localize_time_to_utc(time: datetime, timezone: str) -> datetime:
    """
    Convert time from user timezone to UTC
    :param timezone: str
    :param time: datetime
    :return: datetime
    """
    logger.debug(f"localize_time_to_utc: timezone={timezone}, time={time}")
    return pytz.timezone(timezone).localize(time).astimezone(pytz.utc).replace(tzinfo=None)


async def localize_timenow_to_timezone(timezone: str) -> datetime:
    """
    Convert current time to user timezone
    :param timezone: str
    :return: datetime
    """
    logger.debug(f"localize_time_to_timezone: timezone={timezone}")
    return pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone(timezone)).replace(tzinfo=None)


async def localize_time_to_timezone(time: datetime, timezone: str) -> datetime:
    """
    Convert time to user timezone
    :param time: datetime
    :param timezone: str
    :return: datetime
    """
    logger.debug(f"localize_time_to_timezone: timezone={timezone}, time={time}")
    return pytz.utc.localize(time).astimezone(pytz.timezone(timezone)).replace(tzinfo=None)

async def is_today(dtime: datetime, timezone: str) -> bool:
    """
    Check if time is today in user timezone
    :param time: datetime
    :param timezone: str
    :return: bool
    """
    logger.debug(f"running is_today")

    return datetime.today().astimezone(pytz.timezone(timezone)).strftime("%Y %m %d") == dtime.strftime("%Y %m %d")

