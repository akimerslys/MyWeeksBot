from aiogram import Router, Bot
from aiogram.types import Message, TextQuote
from aiogram.filters import CommandStart
from keyboards.inline.menu import main_kb
from keyboards.inline.timezone import timezone_simple_keyboard

from database.dbusercommands import add_user, user_exists

from git import Repo

router = Router(name="start")


@router.message(CommandStart())
async def start_message(message: Message, bot: Bot):
    last_commit = Repo('C:/Work/MyWeeksBot').head.commit
    await bot.send_message(message.from_user.id,
                           f"Hi There, Welcome to MyWeeksBot\n\nLast Update:\n{last_commit.committed_datetime.strftime('%H:%M %d/%m/%Y')} by {last_commit.author}:\n{last_commit.message}")
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



