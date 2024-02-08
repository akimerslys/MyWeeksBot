from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.filters import Command
from bot import shutdown
from core.config import settings as config
from filters.admin import IsAdmin
from loguru import logger
import asyncio

router = Router(name="stop")


# TODO reformat to restart button (with docker)
@router.message(Command("stop"), IsAdmin(config.ADMINS_ID))
async def stop_bot(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, f"Stopping bot...")
    logger.warning(f"Bot stopping by " + message.from_user.username + " (" + str(message.from_user.id) + ")")
    await shutdown()
