from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.utils.command import find_command_argument
from src.bot.filters.admin import IsAdmin
from src.core.config import settings
from src.database.services.keys import add_key

from loguru import logger


router = Router(name="add_key")


@router.message(Command("add_key", "key_add"), IsAdmin(settings.ADMINS_ID))
async def generating_key(message: Message, bot: Bot, session: AsyncSession):
    days = find_command_argument(message.text)
    await bot.delete_message(message.chat.id, message.message_id)
    if days:
        if not days.isdigit() or int(days) < 1:
            await bot.send_message(message.from_user.id, "Invalid argument")
            return
    await bot.send_message(
        message.from_user.id, f"{'' + await add_key(session) if not days else '' + await add_key(session, int(days))}")
    logger.info(f"@{message.from_user.username}({message.from_user.id}) created new key")


