from aiogram import Router, Bot
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from services.users import set_user_premium, is_premium
from services.keys import use_key, get_key_days
from utils.command import find_command_argument

from loguru import logger


router = Router(name="premium")


# TODO add anti brutforce middleware ?
@router.message(Command("premium"))
async def give_premium(message, bot: Bot, session: AsyncSession):
    args = find_command_argument(message.text)
    await bot.delete_message(message.from_user.id, message.message_id)
    if not args:
        return

    if await use_key(session, args, message.from_user.id):
        days = await get_key_days(session, args)
        await bot.send_message(message.from_user.id, f"🎉 Your {days}d premium has been {'extended!' if await is_premium(session, message.from_user.id) else 'activated' }")
        await set_user_premium(session, message.from_user.id, days)
        logger.success(f"User {message.from_user.id} has activated premium by key")
    else:
        logger.warning(f"User {message.from_user.id} has tried to activate premium by key")
