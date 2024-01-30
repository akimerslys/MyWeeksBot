from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode


from core.config import settings

bot = Bot(token=settings.TOKEN, parse_mode=ParseMode.HTML)

dp = Dispatcher()
