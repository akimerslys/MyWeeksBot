from __future__ import annotations
from typing import TYPE_CHECKING
from loguru import logger
from datetime import datetime, timedelta

from sqlalchemy import func, select, update

from cache.redis import build_key, cached, clear_cache
from database.models import KeyModel
from services.users import set_user_premium

from key_generator.key_generator import generate
from core.config import settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

"""
    id: Mapped[int_pk]
    key: Mapped[str] = mapped_column(primary_key=True)
    days: Mapped[int] = mapped_column(default=7, nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False)
    used_by: Mapped[int | None]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
"""


async def add_key(session: AsyncSession, days: int = 7) -> str:
    """Generate and add a new key to the database."""
    try:
        key = generate(4, '-', 4, 4,
                       type_of_value=settings.TYPE,
                       capital=settings.CAPITAL,
                       extras=settings.EXTRAS).get_key()
    except Exception as e:
        logger.error(f"Key generation failed: {e}")
        return ""
    new_key = KeyModel(
        key=key,
        days=days,
    )
    session.add(new_key)
    await session.commit()
    return key


async def select_key(session: AsyncSession, key: str) -> KeyModel | None:
    query = select(KeyModel).filter_by(key=key)

    result = await session.execute(query)

    key = result.scalar_one_or_none()
    return key


async def is_used(session: AsyncSession, key: str) -> bool:
    key_ = await select_key(session, key)
    return key_.is_used


async def is_key(session: AsyncSession, key: str) -> bool:
    query = await select_key(session, key)

    if not query:
        return False
    return True


async def get_key_days(session: AsyncSession, key: str) -> int:
    key_ = await select_key(session, key)
    return key_.days


async def use_key(session: AsyncSession, key: str, user_id: int) -> bool:
    key_ = await select_key(session, key)
    if not key_ or key_.is_used:
        return False
    logger.info(f"Using key for user {user_id}")
    key_.is_used = True
    key_.used_by = user_id
    stmt = update(KeyModel).where(KeyModel.key == key).values(is_used=True, used_by=user_id)
    await session.execute(stmt)
    await session.commit()
    await set_user_premium(session, user_id, key_.days)

    return True

