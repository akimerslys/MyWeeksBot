import asyncio
from loguru import logger

from core.config import settings
from core.loader import dp, bot
from database.engine import create_async_engine, create_sessionmaker
from handlers import get_handlers_router
from keyboards.default_commands import remove_default_commands, set_default_commands
from middlewares import register_middlewares


async def startup() -> None:
    logger.info("bot starting...")
    register_middlewares(dp)
    dp.include_router(get_handlers_router())

    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    logger.success(f"bot started as @{bot_info.username}")


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
        rotation="10 MB",
        compression="zip",
            )

    dp.startup.register(startup)

    dp.shutdown.register(shutdown)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
