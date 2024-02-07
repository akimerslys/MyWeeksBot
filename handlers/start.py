from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from keyboards.inline.menu import main_kb
from keyboards.inline.timezone import timezone_simple_keyboard

from database.dbusercommands import add_user, user_exists

router = Router(name="start")


@router.message(CommandStart())
async def start_message(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, "Hi There, Welcome to MyWeeksBot\nI will help you to manage your time")
    if not await user_exists(message.from_user.id):
        await add_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.language_code,
        )
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



