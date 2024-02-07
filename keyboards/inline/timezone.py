from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from datetime import datetime, timedelta, tzinfo, timezone

#TODO make reply keyboard with all timezones

def timezone_simple_keyboard() -> InlineKeyboardMarkup:
    buttons = [
            [InlineKeyboardButton(text="London/GMT 0", callback_data="set_timezone_UTC")],
            [InlineKeyboardButton(text="Europe/GMT +1", callback_data="set_timezone_Europe/Berlin")],
            [InlineKeyboardButton(text="Ukraine/GMT +2", callback_data="set_timezone_Europe/Kyiv")],
            [InlineKeyboardButton(text="Moscow/GMT +3", callback_data="set_timezone_Europe/Moscow")],
            [InlineKeyboardButton(text="send_timezone", callback_data="send_geo")],
            [InlineKeyboardButton(text="🌐 ShowAll timezones", callback_data="show_all")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="settings_kb")],
        ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(2, 2, 1, 1, 1)
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


def timezone_geo_reply() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="Send location",
        request_location=True
    )
    builder.button(text="⬅️ Cancel")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
