from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from utils.command import find_command_argument
from filters.admin import IsAdmin
from core.config import settings
from services.keys import add_key

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
