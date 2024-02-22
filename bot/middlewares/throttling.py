from __future__ import annotations
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from cachetools import TTLCache

from bot.core.config import settings

# TODO add callbackquery throttling


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = settings.RATE_LIMIT) -> None:
        self.cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) or isinstance(event, CallbackQuery):
            if event.chat.id in self.cache:
                return None
            self.cache[event.chat.id] = None

        return await handler(event, data)


