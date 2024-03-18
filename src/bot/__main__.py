import asyncio
from datetime import timedelta

from arq.connections import create_pool
from loguru import logger

from src.bot.scheduler.main import WorkerSettings
from src.core.config import settings
from src.bot.loader import dp, bot

from src.bot.handlers import get_handlers_router
from src.bot.keyboards.default_commands import remove_default_commands, set_default_commands
from src.bot.middlewares import register_middlewares


async def startup() -> None:
    logger.info("bot starting...")
    register_middlewares(dp)
    dp.include_router(get_handlers_router())

    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    logger.success(f"bot started")


async def shutdown() -> None:

    logger.warning("bot stopping...")

    await remove_default_commands(bot)

    #await db.pop_bind().close()

    await dp.storage.close()
    await dp.fsm.storage.close()

    await bot.session.close()

    # await close_orm()

    logger.warning("bot stopped")


async def main() -> None:

    logger.add(
        "logs/myweeks.log",
        level="DEBUG",
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        rotation="00:03",
        compression="zip",
        backtrace=True
    )

    redis_pool = await create_pool(settings.redis_pool)

    dp.startup.register(startup)

    dp.shutdown.register(shutdown)

    #worker = WorkerSettings()
    #await worker.run(redis_pool)

    await dp.start_polling(bot, arqredis=redis_pool)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
