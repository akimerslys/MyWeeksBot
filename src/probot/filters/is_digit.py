from aiogram.filters import BaseFilter


class IsDigit(BaseFilter):
    def __init__(self, message: str):
        self.message = message

    async def __call__(self, message: str):
        return message.isdigit()
