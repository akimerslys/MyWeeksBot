from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from keyboards.inline.menu import main_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def start_message(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, "Hi There, Welcome to MyWeeksBot\nHope you enjoy\nAHAHAHAHAHA")
    await bot.send_message(
        message.from_user.id,
        "Please choose an option from the menu below",
        reply_markup=main_keyboard()
    )
