from aiogram.filters import BaseFilter
from aiogram.types import Message
from typing import List


class IsAdmin(BaseFilter):
    def __init__(self, user_ids: int | List[int]):
        self.user_ids = user_ids

    async def __call__(self, message: Message):
        if isinstance(self.user_ids, int):
            return message.from_user.id == self.user_ids
        return message.from_user.id in self.user_ids
