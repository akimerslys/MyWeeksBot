from datetime import datetime, timedelta
from pytz import timezone as tz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from pytz import common_timezones


def main_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📈 Add Notification", callback_data="add")],
        [InlineKeyboardButton(text="📊 Remove Notification", callback_data="remove")],
        [InlineKeyboardButton(text="📚 Settings", callback_data="settings_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def back_main() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def setting_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🌐 Language", callback_data="lang_kb")],
        [InlineKeyboardButton(text="🕔 Timezone", callback_data="timezone_kb")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def language_kb() -> InlineKeyboardMarkup:
    buttons = [
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
            [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="set_lang_uk")],
            [InlineKeyboardButton(text="🇷🇺 Руzzкий", callback_data="set_lang_ru")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="settings_kb")],
        ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_keyboard_first(timezone_str: str = "UTC") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    time_now = datetime.now(tz(timezone_str))
    current_day_index = time_now.weekday()

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    sorted_days = days_of_week[current_day_index:] + days_of_week[:current_day_index]

    for i, day in enumerate(sorted_days):
        builder.button(
            text=f"{day}{' (Today)' if i == 0 else ' (' + (time_now + timedelta(days=i)).strftime('%d.%m') + ')'} ",
            callback_data=f"day_{(time_now + timedelta(days=i)).strftime('%Y %m %d')}"
        )
    builder.button(text="Calendar", callback_data="open_calendar")
    builder.button(text="⬅️ Back", callback_data="main_kb")

    builder.adjust(1, 2, 2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def hours_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index in range(0, 24):
        builder.button(
            text=f"{index}:00",
            callback_data=f"set_hours_{index}"
        )
    builder.adjust(1, 5, 1, 5, 1, 5, 1, 5)
    return builder.as_markup(resize_keyboard=True)


def minute_kb(hour) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index in range(0, 12):
        builder.button(
            text=f"{hour}:{'0' if index<=1 else ''}{index*5}",
            callback_data=f"set_minute_{'0' if index<=1 else ''}{index*5}"
        )
    builder.adjust(1, 2, 1, 2, 1, 2, 1, 2)
    return builder.as_markup(resize_keyboard=True)


def add_notif_repeat_none_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🕔 Do not repeat", callback_data="repeatable_week")],
        [InlineKeyboardButton(text="✅ Complete",callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_notif_repeat_week_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🕔 Every   Week", callback_data="repeatable_month")],
        [InlineKeyboardButton(text="✅ Complete", callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_notif_repeat_month_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🕔 Every  Month", callback_data="repeatable_none")],
        [InlineKeyboardButton(text="✅ Complete", callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)
