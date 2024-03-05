import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.utils.i18n import I18n

from loguru import logger
from src.core.config import settings
from src.core.redis_loader import redis_client

bot = Bot(token=settings.TOKEN, parse_mode=ParseMode.HTML)


logger.info("loading redis")

storage = RedisStorage(
    redis=redis_client,
    key_builder=DefaultKeyBuilder(with_bot_id=True),
)

lock = asyncio.Lock()

dp = Dispatcher(storage=storage)
logger.success("storage loaded")

i18n: I18n = I18n(path=settings.LOCALES_DIR, default_locale="en", domain=settings.I18N_DOMAIN)

DEBUG = settings.DEBUG
