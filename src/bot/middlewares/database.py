from __future__ import annotations
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware

from src.database.engine import sessionmaker

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import Update


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        async with sessionmaker() as session:
            data["session"] = session
            return await handler(event, data)
