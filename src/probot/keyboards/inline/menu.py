import logging
from datetime import datetime, timedelta

from loguru import logger
from pytz import timezone as tz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# TODO REWRITE, OPTIMIZE


def main_kb(event1: str = "", match1: str = "") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    e_ = 1
    if event1:
        e_ = 2
        keyboard.add(InlineKeyboardButton(text=event1, callback_data="event_id"))
    keyboard.add(InlineKeyboardButton(text=_("Events"), callback_data="events_menu"))

    m_ = 1
    if match1:
        m_ = 2
        keyboard.add(InlineKeyboardButton(text=match1, callback_data="match_id"))
    keyboard.add(InlineKeyboardButton(text=_("Matches"), callback_data="matches_menu"))

    keyboard.add(InlineKeyboardButton(text=_("Live Matches (SOON)"), callback_data="live_matches"))
    keyboard.add(InlineKeyboardButton(text=_("Results"), callback_data="results_menu"))
    keyboard.add(InlineKeyboardButton(text=_("Best Players"), callback_data="best_players"))
    keyboard.add(InlineKeyboardButton(text=_("Top Teams"), callback_data="best_teams"))
    keyboard.add(InlineKeyboardButton(text=_("News"), callback_data="last_news"))
    keyboard.add(InlineKeyboardButton(text=_("settings"), callback_data="settings_kb"))
    keyboard.adjust(e_, m_, 1, 3, 1)
    return keyboard.as_markup(resize_keyboard=True)


def match_kb(status: str | int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if status == "LIVE":
        keyboard.add(InlineKeyboardButton(text=_("Watch"), callback_data="main_kb"))
        keyboard.add(InlineKeyboardButton(text=_("Watch"), callback_data="main_kb"))
    elif status == "Upcoming":
        keyboard.add(InlineKeyboardButton(text=_("Remind"), callback_data="remind_id"))
    elif status == "Finished":
        keyboard.add(InlineKeyboardButton(text=_("Stats"), callback_data="stats_id"))
    keyboard.add(InlineKeyboardButton(text=_("Back"), callback_data="main_kb"))
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


def events_kb(events: list, more: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for i, event in enumerate(events, start=1):
        if i > 4 and not more:
            keyboard.add(InlineKeyboardButton(text=_("more"), callback_data="events_menu_more"))
            break
        keyboard.add(InlineKeyboardButton(text=event["name"], callback_data=f"event_{event['id']}"))
    keyboard.add(InlineKeyboardButton(text=_("back"), callback_data="main_kb"))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def event_kb(id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_("Follow (soon)"), callback_data=f"event_follow_{id}"))
    keyboard.add(InlineKeyboardButton(text=_("Matches"), callback_data=f"event_matches_{id}"))
    keyboard.add(InlineKeyboardButton(text=_("Teams"), callback_data=f"event_teams_{id}"))
    keyboard.add(InlineKeyboardButton(text=_("Update"), callback_data=f"event_update_{id}"))
    keyboard.add(InlineKeyboardButton(text=_("Back"), callback_data="events_menu"))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def event_matches_kb(matches: list, more: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for i, match in enumerate(matches, start=1):
        if i > 4 and not more:
            keyboard.add(InlineKeyboardButton(text=_("more"), callback_data="event_matches_more"))
            break
        keyboard.add(InlineKeyboardButton(text=match["name"], callback_data=f"match_{match['id']}"))
    keyboard.add(InlineKeyboardButton(text=_("back"), callback_data="events_menu"))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)
