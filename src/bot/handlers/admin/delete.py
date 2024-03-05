from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.methods import get_chat
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.utils.command import find_command_argument
from src.bot.filters.admin import IsAdmin
from src.core.config import settings
from src.bot.services.users import delete_user

from loguru import logger


router = Router(name="delete")


@router.message(Command("delete"), IsAdmin(settings.ADMINS_ID))
async def generating_key(message: Message, bot: Bot, session: AsyncSession):
    user = find_command_argument(message.text)
    await bot.delete_message(message.chat.id, message.message_id)
    if user:
        await delete_user(session, int(user))
    else:
        await delete_user(session, message.from_user.id)
