from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _


# TODO make reply keyboard with all timezones


def timezone_simple_keyboard(user_exist: bool = True) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("🇬🇧 London/UTC"), callback_data="set_timezone_UTC")],
        [InlineKeyboardButton(text=_("🇪🇺 Europe"), callback_data="set_timezone_Europe/Berlin")],
        [InlineKeyboardButton(text=_("🇺🇦 Ukraine/Kyiv"), callback_data="set_timezone_Europe/Kyiv")],
        [InlineKeyboardButton(text=_("  ️ Moscow"), callback_data="set_timezone_Europe/Moscow")],
        [InlineKeyboardButton(text=_("🌍 ShowAll timezones"), callback_data="timezone_show_adv")],
        [InlineKeyboardButton(text=_("📍 Timezone by your Location(beta)"), callback_data="timezone_send_geo")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    if user_exist:
        keyboard.button(text="⬅️ Back", callback_data="settings_kb"),
    keyboard.adjust(2, 2, 1, 1, 1)
    return keyboard.as_markup(resize_keyboard=True)


def timezone_advanced_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(13):
        builder.button(text=f"GMT{i - 12}", callback_data=f"set_timezone_Etc/GMT{i - 12}")

    builder.button(text="GMT+0", callback_data="set_timezone_UTC")

    for i in range(11):
        builder.button(text=f"GMT{i + 1}", callback_data=f"set_timezone_Etc/GMT+{i + 1}")

    builder.button(text=_("Timezone by country (beta)"), callback_data="timezone_country")
    builder.button(text=_("All timezones"), callback_data="timezone_all")
    builder.button(text=_("back"), callback_data="timezone_kb")
    builder.adjust(6, 6, 1, 1)
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
