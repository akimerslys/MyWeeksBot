from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import Redis, ConnectionPool
from redis.connection import AbstractConnection

from loguru import logger
from core.config import settings

bot = Bot(token=settings.TOKEN, parse_mode=ParseMode.HTML)





if settings.USE_REDIS:
    logger.info("loading redis")
    redis_client = Redis(
        connection_pool=ConnectionPool.from_url(settings.redis_url)
    )

    storage = RedisStorage(
        redis=redis_client,
        key_builder=DefaultKeyBuilder(with_bot_id=True),
    )
else:
    from aiogram.fsm.storage.memory import MemoryStorage
    storage = MemoryStorage()


dp = Dispatcher(storage=storage)
logger.success("storage loaded")
#i18n

DEBUG = settings.DEBUG
