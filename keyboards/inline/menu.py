from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📈 Add Notification", callback_data="add")],
        [InlineKeyboardButton(text="📊 Remove Notification", callback_data="remove")],
        [InlineKeyboardButton(text="📚 Settings", callback_data="settings_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)



def setting_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🌐 Language", callback_data="lang_kb")],
        [InlineKeyboardButton(text="🕔 Timezone", callback_data="timezone_kb")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def language_keyboard() -> InlineKeyboardMarkup:
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
        [InlineKeyboardButton(text="🌐 Monday", callback_data="day_mon")],
        [InlineKeyboardButton(text="🌐 Tuesday", callback_data="day_tue")],
        [InlineKeyboardButton(text="🌐 Wednesday", callback_data="day_wed")],
        [InlineKeyboardButton(text="🌐 Thursday", callback_data="day_thu")],
        [InlineKeyboardButton(text="🌐 Friday", callback_data="day_fri")],
        [InlineKeyboardButton(text="🌐 Saturday", callback_data="day_sat")],
        [InlineKeyboardButton(text="🌐 Sunday", callback_data="day_sun")],
        [InlineKeyboardButton(text="🕔 Add specific date", callback_data="open_calendar")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(3, 3, 1, 1, 1)
    return keyboard.as_markup(resize_keyboard=True)

