import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis, ConnectionPool

from loguru import logger
from bot.core.config import settings

bot = Bot(token=settings.TOKEN, parse_mode=ParseMode.HTML)


logger.info("loading redis")
redis_client = Redis(
    connection_pool=ConnectionPool.from_url(settings.redis_url)
)

storage = RedisStorage(
    redis=redis_client,
    key_builder=DefaultKeyBuilder(with_bot_id=True),
)

lock = asyncio.Lock()

dp = Dispatcher(storage=storage)
logger.success("storage loaded")

i18n: I18n = I18n(path=settings.LOCALES_DIR, default_locale="en", domain=settings.I18N_DOMAIN)

DEBUG = settings.DEBUG
