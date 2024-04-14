from __future__ import annotations
from typing import Any, Awaitable, Callable
from loguru import logger

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache

from src.core.config import settings

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
        if not isinstance(event, Message):
            return await handler(event, data)
        if event.chat.id in self.cache:
            logger.warning(f"Throttling event from chat {event.chat.id}")
            return None
        self.cache[event.chat.id] = None
        return await handler(event, data)


