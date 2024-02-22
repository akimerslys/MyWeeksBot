from __future__ import annotations
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import func, select, update

from bot.cache.redis import build_key, cached, clear_cache
from bot.database.models import ScheduleModel


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


async def add_schedule(
    session: AsyncSession,
    user_id: int,
    day: str,
    time: str,
    text: str | None = "",
) -> None:
    """Add a new user to the database."""
    logger.info(f"adding schedule for user {user_id}")
    if time[1] == ":":
        time = '0' + time
    if text == "Skip":
        text = None
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


async def get_one_schedule(session: AsyncSession, id: int) -> ScheduleModel:
    logger.debug(f"selected schedule {id}")
    query = select(ScheduleModel).filter_by(id=id)
    result = await session.execute(query)
    schedule = result.scalar_one_or_none()
    return schedule


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_user_schedule(session: AsyncSession, user_id: int) -> list[ScheduleModel]:
    query = select(ScheduleModel).filter_by(user_id=user_id)

    result = await session.execute(query)
    logger.debug(f"got user notifs {user_id}")
    schedule_list = result.scalars()
    return list(schedule_list)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_user_schedule_day_time_text(session: AsyncSession, user_id: int) -> list[tuple]:
    query = select(ScheduleModel).filter_by(user_id=user_id)

    result = await session.execute(query)
    logger.debug(f"got user notifs {user_id}")
    schedule_list = result.scalars()

    schedule_info = [(schedule.day, schedule.time, schedule.text) for schedule in schedule_list]

    return schedule_info


async def count_user_schedule(session: AsyncSession, user_id: int) -> int:
    query = select(ScheduleModel).filter_by(user_id=user_id)

    result = await session.execute(query)
    logger.debug(f"counted user schedule {user_id}")
    count = result.scalar_one_or_none() or 0
    return count


async def get_schedule_text(session: AsyncSession, id: int) -> str:
    query = select(ScheduleModel.text).filter_by(id=id)

    result = await session.execute(query)
    logger.debug(f"got notif text {id}")
    text = result.scalar_one_or_none()
    return text or ""


async def update_schedule_text(session: AsyncSession, id: int, text: str) -> None:
    stmt = update(ScheduleModel).where(ScheduleModel.id == id).values(text=text)
    logger.debug(f"updated schedule text {id}")
    await session.execute(stmt)
    await session.commit()


async def delete_one_schedule(session: AsyncSession, id: int) -> None:
    user_schedule = await get_one_schedule(session, id)
    tmp_id = int("0" + str(user_schedule.user_id))
    stmt = update(ScheduleModel).where(ScheduleModel.id == id).values(user_id=tmp_id, active=False)
    logger.debug(f"deleted notification {id}")
    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_one_schedule, id)


async def get_notifs_by_day(session: AsyncSession, day: str) -> list[ScheduleModel]:
    query = select(ScheduleModel).filter_by(day=day)

    result = await session.execute(query)
    logger.debug(f"got schedule by day {day}")
    notifs = result.scalars()
    return list(notifs)


@cached(key_builder=lambda session: build_key())
async def get_all_notifs(session: AsyncSession) -> list[ScheduleModel]:
    query = select(ScheduleModel)

    result = await session.execute(query)
    logger.debug(f"got all schedule")
    users = result.scalars()
    return list(users)


async def count_schedules(session: AsyncSession) -> int:
    query = select(func.count()).select_from(ScheduleModel)

    result = await session.execute(query)
    logger.debug(f"counted all schedule")
    count = result.scalar_one_or_none() or 0
    return int(count)
