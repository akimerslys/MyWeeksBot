from aiogram import Router, Bot
from aiogram.filters import Command
from database import dbusercommands as dbuc

from utils.command import find_command_argument
from core.config import settings

from datetime import datetime, timedelta
from loguru import logger


router = Router(name="premium")


# TODO add anti brutforce ware ?
@router.message(Command("premium"))
async def give_premium(message, bot: Bot):
    if find_command_argument(message.text) == settings.PREMIUM_KEY:
        await dbuc.update_user_premium(message.from_user.id, True, datetime.now() + timedelta(days=30))
        await bot.send_message(message.from_user.id, "🎉 Your 30days premium has been activated!")
        logger.success(f"User {message.from_user.id} has activated premium by key")
    else:
        logger.warning(f"User {message.from_user.id} has tried to activate premium by key")
    await bot.delete_message(message.from_user.id, message.message_id)