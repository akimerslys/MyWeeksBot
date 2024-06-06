from datetime import datetime, timedelta, time
import pytz
from loguru import logger


def localize_datetime_to_utc(time: datetime, timezone: str) -> datetime:
    """
    Convert time from user timezone to UTC
    :param timezone: str
    :param time: datetime
    :return: datetime
    """
    logger.debug(f"localize_time_to_utc: timezone={timezone}, time={time}")
    return pytz.timezone(timezone).localize(time).astimezone(pytz.utc).replace(tzinfo=None)


def localize_datetimenow_to_timezone(timezone: str) -> datetime:
    """
    Convert current time to user timezone
    :param timezone: str
    :return: datetime
    """
    logger.debug(f"localize_time_to_timezone: timezone={timezone}")
    return pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone(timezone)).replace(tzinfo=None)


def localize_datetime_to_timezone(time: datetime, timezone: str) -> datetime:
    """
    Convert utc time to user timezone
    :param time: datetime
    :param timezone: str
    :return: datetime
    """
    logger.debug(f"localize_time_to_timezone: timezone={timezone}, time={time}")
    return pytz.utc.localize(time).astimezone(pytz.timezone(timezone)).replace(tzinfo=None)


def is_today(dtime: datetime, timezone: str) -> bool:
    """
    Check if time is today in user timezone
    :param timezone: str
    :return: bool
    """
    logger.debug(f"running is_today")

    return datetime.today().astimezone(pytz.timezone(timezone)).strftime("%Y %m %d") == dtime.strftime("%Y %m %d")


def day_of_week_to_date(day: str | int, time: time, timezone: str = 'UTC'):
    """
    Convert day of week and time to datetime with user's timezone
    :param day: str or int, representing the day of the week ('Monday' or 0 for Monday)
    :param time: str, representing the time in 'HH:MM' format
    :param timezone: str, representing the user's timezone
    :return: datetime object
    """
    logger.debug(f"localizing day of week to datetime")
    tz = pytz.timezone(timezone)
    current_datetime = datetime.now(tz)

    if isinstance(day, str):
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_day_of_week = current_datetime.strftime('%A')
        days_to_target_day = (days_of_week.index(day) - days_of_week.index(current_day_of_week)) % 7
    elif isinstance(day, int):
        days_to_target_day = (day - current_datetime.weekday()) % 7
    else:
        raise ValueError("Invalid day format. It should be either a string or an integer.")

    target_date = current_datetime + timedelta(days=days_to_target_day)

    target_datetime_str = f"{target_date.strftime('%Y-%m-%d')} {time}"

    target_datetime = datetime.strptime(target_datetime_str, '%Y-%m-%d %H:%M')

    target_datetime_with_timezone = target_datetime.replace(tzinfo=tz)

    if target_datetime_with_timezone < current_datetime:
        target_date += timedelta(days=7)
        target_datetime_with_timezone = target_date.replace(tzinfo=tz)

    return target_datetime_with_timezone.replace(tzinfo=None)


def localize_time_to_utc(hrs: str, minutes: str, timezone: str) -> time:
    """
    Convert time from user timezone to UTC
    :param hrs: str
    :param minutes: str
    :param timezone: str
    :return: time
    """
    config_time = time(int(hrs), int(minutes))
    current_date = datetime.now().date()
    config_datetime = datetime.combine(current_date, config_time)
    timezone = pytz.timezone(timezone)
    result = timezone.localize(config_datetime).astimezone(pytz.utc).replace(tzinfo=None)
    logger.debug(f"localize_time_to_utc: timezone={timezone}, time={time}")
    return result.time()


def is_past(date: datetime, timezone: str = 'UTC') -> bool:
    """
    Check if time is in the past in users timezone
    :param timezone: str
    :return: bool
    """

    logger.debug(f"running if_past_time, date: {date}, timezone: {timezone}")
    return localize_datetimenow_to_timezone(timezone) > date + timedelta(minutes=5)


def is_future(date: datetime) -> bool:
    """
    Check if time is in more than a year of now
    :param date: datetime
    :return: bool
    """
    logger.debug(f"running if_future_time, date: {date}")
    return date > datetime.now() + timedelta(days=365)


def round_minute(hour, minute):
    if minute % 5 >= 2.5:
        minute_rounded = minute + (5 - minute % 5)
    else:
        minute_rounded = minute - (minute % 5)

    if minute_rounded == 60:
        hour += 1
        minute_rounded = 0

    hour %= 24

    return hour, minute_rounded


def weekday_to_future_date(weekday_number, tz: str = 'UTC'):
    now = datetime.now(pytz.timezone(tz))
    current_weekday = now.weekday()
    return now + timedelta(days=(weekday_number - current_weekday) % 7)
