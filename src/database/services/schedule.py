from __future__ import annotations
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import func, select, update, delete

from src.database.services.notifs import get_all_notifs
from src.cache.redis import build_key, cached, clear_cache
from src.database.models import ScheduleModel


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

"""
    id: Mapped[int_pk]
    user_id = Column(BigInteger)
    day: Mapped[str]
    time: Mapped[dtime]
    text: Mapped[str] = mapped_column(default=None)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
"""


def upgrade_day(s: str | int):
    if isinstance(s, str):
        days_of_week = {
                    "Monday": 0,
                    "Tuesday": 1,
                    "Wednesday": 2,
                    "Thursday": 3,
                    "Friday": 4,
                    "Saturday": 5,
                    "Sunday": 6
                }
        s = days_of_week[s]
    return s


async def add_schedule(
    session: AsyncSession,
    user_id: int,
    day: str | int,
    time: str,
    text: str | None = "",
) -> None:
    """Add a new user schedule to the database."""
    if time[1] == ":":
        time = '0' + time
    if text == "Skip":
        text = None
    day = upgrade_day(day)
    logger.info(f"adding schedule for user {user_id}, [{day}, {time}, {text}]")
    new_notif = ScheduleModel(
        user_id=user_id,
        day=day,
        time=time,
        text=text,
    )
    await clear_cache(get_user_schedule, user_id)
    await clear_cache(get_user_schedule_day_time_text, user_id)
    session.add(new_notif)
    await session.commit()


@cached(key_builder=lambda session, id: build_key(id))
async def get_one_schedule(session: AsyncSession, id: int) -> ScheduleModel:
    logger.debug(f"selected schedule {id}")
    query = select(ScheduleModel).filter_by(id=id)
    result = await session.execute(query)
    schedule = result.scalar_one_or_none()
    return schedule


async def get_user_schedule(session: AsyncSession, user_id: int) -> list[ScheduleModel]:
    query = select(ScheduleModel).filter_by(user_id=user_id)

    result = await session.execute(query)
    logger.debug(f"got user notifs {user_id}")
    schedule_list = result.scalars()
    return list(schedule_list)


async def get_user_schedule_day_time_text(session: AsyncSession, user_id: int) -> list[tuple]:
    query = select(ScheduleModel).filter_by(user_id=user_id).order_by(ScheduleModel.time)

    result = await session.execute(query)
    logger.debug(f"got user notifs {user_id}")
    schedule_list = result.scalars()

    schedule = [(schedule.day, schedule.time, schedule.text) for schedule in schedule_list]

    return schedule


async def get_user_day_schedule_day_time_text(session: AsyncSession, user_id: int, day: str | int) -> list[tuple]:
    day = upgrade_day(day)
    query = select(ScheduleModel).filter_by(user_id=user_id, day=day).order_by(ScheduleModel.time)

    result = await session.execute(query)
    logger.debug(f"got user schedule by day {day}")
    notifs = result.scalars()
    schedule_list = [(day, schedule.time, schedule.text) for schedule in notifs]
    return schedule_list


@cached(key_builder=lambda session, id: build_key(id))
async def count_user_schedule(session: AsyncSession, user_id: int) -> int:
    query = select(func.count()).where(ScheduleModel.user_id == user_id)

    result = await session.execute(query)

    count = result.scalar_one_or_none() or 0

    logger.debug(f"counted user schedule {user_id}: {count}")

    return count


async def get_schedule_text(session: AsyncSession, id: int) -> str:
    query = select(ScheduleModel.text).filter_by(id=id)
    result = await session.execute(query)
    text = result.scalar_one_or_none()
    logger.debug(f"got notif text {id}, {text}")
    return text or ""


async def update_schedule_text(session: AsyncSession, id: int, text: str) -> None:
    stmt = update(ScheduleModel).where(ScheduleModel.id == id).values(text=text)
    logger.debug(f"updated schedule text {id}, {text}")
    await session.execute(stmt)
    await session.commit()


async def delete_one_schedule(session: AsyncSession, id: int) -> None:
    stmt = delete(ScheduleModel).where(ScheduleModel.id == id)
    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_one_schedule, id)
    logger.info(f"deleted schedule {id}")


async def get_user_schedule_by_day(session: AsyncSession, user_id: int, day: str | int) -> list[tuple]:
    day = upgrade_day(day)
    query = select(ScheduleModel).filter_by(user_id=user_id, day=day).order_by(ScheduleModel.time)

    result = await session.execute(query)
    logger.debug(f"got user schedules by day {day}")
    notifs = result.scalars()
    schedule_list = [(schedule.time, schedule.text) for schedule in notifs]
    return schedule_list


async def get_user_schedule_by_day_with_id(session: AsyncSession, user_id: int, day: str | int) -> list[tuple]:
    day = upgrade_day(day)
    query = select(ScheduleModel).filter_by(user_id=user_id, day=day).order_by(ScheduleModel.time)

    result = await session.execute(query)
    logger.debug(f"got user schedule by day {day}")
    notifs = result.scalars()
    schedule_list = [(day, schedule.time, schedule.text, schedule.id) for schedule in notifs]
    return schedule_list


async def get_all_schedule(session: AsyncSession) -> list[ScheduleModel]:
    query = select(ScheduleModel)

    result = await session.execute(query)
    logger.debug(f"got all schedule")
    schedule = result.scalars()
    return list(schedule)


async def count_schedules(session: AsyncSession) -> int:
    query = select(func.count()).select_from(ScheduleModel)

    result = await session.execute(query)
    logger.debug(f"counted all schedule")
    count = result.scalar_one_or_none() or 0
    return int(count)


async def delete_all_user_schedule(session: AsyncSession, user_id) -> None:
    stmt = delete(ScheduleModel).where(ScheduleModel.user_id == user_id)
    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_one_schedule, user_id)
    await clear_cache(get_all_notifs, user_id)
