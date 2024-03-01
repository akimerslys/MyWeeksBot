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


async def day_of_week_to_date(day, time, timezone):
    """
    Convert day of week and time to datetime with user's timezone
    :param day:
    :param time:
    :param timezone:
    :return:
    """
    logger.debug(f"localizing day of week to datetime")
    tz = pytz.timezone(timezone)
    current_datetime = datetime.now(tz)

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    current_day_of_week = current_datetime.strftime('%A')
    days_to_target_day = (days_of_week.index(day) - days_of_week.index(current_day_of_week)) % 7
    target_date = current_datetime + timedelta(days=days_to_target_day)

    target_datetime_str = f"{target_date.strftime('%Y-%m-%d')} {time}"

    target_datetime = datetime.strptime(target_datetime_str, '%Y-%m-%d %H:%M')

    target_datetime_with_timezone = target_datetime.replace(tzinfo=tz)

    if target_datetime_with_timezone < current_datetime:
        target_date += timedelta(days=7)
        target_datetime_with_timezone = target_date.replace(tzinfo=tz)

    return target_datetime_with_timezone.replace(tzinfo=None)
