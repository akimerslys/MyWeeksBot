import asyncio
from loguru import logger
from core.loader import dp, bot
from handlers import get_handlers_router
from keyboards.default_commands import remove_default_commands, set_default_commands
from middlewares import register_middlewares
from core.config import settings
from database.database import on_startup

from aiogram.exceptions import TelegramAPIError


async def startup() -> None:
    logger.info("bot starting...")
    register_middlewares(dp)
    dp.include_router(get_handlers_router())

    await set_default_commands(bot)

    try:
        logger.info("Connecting to PostgreSQL")
        await on_startup(dp)
    except Exception as e:
        logger.error(f"Error while connecting to PostgreSQL: {e}")
        return await shutdown()
    logger.success("Connected to PostgreSQL")

    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()

    logger.success(f"bot started as @{bot_info.username}")


async def shutdown() -> None:

    logger.warning("bot stopping...")

    await remove_default_commands(bot)

    #await db.pop_bind().close()
    await dp.storage.close()

    #await dp.fsm.storage.close()
    await bot.session.close()
    # await close_orm()

    logger.error("bot stopped")


async def main() -> None:
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, TelegramAPIError):
        pass
