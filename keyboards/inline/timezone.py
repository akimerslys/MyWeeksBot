from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from services.users import get_timezone
from datetime import datetime, timedelta, tzinfo, timezone

#TODO make reply keyboard with all timezones


def timezone_simple_keyboard(user_exist: bool = True) -> InlineKeyboardMarkup:
    buttons = [
            [InlineKeyboardButton(text="🇬🇧 London/UTC", callback_data="set_timezone_UTC")],
            [InlineKeyboardButton(text="🇪🇺 Europe", callback_data="set_timezone_Europe/Berlin")],
            [InlineKeyboardButton(text="🇺🇦 Ukraine/Kyiv", callback_data="set_timezone_Europe/Kyiv")],
            [InlineKeyboardButton(text="🏳️ Moscow", callback_data="set_timezone_Europe/Moscow")],
            [InlineKeyboardButton(text="🌍 ShowAll timezones", callback_data="show_all")],
            [InlineKeyboardButton(text="📍 Timezone by your Location(beta)", callback_data="send_geo")],
        ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    if user_exist:
        keyboard.button(text="⬅️ Back", callback_data="settings_kb"),
    keyboard.adjust(2, 2, 1, 1, 1)
    return keyboard.as_markup(resize_keyboard=True)


# TODO REWORK THIS
def timezone_advanced_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index in range(0, 24):
        builder.button(
            text=f"🕙 GMT {'+' if index - 12 >= 0 else ''}{index - 12}",
            callback_data=f"set_timezone_{index-12}"
        )
    builder.button(text="⬅️ Back", callback_data="timezone_kb")
    builder.adjust(4, 4, 4, 4, 4, 4, 4, 4, 1)
    return builder.as_markup(resize_keyboard=True)


def timezone_geo_reply() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="Send location",
        request_location=True
    )
    builder.button(text="⬅️ Cancel")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def ask_location_confirm() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Confirm", callback_data="confirm_location")
    builder.button(text="⬅️ Cancel", callback_data="cancel_location")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)