from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _


def start_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=_("Language"), callback_data="new_lang_kb"))
    builder.add(InlineKeyboardButton(text=_("Timezone"), callback_data="new_timezone_kb"))
    builder.add(InlineKeyboardButton(text=_("guide"), callback_data="guide_page_1"))
    builder.add(InlineKeyboardButton(text=_("complete_registration"), callback_data="reg_complete"))
    builder.adjust(2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def new_lang_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🇬🇧 English", callback_data="set_new_lang_en"))
    builder.add(InlineKeyboardButton(text="🇺🇦 Українська", callback_data="set_new_lang_ru"))
    builder.add(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_new_lang_uk"))
    builder.add(InlineKeyboardButton(text=_("more_lang"), callback_data="set_new_lang_add"))
    builder.add(InlineKeyboardButton(text=_("back"), callback_data="start_kb"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def guide_start_kb(page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.adjust(2)
    if page != 1:
        builder.add(InlineKeyboardButton(text=_("Prev"), callback_data=f"guide_page_{page-1}"))

    if page != 3:
        builder.add(InlineKeyboardButton(text=_("Next"), callback_data=f"guide_page_{page+1}"))
    else:
        builder.add(InlineKeyboardButton(text=_("Complete"), callback_data="guide_complete"))

    return builder.as_markup(resize_keyboard=True)
