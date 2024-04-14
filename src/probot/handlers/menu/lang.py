from __future__ import annotations

from aiogram import Router, F
from aiogram.utils.i18n import gettext as _
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.keyboards.inline import menu as mkb
from src.database.services import prousers as dbuc

router = Router(name="lang")


@router.callback_query(F.data == "lang_kb")
async def choose_language_kb(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=mkb.language_kb())


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language_kb(call: CallbackQuery, session: AsyncSession):
    await call.message.edit_text(_("WAIT_MESSAGE"))
    await call.message.edit_text(
        _("lang_changed") + ' ' + _("language"),
        reply_markup=mkb.setting_kb()
    )
    if await dbuc.get_language_code(session, call.from_user.id) != call.data[9:]:
        await dbuc.set_language_code(session, call.from_user.id, call.data[9:])


@router.callback_query(F.data == "add_lang")
async def add_language_kb(call: CallbackQuery):
    await call.answer(
        "⚙️ This function is not available yet\nSoon u will have ability to add your own language",
        show_alert=True)