from __future__ import annotations
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import func, select, update

from bot.cache.redis import build_key, cached, clear_cache
from bot.database.models import UserModel

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


async def get_user(session: AsyncSession, user_id: int) -> UserModel:
    query = select(UserModel).filter_by(user_id=user_id)
    logger.debug(f"selected user {user_id}")
    result = await session.execute(query)

    user = result.scalar_one_or_none()
    return user


async def count_user_notifs(session: AsyncSession, user_id: int) -> int:
    query = select(func.count(UserModel.active_notifs)).filter_by(user_id=user_id)

    result = await session.execute(query)

    count = result.scalar_one_or_none() or 0
    return int(count)


async def inc_user_notifs(session: AsyncSession, user_id: int) -> None:
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(active_notifs=UserModel.active_notifs + 1)

    await session.execute(stmt)
    await session.commit()


async def dec_user_notifs(session: AsyncSession, user_id: int) -> None:
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(active_notifs=UserModel.active_notifs - 1)

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
    return language_code or ""


async def set_language_code(
    session: AsyncSession,
    user_id: int,
    language_code: str,
) -> None:
    logger.info(f"Setting user {user_id} language to {language_code}")
    stmt = update(UserModel).where(UserModel.user_id == user_id).values(language_code=language_code)
    await session.execute(stmt)
    await session.commit()


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


@cached(key_builder=lambda session: build_key())
async def get_all_users(session: AsyncSession) -> list[UserModel]:
    query = select(UserModel)

    result = await session.execute(query)

    users = result.scalars()
    return list(users)


@cached(key_builder=lambda session: build_key())
async def count_users(session: AsyncSession) -> int:
    query = select(func.count()).select_from(UserModel)

    result = await session.execute(query)

    count = result.scalar_one_or_none() or 0
    return int(count)
