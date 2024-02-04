from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta, tzinfo, timezone


def timezone_simple_keyboard() -> InlineKeyboardMarkup:
    buttons = [
            [InlineKeyboardButton(text="🌐 GMT 0 (London)", callback_data="set_timezone_0")],
            [InlineKeyboardButton(text="🌐 GMT +1 (Europe)", callback_data="set_timezone_1")],
            [InlineKeyboardButton(text="🌐 GMT +2 (Ukraine)", callback_data="set_timezone_2")],
            [InlineKeyboardButton(text="🌐 GMT +3 (Moscow)", callback_data="set_timezone_3")],
            [InlineKeyboardButton(text="🌐 ShowAll timezone", callback_data="show_all")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="settings_kb")],
        ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def timezone_advanced_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index in range(0, 24):
        builder.button(
            text=f"🌐 GMT {'+' if index - 12 >= 0 else ''}{index - 12}",
            callback_data=f"set_timezone_{index-12}"
        )
    builder.button(text="⬅️ Back", callback_data="timezone_kb")
    builder.adjust(4, 4, 4, 4, 4, 4, 4, 4, 1)
    return builder.as_markup(resize_keyboard=True)
