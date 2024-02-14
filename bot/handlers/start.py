from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline.menu import main_kb
from bot.keyboards.inline.timezone import timezone_simple_keyboard

from bot.services.users import add_user, user_exists

router = Router(name="start")


@router.message(CommandStart())
async def start_message(message: Message, bot: Bot, session: AsyncSession):
    logger.info(f"User {message.from_user.id} started bot")
    await bot.send_message(
        message.from_user.id,
        f"Hi There, Welcome to MyWeeksBot (pre-dev)\n"
        f"If you see any bug, please report it using /report")
    if not await user_exists(session, message.from_user.id):
        await add_user(session, message.from_user.id, message.from_user.first_name, message.from_user.language_code)
        await bot.send_message(
            message.from_user.id,
            "Please choose your timezone below",
            reply_markup=timezone_simple_keyboard(False)
        )
    else:
        await bot.send_message(
            message.from_user.id,
            "Please choose an option from the menu below",
            reply_markup=main_kb()
        )



