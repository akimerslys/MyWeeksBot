from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from database.database import db

from core.config import settings

bot = Bot(token=settings.TOKEN, parse_mode=ParseMode.HTML)

storage = MemoryStorage()

dp = Dispatcher(storage=storage)


__all__ = ["bot", "storage", "dp", "db"]