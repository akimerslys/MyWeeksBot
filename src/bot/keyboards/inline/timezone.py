from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _


# TODO make reply keyboard with all timezones


def timezone_simple_keyboard(user_logged: bool = False) -> InlineKeyboardMarkup:
    tmp = 'set_new_timezone_'
    if user_logged:
        tmp = 'set_timezone_'
    buttons = [
        [InlineKeyboardButton(text="🇬🇧 London/UTC", callback_data=f"{tmp}UTC")],
        [InlineKeyboardButton(text="🇪🇺 Europe", callback_data=f"{tmp}Europe/Berlin")],
        [InlineKeyboardButton(text="🇺🇦 Ukraine/Kyiv", callback_data=f"{tmp}Europe/Kyiv")],
        [InlineKeyboardButton(text="  ️ Moscow", callback_data=f"{tmp}Europe/Moscow")],
        [InlineKeyboardButton(text=_("timezone_by_location") + " (beta)",
                              callback_data=f"timezone_send_geo_{str(user_logged)}")],
        [InlineKeyboardButton(text=_("timezone_country") + "(beta)", callback_data="timezone_country")],
        [InlineKeyboardButton(text=_("timezone_adv"), callback_data="timezone_show_adv_1")]
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    if user_logged:
        keyboard.button(text=_("back"), callback_data="settings_kb"),
    else:
        keyboard.button(text=_("back"), callback_data="start_kb")
    keyboard.adjust(2, 2, 1, 1, 1)
    return keyboard.as_markup(resize_keyboard=True)


def timezone_advanced_keyboard(first_page: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if first_page:
        for i in range(11):
            builder.button(text=f"GMT+{i + 1}", callback_data=f"set_timezone_Etc/GMT+{i + 1}")

        builder.button(text=f"More...", callback_data="timezone_show_adv_2")

    else:
        for i in range(11):
            builder.button(text=f"GMT{i - 12}", callback_data=f"set_timezone_Etc/GMT{i - 12}")

        builder.button(text=f"Less", callback_data="timezone_show_adv_2")

    builder.button(text=_("timezones_all"), callback_data="ignore")
    builder.button(text=_("back"), callback_data="timezone_kb")

    builder.adjust(3, 3, 3, 3, 1, 1, 1)

    return builder.as_markup(resize_keyboard=True)


def timezone_geo_reply() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=_("send_location_btn"),
        request_location=True
    )
    builder.button(text=_("cancel_location_btn"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def ask_location_confirm() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("cancel"), callback_data="cancel_location")
    builder.button(text=_("confirm"), callback_data="confirm_location")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def timezone_country_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇸 United States", callback_data="timezone_country_US")
    builder.button(text="Kazakhstan", callback_data="timezone_country_KZ")
    builder.button(text="🇨🇳 China", callback_data="timezone_country_CN")
    builder.button(text="Brazil", callback_data="timezone_country_BR")
    builder.button(text="🇮🇳 India", callback_data="timezone_country_IN")
    builder.button(text="🇦🇺 Australia", callback_data="timezone_country_AU")
    builder.button(text=_("back"), callback_data="timezone_kb")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup(resize_keyboard=True)


def timezone_country_list_kb(tz_list: list, new_user: bool) -> InlineKeyboardMarkup:
    calldata = "set_timezone_"
    if new_user:
        calldata="set_new_timezone_"
    builder = InlineKeyboardBuilder()
    for tz in tz_list:
        builder.button(text=tz, callback_data=f"{calldata}{tz}")
    builder.button(text=_("back"), callback_data="timezone_kb")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
