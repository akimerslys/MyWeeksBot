from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _


from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards.inline.menu import main_kb
from bot.keyboards.inline.timezone import timezone_simple_keyboard
from bot.services.users import user_exists

router = Router(name="start")


@router.message(CommandStart())
async def start_message(message: Message, bot: Bot, session: AsyncSession):
    logger.info(f"User {message.from_user.id} started bot")
    await bot.send_message(
        message.from_user.id,
        _("start_msg"))
    if not await user_exists(session, message.from_user.id):
        await bot.send_message(
            message.from_user.id,
            _("choose_timezone"),
            reply_markup=timezone_simple_keyboard(False)
        )
    else:
        await bot.send_message(
            message.from_user.id,
            _("pls_choose_option"),
            reply_markup=main_kb()
        )



