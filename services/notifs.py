from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import func, select, update

from cache.redis import build_key, cached, clear_cache
from database.models import NotifModel

from datetime import datetime, timedelta

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

"""
    id: Mapped[int_pk]
    date: Mapped[dtime]
    user_id: Mapped[int]
    text: Mapped[str]
    repeat_daily: Mapped[bool] = mapped_column(default=False)
    repeat_weekly: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
"""


async def add_notif(
    session: AsyncSession,
    date: datetime,
    user_id: int,
    text: str | None = "",
    repeat_daily: bool | None = False,
    repeat_weekly: bool | None = False,
) -> None:
    """Add a new user to the database."""
    date: datetime
    user_id: int = user_id
    text: str | None = text
    repeat_daily: bool | None = repeat_daily
    repeat_weekly: bool | None = repeat_weekly

    new_notif = NotifModel(
        date=date,
        user_id=user_id,
        text=text,
        repeat_daily=repeat_daily,
        repeat_weekly=repeat_weekly,
    )

    session.add(new_notif)
    await session.commit()
    #await clear_cache()


async def get_notif(session: AsyncSession, id: int) -> NotifModel:
    query = select(NotifModel).filter_by(id=id)

    result = await session.execute(query)

    user = result.scalar_one_or_none()
    return user


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_user_notifs(session: AsyncSession, user_id: int) -> list[NotifModel]:
    query = select(NotifModel).filter_by(user_id=user_id)

    result = await session.execute(query)

    notifs = result.scalars()
    return list(notifs)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def count_user_notifs(session: AsyncSession, user_id: int) -> int:
    query = select(NotifModel).filter_by(user_id=user_id)

    result = await session.execute(query)

    count = result.scalar_one_or_none() or 0
    return count


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_notif_text(session: AsyncSession, id: int) -> None:
    query = select(NotifModel.text).filter_by(id=id)

    result = await session.execute(query)

    text = result.scalar_one_or_none()
    return text or ""


async def update_notif(session: AsyncSession,
                       id: int,
                       date: datetime | None = None,
                       text: str | None = None,
                       repeat_daily: bool | None = None,
                       repeat_weekly: bool | None = None,
                        ) -> None:
    notification = await get_notif(session, id)
    if date is not None:
        notification.date = date
    if text is not None:
        notification.text = text
    if repeat_daily is not None:
        notification.repeat_daily = repeat_daily
    if repeat_weekly is not None:
        notification.repeat_weekly = repeat_weekly

    stmt = update(NotifModel).where(NotifModel.id == id).values(
        date=notification.date,
        text=notification.text,
        repeat_daily=notification.repeat_daily,
        repeat_weekly=notification.repeat_weekly
    )
    await session.execute(stmt)
    await session.commit()


async def update_notif_auto(session: AsyncSession,
                            id: int,
                            ) -> None:
    notification = await get_notif(session, id)

    if notification.repeat_daily:
        notification.date = notification.date + timedelta(days=1)
    elif notification.repeat_weekly:
        notification.date = notification.date + timedelta(days=7)
    else:
        notification.date = notification.date + timedelta(days=30)

    stmt = update(NotifModel).where(NotifModel.id == id).values(
        date=notification.date,
    )
    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_notif, id)


@cached(key_builder=lambda session: build_key())
async def get_all_notifs(session: AsyncSession) -> list[NotifModel]:
    query = select(NotifModel)

    result = await session.execute(query)

    users = result.scalars()
    return list(users)


@cached(key_builder=lambda session: build_key())
async def count_notif(session: AsyncSession) -> int:
    query = select(func.count()).select_from(NotifModel)

    result = await session.execute(query)

    count = result.scalar_one_or_none() or 0
    return int(count)
