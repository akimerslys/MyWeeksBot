from aiogram import Router, Bot
from aiogram.filters import Command

from bot.utils.last_commits import get_changelog

router = Router(name="changelog")


@router.message(Command("changelog", "change_log", "dev"))
async def send_changelog(message, bot: Bot):
    message_changelog = "".join(await get_changelog(5))
    await bot.send_message(message.from_user.id, message_changelog)
