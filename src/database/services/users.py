from __future__ import annotations
from __future__ import annotations
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import func, select, update, delete

from src.cache.redis import build_key, cached, clear_cache
from src.database.models import UserModel

from datetime import datetime, timedelta

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

"""
    id: Mapped[int_pk]
    userid: Mapped[int]
    name: Mapped[str]
    language_code: Mapped[str | None]
    timezone: Mapped[str | None] = mapped_column(default="UTC")
    active_notifs: Mapped[int] = mapped_column(default=0)
    is_premium: Mapped[bool] = mapped_column(default=False)
    premium_until: Mapped[dtime]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
"""


async def add_user(
    session: AsyncSession,
    user_id: int,
    first_name: str,
    language_code: str | None = "en",
    timezone: str = "UTC",
    active: bool = False,
) -> None:
    """Add a new user to the database."""
    user_id: int = user_id
    if await user_exists(session, user_id):
        return
    first_name: str = first_name
    language_code: str | None = language_code
    timezone: str | None = timezone
    logger.info(f"Added new user {user_id} to the database")
    new_user = UserModel(
        user_id=user_id,
        first_name=first_name,
        language_code=language_code,
        timezone=timezone,
        is_blocked=False,
        active=active
    )

    session.add(new_user)
    await session.commit()
    await clear_cache(user_exists, user_id)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def user_exists(session: AsyncSession, user_id: int) -> bool:
    """Checks if the user is in the database."""
    logger.debug(f"Checking if user {user_id} exists")
    query = select(UserModel.id).filter_by(user_id=user_id).limit(1)

    result = await session.execute(query)

    user = result.scalar_one_or_none()
    return bool(user)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def user_logged(session: AsyncSession, user_id: int) -> bool:
    """Checks if the user exist and active ()"""
    logger.debug(f"Checking if user {user_id} active")
    query = select(UserModel.active).filter_by(user_id=user_id).limit(1)

    result = await session.execute(query)

    active = result.scalar_one_or_none()

    active = bool(active)

    logger.debug(f"user {user_id} is active: {active}")

    return active


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_user_active(session: AsyncSession, user_id: int) -> bool:
    query = select(UserModel.active).filter_by(user_id=user_id)

    result = await session.execute(query)

    active = result.scalar_one_or_none()

    active = bool(active)
    logger.debug("user active: " + str(active))

    return active

async def set_user_active(session: AsyncSession, user_id: int, active: bool) -> None:
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(active=active)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_user_active, user_id)


async def get_user(session: AsyncSession, user_id: int) -> UserModel:
    query = select(UserModel).filter_by(user_id=user_id)
    logger.debug(f"selected user {user_id}")
    result = await session.execute(query)

    user = result.scalar_one_or_none()
    return user


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def count_user_notifs(session: AsyncSession, user_id: int) -> int:
    query = select(func.count(UserModel.active_notifs)).filter_by(user_id=user_id)

    result = await session.execute(query)

    count = result.scalar_one_or_none()
    if not count:
        return 0
    return int(count)


async def inc_user_notifs(session: AsyncSession, user_id: int) -> None:
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(active_notifs=UserModel.active_notifs + 1)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(count_user_notifs, user_id)

async def dec_user_notifs(session: AsyncSession, user_id: int) -> None:
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(active_notifs=UserModel.active_notifs - 1)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(count_user_notifs, user_id)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_user_max_notifs(session: AsyncSession, user_id: int) -> int:
    query = select(UserModel.max_notifs).filter_by(user_id=user_id)

    result = await session.execute(query)
    logger.debug(result)
    max_notifs = result.scalar_one_or_none()
    logger.debug(f"counted max notif for user {user_id}, {max_notifs}")
    return max_notifs or None


async def update_max_notifs(session: AsyncSession, user_id: int, max_notifs: int, operator: str) -> None:
    if operator == None:
        stmt = update(UserModel).where(UserModel.user_id == user_id).values(max_notifs=max_notifs)
    elif operator == "add":
        stmt = update(UserModel).where(UserModel.user_id == user_id).values(max_notifs=UserModel.max_notifs + max_notifs)
    elif operator == "sub":
        stmt = update(UserModel).where(UserModel.user_id == user_id).values(max_notifs=UserModel.max_notifs - max_notifs)
    else:
        logger.error(f"Invalid operator {operator}, {user_id}")
        return

    await session.execute(stmt)
    await session.commit()


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_first_name(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.first_name).filter_by(user_id=user_id)

    result = await session.execute(query)

    first_name = result.scalar_one_or_none()
    return first_name or ""


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_language_code(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.language_code).filter_by(user_id=user_id)

    result = await session.execute(query)

    language_code = result.scalar_one_or_none()
    return language_code or "en"


async def set_language_code(
    session: AsyncSession,
    user_id: int,
    language_code: str,
) -> None:
    logger.info(f"Setting user {user_id} language to {language_code}")
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(language_code=language_code)
    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_language_code, user_id)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_timezone(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.timezone).filter_by(user_id=user_id)
    logger.debug(f"Returned timezone for user {user_id}")
    result = await session.execute(query)

    timezone = result.scalar_one_or_none()
    return timezone or ""


async def set_timezone(
    session: AsyncSession,
    user_id: int,
    timezone: str,
) -> None:
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(timezone=timezone)
    logger.info(f"Setting user {user_id} timezone to {timezone}")
    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_timezone, user_id)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def is_premium(session: AsyncSession, user_id: int) -> bool:
    query = select(UserModel.is_premium).filter_by(user_id=user_id)

    result = await session.execute(query)

    is_premium = result.scalar_one_or_none()
    return bool(is_premium)


async def set_user_premium(session: AsyncSession, user_id: int, days: int) -> None:
    if days < 1:
        return
    logger.info(f"Setting user {user_id} premium for {days} days")
    if await is_premium(session, user_id):
        stmt = update(UserModel).where(UserModel.user_id == user_id).values(
            premium_until=UserModel.premium_until + timedelta(days=days))
    else:
        stmt = update(UserModel).where(UserModel.user_id == user_id).values(
            premium_until=datetime.now() + timedelta(days=days), is_premium=True)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(is_premium, user_id)


async def get_all_users(session: AsyncSession) -> list[UserModel]:
    query = select(UserModel)

    result = await session.execute(query)

    users = result.scalars()
    return list(users)


async def count_users(session: AsyncSession) -> int:
    query = select(func.count()).select_from(UserModel)

    result = await session.execute(query)

    count = result.scalar_one_or_none() or 0
    return int(count)


async def set_schedule_time(session: AsyncSession, user_id: int, time: datetime.time) -> None:
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(schedule_time=time)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_schedule_time, user_id)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_schedule_time(session: AsyncSession, user_id: int) -> datetime.time | None:
    query = select(UserModel.schedule_time).filter_by(user_id=user_id)

    result = await session.execute(query)

    schedule_time = result.scalar_one_or_none()
    return schedule_time


async def set_schedule_mode(session: AsyncSession, user_id: int, mode: bool) -> None:
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(schedule_mode=mode)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_schedule_mode, user_id)


@cached(key_builder=lambda session, time: build_key(time))
async def get_schedule_mode(session: AsyncSession, user_id: int) -> str | None:
    query = select(UserModel.schedule_mode).filter_by(user_id=user_id)

    result = await session.execute(query)

    schedule_mode = result.scalar_one_or_none()
    return bool(schedule_mode)

async def get_schedule_users_by_time(session: AsyncSession, time: datetime.time) -> list[UserModel]:
    query = select(UserModel).filter_by(schedule_time=time)

    result = await session.execute(query)

    users = result.scalars()
    return list(users)


async def block_user(session: AsyncSession, user_id: int) -> None:
    logger.info(f"Blocking user {user_id}")
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(is_blocked=True)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(is_blocked, user_id)


async def unblock_user(session: AsyncSession, user_id: int) -> None:
    logger.info(f"Unblocking user {user_id}")
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(is_blocked=False)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(is_blocked, user_id)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def is_blocked(session: AsyncSession, user_id: int) -> bool:
    query = select(UserModel.is_blocked).filter_by(user_id=user_id)

    result = await session.execute(query)

    is_blocked = result.scalar_one_or_none()
    return bool(is_blocked)


async def delete_user(session: AsyncSession, user_id: int) -> None:
    logger.info(f"Deleting user {user_id}")
    stmt = delete(UserModel).where(UserModel.user_id == user_id)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(user_exists, user_id)
    await clear_cache(get_first_name, user_id)
    await clear_cache(get_language_code, user_id)
    await clear_cache(get_timezone, user_id)
    await clear_cache(is_premium, user_id)
    await clear_cache(count_user_notifs, user_id)
    await clear_cache(get_user_max_notifs, user_id)
    await clear_cache(get_schedule_time, user_id)
    await clear_cache(get_schedule_mode, user_id)
    await clear_cache(is_blocked, user_id)
    await clear_cache(get_user_active, user_id)

