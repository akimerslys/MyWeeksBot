import asyncio

import uvloop
from loguru import logger

from src.core.config import settings
from src.bot.loader import dp, bot

from src.bot.handlers import get_handlers_router
from src.bot.keyboards.default_commands import remove_default_commands, set_default_commands
from src.bot.middlewares import register_middlewares

if settings.USE_WEBHOOK:
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from src.bot.loader import app
    from aiohttp import web
else:
    from arq import create_pool

async def on_startup() -> None:
    logger.info("bot starting...")

    register_middlewares(dp)

    dp.include_router(get_handlers_router())

    await set_default_commands(bot)

    logger.success(f"bot started")


async def setup_webhook() -> None:
    logger.info(f"Starting web app on {settings.WEBHOOK_HOST}:{settings.WEBHOOK_PORT}")
    await bot.set_webhook(
        settings.webhook_uri,
        allowed_updates=dp.resolve_used_update_types(),
        secret_token=settings.WEBHOOK_SECRET,
    )

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET,
    )

    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=settings.WEBHOOK_HOST, port=settings.WEBHOOK_PORT)
    await site.start()

    logger.success(f"App started on {settings.WEBHOOK_HOST}:{settings.WEBHOOK_PORT}")

    await asyncio.Event().wait()


async def on_shutdown() -> None:

    logger.warning("bot stopping...")

    await remove_default_commands(bot)

    await dp.storage.close()
    await dp.fsm.storage.close()

    await bot.delete_webhook()
    await bot.session.close()
    #await close_orm()

    logger.warning("bot stopped")


async def main() -> None:
    logger.add(
        f"{settings.LOGS_DIR}/myweeks.log",
        level="DEBUG",
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        rotation="00:03",
        compression="zip",
        backtrace=True
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    if settings.USE_WEBHOOK:
        await setup_webhook()
    else:
        redis_pool = await create_pool(settings.redis_pool)
        await dp.start_polling(bot, arqredis=redis_pool)


if __name__ == "__main__":
    uvloop.run(main())
