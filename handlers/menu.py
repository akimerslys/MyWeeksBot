from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from keyboards.inline.menu import main_keyboard, setting_keyboard, language_keyboard
from loguru import logger
router = Router(name="menu")


@router.callback_query(F.data == 'settings_kb')
async def settings(call: CallbackQuery):
    await call.message.edit_text("🔧 Choose Settings", reply_markup=setting_keyboard())


@router.callback_query(F.data == "lang_kb")
async def choose_language(call: CallbackQuery):
    await call.message.edit_text("🌐 Choose your language", reply_markup=language_keyboard())


@router.callback_query(F.data == "main_kb")
async def menu_back(call: CallbackQuery):
    await call.message.edit_text("⤵️ Please choose an option from the menu below", reply_markup=main_keyboard())


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(call: CallbackQuery):
    print(call)
    await call.message.edit_text(f"🌐 Language changed to {call.data}\n\nif you see this message, everything ok, thank you :)", reply_markup=language_keyboard())


@router.callback_query(F.data == "timezone_kb")
async def choose_timezone(call: CallbackQuery):
    await call.answer("⚙️ This function is not available yet")


@router.callback_query()
async def found_callback(call: CallbackQuery):
    logger.error(f"Found unexpected callback: {call.data}, from {call.from_user.username} ({call.from_user.id})")
    await call.answer("⚙️ Under development")
