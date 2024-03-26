import logging
from datetime import datetime, timedelta

from loguru import logger
from pytz import timezone as tz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# TODO REWRITE TO NEW CLASS


def main_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_("Match1"), callback_data="match_id"))
    keyboard.add(InlineKeyboardButton(text=_("Live"), callback_data="match_id"))
    keyboard.add(InlineKeyboardButton(text=_("Match2"), callback_data="match_id"))
    keyboard.add(InlineKeyboardButton(text=_("Remind"), callback_data="remind_id"))
    keyboard.add(InlineKeyboardButton(text=_("Tournament1"), callback_data="tournament_id"))
    keyboard.add(InlineKeyboardButton(text=_("Tournament2"), callback_data="tournament_id"))
    keyboard.add(InlineKeyboardButton(text=_("All Tournaments"), callback_data="tournament_id"))
    keyboard.add(InlineKeyboardButton(text=_("All matches"), callback_data="show_events_week"))
    keyboard.add(InlineKeyboardButton(text=_("settings"), callback_data="settings_kb"))
    keyboard.adjust(2, 2, 1, 1, 1, 1, 1)
    return keyboard.as_markup(resize_keyboard=True)


def match_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_("Watch"), callback_data="main_kb"))
    keyboard.add(InlineKeyboardButton(text=_("Remind"), callback_data="remind_id"))
    keyboard.add(InlineKeyboardButton(text=_("Back"), callback_data="settings_kb"))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def back_main() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("back_main"), callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def back_main_premium() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("buy_premium"), callback_data="buy_premium")],
        [InlineKeyboardButton(text=_("back_main"), callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def setting_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("set_lang"), callback_data="lang_kb")],
        [InlineKeyboardButton(text=_("set_timezone"), callback_data="timezone_kb")],
        [InlineKeyboardButton(text=_("profile"), callback_data="profile")],
        [InlineKeyboardButton(text=_("changelog"), callback_data="show_changelog")],
        [InlineKeyboardButton(text=_("guide"), callback_data="guide_page_1")],
        [InlineKeyboardButton(text=_("buy_premium_donate"), callback_data="buy_premium")],
        [InlineKeyboardButton(text=_("back"), callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(2, 2, 2, 1)
    return keyboard.as_markup(resize_keyboard=True)


def lang_kb(user_active: bool = False) -> InlineKeyboardMarkup:
    tmp = "set_lang_"

    if user_active:
        tmp = "change_lang_"
    buttons = [
        [InlineKeyboardButton(text="🇬🇧 English", callback_data=f"{tmp}en")],
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data=f"{tmp}uk")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data=f"{tmp}ru")],
        [InlineKeyboardButton(text=_("more_lang"), callback_data=f"add_lang")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    if user_active:
        keyboard.add(InlineKeyboardButton(text=_("back"), callback_data="settings_kb"))
    else:
        keyboard.add(InlineKeyboardButton(text=_("back"), callback_data="start_kb"))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def loading() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("loading"), callback_data="ignore")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)
