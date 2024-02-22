from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from typing import Callable, Dict, Any, Awaitable, TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime, timedelta


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.callbacks = {}

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        callback_data = event.data

        if user_id not in self.callbacks:
            self.callbacks[user_id] = {callback_data: event.message.date}
        elif callback_data not in self.callbacks[user_id]:
            self.callbacks[user_id][callback_data] = event.message.date
        else:
            # If the same callback from the same user within 1 second, discard it
            prev_event_date = self.callbacks[user_id][callback_data]
            current_event_date = event.message.date
            if (current_event_date - prev_event_date).total_seconds() < 1:
                return None
            else:
                self.callbacks[user_id][callback_data] = current_event_date

        return await handler(event, data)
