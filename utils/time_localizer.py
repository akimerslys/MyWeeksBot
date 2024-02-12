from datetime import datetime, timedelta
import pytz


async def localize_time_to_utc(time: datetime, timezone: str) -> datetime:
    """
    Convert time from user timezone to UTC
    :param timezone: str
    :param time: datetime
    :return: datetime
    """
    return pytz.timezone(timezone).localize(time).astimezone(pytz.utc).replace(tzinfo=None)


async def localize_time_to_timezone(timezone: str) -> datetime:
    """
    Convert current time to user timezone
    :param timezone: str
    :return: datetime
    """
    return pytz.timezone(timezone).localize(datetime.utcnow()).astimezone(pytz.utc).replace(tzinfo=None)