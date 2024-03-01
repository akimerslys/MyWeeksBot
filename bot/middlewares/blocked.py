from __future__ import annotations
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, InlineQuery, CallbackQuery
from loguru import logger

from bot.services.users import is_blocked

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from sqlalchemy.ext.asyncio import AsyncSession


class BlockedMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:

        session: AsyncSession = data["session"]

        event_type: Message | CallbackQuery | InlineQuery = event
        if event.message:
            event_type: Message = event.message
        elif event.callback_query:
            event_type: CallbackQuery = event.callback_query
        elif event.inline_query:
            event_type: InlineQuery = event.inline_query

        user_id = event_type.from_user.id

        if await is_blocked(session=session, user_id=user_id):
            logger.info(f"User {user_id} is blocked, ignoring!")
            return
        return await handler(event, data)
