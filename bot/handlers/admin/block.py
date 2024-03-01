from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.command import find_command_argument
from bot.filters.admin import IsAdmin
from bot.core.config import settings
from bot.services.users import block_user, unblock_user

from loguru import logger


router = Router(name="block")


@router.message(Command("block"), IsAdmin(settings.ADMINS_ID))
async def generating_key(message: Message, bot: Bot, session: AsyncSession):
    user = find_command_argument(message.text)
    await bot.delete_message(message.chat.id, message.message_id)
    if user:
        await block_user(session, int(user))
        await bot.send_message(message.from_user.id, f"User {user} blocked")
        logger.info(f"@{message.from_user.username}({message.from_user.id}) blocked user {user}")
    else:
        await block_user(session, message.from_user.id)
        await bot.send_message(message.from_user.id, "Blocking yourself :D")
        logger.info(f"@{message.from_user.username}({message.from_user.id}) blocked himself")


@router.message(Command("unblock"), IsAdmin(settings.ADMINS_ID))
async def generating_key(message: Message, bot: Bot, session: AsyncSession):
    user = find_command_argument(message.text)
    await bot.delete_message(message.chat.id, message.message_id)
    if user:
        await unblock_user(session, int(user))
        await bot.send_message(message.from_user.id, f"User {user} unblocked")
        logger.info(f"@{message.from_user.username}({message.from_user.id}) unblocked user {user}")
    else:
        await unblock_user(session, message.from_user.id)
        await bot.send_message(message.from_user.id, "unblocking yourself :D")
        logger.info(f"@{message.from_user.username}({message.from_user.id}) unblocked himself")

