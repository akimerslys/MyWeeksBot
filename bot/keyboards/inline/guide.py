from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton


def guide_start_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=" ", callback_data="ignore"))
    builder.add(InlineKeyboardButton(text="Next", callback_data="guide_page_2"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
