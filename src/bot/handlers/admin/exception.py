from aiogram import Router, Bot
from aiogram.types import ErrorEvent
from loguru import logger

from src.core.config import settings


router = Router(name="error_handler")


@router.errors()
async def error_handler(event: ErrorEvent, bot: Bot):

    userid: int
    username: str


    logger.error(f"Error: {event.exception}")
    logger.error(f"Update: {event.update}")

    if event.update.message:
       userid = event.update.message.from_user.id
       username = event.update.message.from_user.username

    elif event.update.callback_query:
        userid = event.update.callback_query.from_user.id
        username = event.update.callback_query.from_user.username
    else:
        for admin in settings.ADMINS_ID:
            await bot.send_message(admin, f"Error: {event.exception}\n\nUpdate: {event.update}")
        return True

    await bot.send_message(userid, "An error occurred while processing your request. Please try again later.")

    for admin in settings.ADMINS_ID:
        await bot.send_message(admin, f"Catch Exception by user: {userid} "
                                      f"(@{username})\n\n"
                                      f"Error: {event.exception}\n\nUpdate: {event.update[:3500]}")

    return True
