from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


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


def add_keyboard_first() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🌐 Monday", callback_data="day_Monday")],
        [InlineKeyboardButton(text="🌐 Tuesday", callback_data="day_Tuesday")],
        [InlineKeyboardButton(text="🌐 Wednesday", callback_data="day_Wednesday")],
        [InlineKeyboardButton(text="🌐 Thursday", callback_data="day_Thursday")],
        [InlineKeyboardButton(text="🌐 Friday", callback_data="day_Friday")],
        [InlineKeyboardButton(text="🌐 Saturday", callback_data="day_Saturday")],
        [InlineKeyboardButton(text="🌐 Today", callback_data="day_Today")],
        [InlineKeyboardButton(text="🌐 Sunday", callback_data="day_Sunday")],
        [InlineKeyboardButton(text="🕔 Calendar", callback_data="open_calendar")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(2, 2, 2, 3, 1)
    return keyboard.as_markup(resize_keyboard=True)


def hours_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index in range(0, 24):
        builder.button(
            text=f"{'0' if index<=9 else ''}{index}:",
            callback_data=f"set_hours_{index}"
        )
    builder.adjust(4, 4, 4, 4, 4, 4, 1)
    return builder.as_markup(resize_keyboard=True)


def minute_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index in range(0, 12):
        builder.button(
            text=f"{'0' if index<=1 else ''}{index*5}",
            callback_data=f"set_minute_{'0' if index<=1 else ''}{index*5}"
        )
    builder.adjust(4, 4, 4, 4, 4, 4, 1)
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
