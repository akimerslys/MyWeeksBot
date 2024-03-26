from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from typing import Callable, Dict, Any, Awaitable, TYPE_CHECKING

from datetime import datetime, timedelta


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self):
        self.last_callback_data = {}

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        callback_data = event.data
        user_id = event.from_user.id
        now = datetime.now()

        key = f"{user_id}_{callback_data}"

        if (
            key in self.last_callback_data
            and self.last_callback_data[key] + timedelta(seconds=1) >= now
        ):
            return

        self.last_callback_data[key] = now

        return await handler(event, data)
