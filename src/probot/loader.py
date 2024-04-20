import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.utils.i18n import I18n
from aiohttp import web
#from fastapi import FastAPI
from hltv_async_api import Hltv

from loguru import logger
from src.core.redis_loader import redis_client
from src.core.config import settings


if settings.USE_WEBHOOK:
    app = web.Application()

bot = Bot(token=settings.PROBOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

i18n: I18n = I18n(path=settings.LOCALES_DIR, default_locale="en", domain=settings.I18N_DOMAIN)

storage = RedisStorage(
    redis=redis_client,
    key_builder=DefaultKeyBuilder(with_bot_id=True),
)

lock = asyncio.Lock()

dp = Dispatcher(storage=storage)
logger.success("storage initialized")

# CONFIG TO .ENV!!!
if settings.PROXY:
    hltv = Hltv(max_delay=5, proxy_path=settings.PROXY, debug=settings.DEBUG)
else:
    hltv = Hltv(max_delay=5, debug=settings.DEBUG)
