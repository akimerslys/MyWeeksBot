import os

from aiogram import Router, Bot
from aiogram.types import ErrorEvent, FSInputFile, CallbackQuery, InlineQuery, Message
from loguru import logger

from src.core.config import settings


router = Router(name="error_handler")


@router.errors()
async def error_handler(event: ErrorEvent, bot: Bot):

    userid = 0
    username: str = 'unknown'

    logger.error(f"Error: {event.exception}")
    logger.error(f"Update: {event.update}")

    types = {
        "message": Message,
        "callback_query": CallbackQuery,
        "inline_query": InlineQuery,
    }

    for type_ in types:
        try:
            # Access the attribute directly from the update object
            event_type = getattr(event.update, type_, None)
            if event_type:
                userid = event_type.from_user.id
                username = event_type.from_user.username
                print(f"Type of update: {type_}, User ID: {userid}, Username: {username}")
                break
        except AttributeError:
            pass
    if userid != 0:
        await bot.send_message(userid, "An error occurred while processing your request. We have been notified")

    log_path = os.path.join(settings.LOGS_DIR, "myweeks.log")
    document = FSInputFile(path=log_path, filename="myweeks.log")

    await bot.send_message(settings.ERRORS_CHAT_ID, f"Catch Exception by user: {userid} "
                                      f"(@{username})\n\n"
                                      f"Error: {event.exception}\n\nUpdate: {str(event.update)[:3500]}")
    await bot.send_document(settings.ERRORS_CHAT_ID, document)

    return True
