from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardButton
from aiogram.utils.keyboard import KeyboardBuilder


def skip_kb() -> ReplyKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.add(ReplyKeyboardButton(text="Skip"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
