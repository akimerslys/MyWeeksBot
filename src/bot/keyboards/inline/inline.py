from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

def inline_add(link: str):
    buttons = [
        [InlineKeyboardButton(text=_("add_notif_inline"), url=link)]
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def inline_schedule_add(link: str):
    buttons = [
        [InlineKeyboardButton(text=_("add_schedule_inline"), url=link)]
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)