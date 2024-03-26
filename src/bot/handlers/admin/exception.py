import os

from aiogram import Router, Bot
from aiogram.types import ErrorEvent, FSInputFile, CallbackQuery, InlineQuery, Message
from loguru import logger

from src.core.config import settings


router = Router(name="error_handler")


@router.errors()
async def error_handler(event: ErrorEvent, bot: Bot):

    userid: int
    username: str

    logger.error(f"Error: {event.exception}")
    logger.error(f"Update: {event.update}")

    types = {
        "message": Message,
        "callback_query": CallbackQuery,
        "inline_query": InlineQuery,
    }

    for type_ in types:
        if event.update.get(type_):
            userid = event.update[type_].from_user.id
            username = event.update[type_].from_user.username
            break

    if not userid:  userid = 0
    if not username:    username = "unknown"

    await bot.send_message(userid, "An error occurred while processing your request. We have been notified")

    log_path = os.path.join(settings.LOGS_DIR, "myweeks.log")
    document = FSInputFile(path=log_path, filename="myweeks.log")

    for admin in settings.ADMINS_ID:
        await bot.send_message(admin, f"Catch Exception by user: {userid} "
                                      f"(@{username})\n\n"
                                      f"Error: {event.exception}\n\nUpdate: {str(event.update)[:3500]}")
        await bot.send_document(admin, document)

    return True
