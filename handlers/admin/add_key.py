from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message

from utils.command import find_command_argument
from filters.admin import IsAdmin
from filters.is_digit import IsDigit
from core.config import settings
from database import db_key_commands as dbkey

from loguru import logger

router = Router(name="add_key")


@router.message(Command("add_key", "key_add"), IsAdmin(settings.ADMINS_ID))
async def add_key(message: Message, bot: Bot):
    days = find_command_argument(message.text)
    await bot.delete_message(message.chat.id, message.message_id)
    if days:
        if not days.isdigit():
            await bot.send_message(message.from_user.id, "Invalid argument")
            return
    await bot.send_message(
        message.from_user.id, f"{'' + await dbkey.add_key() if not days else '' + await dbkey.add_key(int(days))}")
    logger.info(f"@{message.from_user.username}({message.from_user.id}) created new key")
