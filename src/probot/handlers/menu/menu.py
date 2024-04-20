from __future__ import annotations

from aiogram import Router, F
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.probot.keyboards.inline import menu as mkb
from src.database.services import prousers as dbuc, schedule as dbsc, notifs as dbnc
from src.core.redis_loader import redis_client as redis

router = Router(name="menu")


async def main_menu(call: CallbackQuery):
    main_event = await redis.get("eventf")
    #main_match = await redis.get("matchf")
    await call.message.edit_text(
        _("main_menu"),
        reply_markup=mkb.main_kb(event1=main_event['title'])
    )

# MAIN
@router.callback_query(F.data == "main_kb")
async def menu_back(call: CallbackQuery, state: FSMContext):
    if state.get_state:
        await state.clear()
    await main_menu(call)


@router.callback_query(F.data == 'settings_kb')
async def place_settings_kb(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=mkb.setting_kb())


# CHANGELOG
@router.callback_query(F.data == "show_changelog")
async def send_changelog(call: CallbackQuery):
    #get_updates = await
    message_changelog = ''
    await call.message.edit_text(
        _("last_updates") + "\n\n" + message_changelog,
        reply_markup=mkb.back_main()
    )


# PREMIUM
@router.callback_query(F.data == "buy_premium")
async def buy_premium(call: CallbackQuery):
    await call.answer(
        "not_available",
        show_alert=True
    )


"""@router.message()
async def found_message(message: Message):
    logger.error(f"Found unexpected message: {message.text}, from {message.from_user.username} ({message.from_user.id})")
    print(message)
    await message.answer("⤵️ Please choose an option from the menu below", reply_markup=mkb.main_kb())"""
