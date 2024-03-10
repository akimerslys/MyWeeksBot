from __future__ import annotations
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import func, select, update, asc, delete

from src.cache.redis import build_key, cached, clear_cache
from src.database.models import NotifModel

from src.bot.services.users import inc_user_notifs, dec_user_notifs

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
    logger.info(f"adding notification for user {user_id}")
    new_notif = NotifModel(
        date=date,
        user_id=user_id,
        text=text,
        repeat_daily=repeat_daily,
        repeat_weekly=repeat_weekly,
    )
    await inc_user_notifs(session, user_id)
    session.add(new_notif)
    await session.commit()
    return new_notif.id
    #await clear_cache()


async def get_notif(session: AsyncSession, id_: int) -> NotifModel:
    logger.debug(f"selected notif {id_}")
    query = select(NotifModel).filter_by(id=id_)

    result = await session.execute(query)

    user = result.scalar_one_or_none()
    return user


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_user_notifs(session: AsyncSession, user_id: int) -> list[NotifModel]:
    query = select(NotifModel).filter_by(user_id=user_id).order_by(asc(NotifModel.date))

    result = await session.execute(query)
    logger.debug(f"got user notifs for {result}")
    notifs = result.scalars()
    return list(notifs)


async def get_user_notifs_id(sessions: AsyncSession, user_id: int) -> list:
    
    query = select(NotifModel).filter_by(user_id=user_id).order_by(asc(NotifModel.date))

    result = await session.execute(query)

    logger.debug(f"got user notifs ids for {result}")

    notif_list = result.scalars()
	
    notif_ids = [notif.id for notif in notif_list]

    return list(notif_ids)

async def get_user_notifs_sorted(session: AsyncSession, user_id: int) -> list[tuple]:
    query = select(NotifModel).filter_by(user_id=user_id).order_by(asc(NotifModel.date))

    result = await session.execute(query)

    notif_list = result.scalars()
    logger.debug(f"got user notifs {notif_list}")

    notif_list_sorted = [(notif.date, notif.text, notif.id) for notif in notif_list]

    return notif_list_sorted


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def count_user_notifs(session: AsyncSession, user_id: int) -> int:
    query = select(NotifModel).filter_by(user_id=user_id)

    result = await session.execute(query)
    logger.debug(f"counted user notifs {user_id}")
    count = result.scalar_one_or_none() or 0
    return count


async def get_notif_text(session: AsyncSession, id: int) -> None:
    query = select(NotifModel.text).filter_by(id=id)

    result = await session.execute(query)
    logger.debug(f"got notif text {id}")
    text = result.scalar_one_or_none()
    return text or ""


async def update_notif_text(session: AsyncSession, id: int, text: str) -> None:
    stmt = update(NotifModel).where(NotifModel.id == id).values(text=text)
    logger.debug(f"updated notification text {id}")
    await session.execute(stmt)
    await session.commit()


async def update_notif_active(session: AsyncSession, id: int, active: bool) -> None:
    stmt = update(NotifModel).where(NotifModel.id == id).values(active=active)
    logger.debug(f"updated notification active {id}")
    await session.execute(stmt)
    await session.commit()


async def delete_notif_fake(session: AsyncSession, id: int) -> None:
    user_notif = await get_notif(session, id)
    tmp_id = int("0" + str(user_notif.user_id))
    stmt = update(NotifModel).where(NotifModel.id == id).values(user_id=tmp_id, active=False)
    logger.debug(f"deleted notification {id}")
    await dec_user_notifs(session, user_notif.user_id)
    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_notif, id)


async def get_notifs_by_date(session: AsyncSession, dtime: datetime):
    query = select(NotifModel).filter_by(date=dtime)

    result = await session.execute(query)
    logger.debug(f"got notifs by date {dtime}")
    notifs = result.scalars()
    return list(notifs)


async def update_notif_auto(session: AsyncSession,
                            id: int,
                            ) -> None:
    notification = await get_notif(session, id)

    if not notification.repeat_daily and not notification.repeat_weekly:
        notification.active = False
    elif notification.repeat_daily and not notification.repeat_weekly:
        notification.date = notification.date + timedelta(days=1)
    elif notification.repeat_weekly and not notification.repeat_daily:
        notification.date = notification.date + timedelta(days=7)
    else:
        notification.date = notification.date + timedelta(days=30)

    stmt = update(NotifModel).where(NotifModel.id == id).values(
        date=notification.date,
        active=notification.active
    )
    logger.info(f"updated notification(auto) {id}")
    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_notif, id)


async def get_all_notifs(session: AsyncSession) -> list[NotifModel]:
    query = select(NotifModel)

    result = await session.execute(query)
    logger.debug(f"got all notifs")
    notifs = result.scalars()
    return list(notifs)


async def count_notif(session: AsyncSession) -> int:
    query = select(func.count()).select_from(NotifModel)

    result = await session.execute(query)
    logger.debug(f"counted all notifs")
    count = result.scalar_one_or_none() or 0
    return int(count)


async def delete_all_user_notifs(session: AsyncSession, user_id: int) -> None:
    stmt = delete(NotifModel).where(NotifModel.user_id == user_id)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_user_notifs, user_id)
    await clear_cache(count_user_notifs, user_id)
    await clear_cache(get_notif, user_id)

    logger.info(f"deleted all user notifs {user_id}")
