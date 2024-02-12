from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline.menu import main_kb
from keyboards.inline.timezone import timezone_simple_keyboard

from services.users import add_user, user_exists
from utils.last_commits import get_changelog


router = Router(name="start")


@router.message(CommandStart())
async def start_message(message: Message, bot: Bot, session: AsyncSession):
    changelog = await get_changelog(1)
    message_start = f"Hi There, Welcome to MyWeeksBot\n\nLast Update:\n\n{''.join(changelog)}use /changelog to see more"
    await bot.send_message(message.from_user.id, message_start)
    if not await user_exists(session, message.from_user.id):
        await add_user(session, message.from_user.id, message.from_user.first_name, message.from_user.language_code)
        await bot.send_message(
            message.from_user.id,
            "Please choose your timezone below",
            reply_markup=timezone_simple_keyboard()
        )
    else:
        await bot.send_message(
            message.from_user.id,
            "Please choose an option from the menu below",
            reply_markup=main_kb()
        )



