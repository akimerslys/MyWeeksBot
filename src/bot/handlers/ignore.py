from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from loguru import logger

from src.bot.keyboards.inline.menu import main_kb


router = Router()


@router.callback_query(F.data == "ignore")
async def ignore(call: CallbackQuery):
    return


@router.callback_query()
async def found_callback(call: CallbackQuery):
    await call.answer("⚙️ Under construction", show_alert=True)


@router.callback_query()
async def found_callback(call: CallbackQuery):
    logger.error(f"Found unexpected callback: {call.data}, from {call.from_user.username} ({call.from_user.id})")
    await call.answer(_("ERROR_MESSAGE"), show_alert=True)
    await call.message.edit_text(_("please_ch_button"), reply_markup=main_kb())