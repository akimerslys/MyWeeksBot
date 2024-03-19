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
    buttons = [
        [InlineKeyboardButton(text=_("notifications"), callback_data="notifications")],
        [InlineKeyboardButton(text=_("schedule"), callback_data="schedule")],
        [InlineKeyboardButton(text=_("settings"), callback_data="settings_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def config_schedule_hrs() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for i in range(4, 13):
        i_str = ('0' + str(i) if i < 10 else str(i))
        keyboard.button(text=i_str + ":00", callback_data=f"schedule_config_hrs_{i_str}")
    keyboard.button(text=_("back"), callback_data="main_kb")
    keyboard.adjust(2, 2, 2, 2, 1, 1)
    return keyboard.as_markup(resize_keyboard=True)


def config_schedule_min(hrs: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for i in range(0, 4):
        i_str = '0' + str(i * 15) if i == 0 else str(i * 15)
        keyboard.button(text=f"{hrs}:{i_str}", callback_data=f"schedule_config_min_{i_str}")
    keyboard.button(text=_("back"), callback_data="main_kb")
    keyboard.adjust(2, 2, 2, 2, 2)
    return keyboard.as_markup(resize_keyboard=True)


def config_schedule_confirm() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("back"), callback_data="config_schedule_confirm_no")
    keyboard.button(text=_("confirm"), callback_data="config_schedule_confirm_yes")
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)


def schedule_kb(is_sch: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if not is_sch:
        keyboard.button(text=_("show_schedule"), callback_data="show_schedule_menu")
    keyboard.button(text=_("update_schedule"), callback_data="schedule_add_day_0")
    keyboard.button(text=_("manage_schedule"), callback_data="manage_schedule")
    keyboard.button(text=_("back"), callback_data="main_kb")

    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_schedule_days_kb(chosen_days: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for day in days_of_week:
        if day == "Sunday":
            builder.button(text=_("workdays"), callback_data="schedule_add_day_workdays")
        if day in chosen_days:
            builder.button(
                text="✅ " + _(day),
                callback_data=f"schedule_add_day_{day}"
            )
        else:
            builder.button(
                text=_(day),
                callback_data=f"schedule_add_day_{day}")
    builder.button(text=_("weekends"), callback_data="schedule_add_day_weekends")
    builder.button(text=_("back"), callback_data="schedule")
    builder.button(text=_("next"), callback_data="schedule_add_go_to_hrs")
    builder.adjust(2, 2, 2, 3, 2)
    return builder.as_markup(resize_keyboard=True)


def hours_schedule_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index in range(0, 24):
        builder.button(
            text=f"{index}:00",
            callback_data=f"schedule_add_hours_{index}"
        )
    builder.button(text=_("back"), callback_data="schedule")
    builder.adjust(4, 1, 4, 1, 4, 1, 4, 1, 4, 1, 1)  # TODO normal sort
    return builder.as_markup(resize_keyboard=True)


def minute_schedule_kb():
    builder = InlineKeyboardBuilder()
    for index in range(0, 12):
        builder.button(
            text=f"{index * 5 if index > 1 else '0' + str(index * 5)}",
            callback_data=f"schedule_add_minute_{index * 5 if index > 1 else '0' + str(index * 5)}"
        )
    builder.button(text=_("back"), callback_data="schedule_add_day_back")
    builder.adjust(1, 2, 1, 2, 1, 2, 1, 2)
    return builder.as_markup(resize_keyboard=True)


def schedule_complete_kb(notify: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if not notify:
        keyboard.button(text=_("notify_off"), callback_data="schedule_add_complete_notify_yes")
    else:
        keyboard.button(text=_("notify_on"), callback_data="schedule_add_complete_notify_no")
    keyboard.button(text=_("cancel"), callback_data="schedule_add_complete_no")
    keyboard.button(text=_("complete"), callback_data="schedule_add_complete")
    keyboard.adjust(1, 2)
    return keyboard.as_markup(resize_keyboard=True)


def back_main_schedule() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("show_schedule"), callback_data="show_schedule_menu")],
        [InlineKeyboardButton(text=_("add_another_schedule"), callback_data="schedule_add_day_0")],
        [InlineKeyboardButton(text=_("back_main"), callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def manage_schedule_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for day in days_of_week:
        keyboard.button(text=_(day), callback_data=f"manage_schedule_day_{day}")
    keyboard.button(text=_("back"), callback_data="schedule")
    keyboard.adjust(2, 3, 2, 1)
    return keyboard.as_markup(resize_keyboard=True)


def manage_schedule_day_kb(user_list: list[tuple]):
    keyboard = InlineKeyboardBuilder()
    logger.debug(user_list)
    for time, text, id_ in user_list:
        keyboard.button(text=f"{time} | {text[:7] if text else ''}",
                        callback_data=f"manage_schedule_id_{id_}")
    keyboard.button(text=_("back"), callback_data="manage_schedule")
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def manage_schedule_info_kb(id):
    buttons = [
        [InlineKeyboardButton(text="🔧" + _("change_day"), callback_data=f"schedule_manage_change_day_{id}")],
        [InlineKeyboardButton(text="🔧" + _("change_time"), callback_data=f"schedule_manage_change_time_{id}")],
        [InlineKeyboardButton(text="🔧" + _("change_day"), callback_data=f"schedule_manage_change_day_{id}")],
        [InlineKeyboardButton(text=_("schedule_delete"), callback_data=f"schedule_delete_{id}")],
        [InlineKeyboardButton(text=_("back"), callback_data="manage_schedule_day")]
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)

def notifications_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("add_notif"), callback_data="add_notif")],
        [InlineKeyboardButton(text=_("notifs"), callback_data="manage_notifs")],
        [InlineKeyboardButton(text=_("back"), callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_notif_first_kb(timezone_str: str = "UTC") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    time_now = datetime.now(tz(timezone_str))
    current_day_index = time_now.weekday()

    days_of_week_translated = [_("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"), _("Friday"), _("Saturday"),
                               _("Sunday")]
    sorted_days = days_of_week_translated[current_day_index:] + days_of_week_translated[:current_day_index]

    for i, day in enumerate(sorted_days):
        builder.button(
            text=day + " ({today_or_date})".format(
                today_or_date=_("Today") if i == 0 else (time_now + timedelta(days=i)).strftime('%d.%m')),
            callback_data=f"set_notif_day_{(time_now + timedelta(days=i)).strftime('%Y %m %d')}"
        )
    builder.button(text=_("calendar"), callback_data="open_calendar")
    builder.button(text=_("back"), callback_data="main_kb")

    builder.adjust(1, 2, 2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def hours_kb(hour: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if hour < 23:
        for index in range(hour, 24):
            builder.button(
                text=f"{index}:00",
                callback_data=f"set_notif_hour_{index}"
            )
    builder.button(text=_("back"), callback_data="add_notif")
    builder.adjust(4, 1, 4, 1, 4, 1, 4, 1, 4, 1, 1)  # TODO normal sort
    return builder.as_markup(resize_keyboard=True)


def minute_kb(hour) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index in range(0, 12):
        builder.button(
            text=f"{hour}:{'0' if index <= 1 else ''}{index * 5}",
            callback_data=f"set_notif_minute_{'0' if index <= 1 else ''}{index * 5}"
        )
    # builder.button(text=_("back"), callback_data="set_notif_day_back")
    builder.adjust(1, 2, 1, 2, 1, 2, 1, 2)
    return builder.as_markup(resize_keyboard=True)


def add_notif_repeat_kb(status: int) -> InlineKeyboardMarkup:
    status_list = [_("repeat_none"), _("repeat_day"), _("repeat_week"), _("repeat_month")]
    buttons = [
        [InlineKeyboardButton(text=status_list[status],
                              callback_data=f"repeatable_{status + 1 if status != 3 else 0}")],
        [InlineKeyboardButton(text=_("complete"), callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


"""def add_notif_repeat_none_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("repeat_none"), callback_data="repeatable_day")],
        [InlineKeyboardButton(text=_("complete"), callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


# TODO ADD PREMIUM BUTTON IF USER NOT PREMIUM
def add_notif_repeat_day_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("repeat_day"), callback_data="repeatable_week")],
        [InlineKeyboardButton(text=_("complete"), callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_notif_repeat_week_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("repeat_week"), callback_data="repeatable_month")],
        [InlineKeyboardButton(text=_("complete"), callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_notif_repeat_month_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("repeat_month"), callback_data="repeatable_none")],
        [InlineKeyboardButton(text=_("complete"), callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)"""


def back_main_notif(id: int | None) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("add_notif"), callback_data="add_notif")],
        [InlineKeyboardButton(text=_("share_notif"), callback_data=f"share_notif_{id}")],
        [InlineKeyboardButton(text=_("back_main"), callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def share_kb(link: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("share"), url=link)],
        [InlineKeyboardButton(text=_("add_notif"), callback_data="add_notif")],
        [InlineKeyboardButton(text=_("back_main"), callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def manage_notifs_kb(user_notifs):
    keyboard = InlineKeyboardBuilder()
    for user_notif in user_notifs:
        if user_notif.active:
            dtime = user_notif.date.strftime("%d.%m %H:%M")
            keyboard.button(text=f"🔔 {dtime} | {user_notif.text[:7] if user_notif.text else ''}",
                            callback_data=f"notif_set_{user_notif.id}")
    keyboard.button(text=_("back"), callback_data="main_kb")
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def notif_info_kb(user_notif):
    buttons = [
        [InlineKeyboardButton(text=_("share_notif"), callback_data=f"share_notif_{user_notif.id}")],
        #[InlineKeyboardButton(text=_("active") if user_notif.active else _("inactive"),
        #                     callback_data=f"notif_active_{user_notif.id}")],
        [InlineKeyboardButton(text=_("notif_text"), callback_data=f"notif_text_{user_notif.id}")],
        [InlineKeyboardButton(text=_("notif_delete"), callback_data=f"notif_delete_{user_notif.id}")],
        [InlineKeyboardButton(text=_("back"), callback_data="notifications")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
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
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def language_kb(user_logged: bool = True) -> InlineKeyboardMarkup:

    buttons = [
        [InlineKeyboardButton(text="🇬🇧 English", callback_data=f"set_lang_en")],
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data=f"set_lang_uk")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data=f"set_lang_ru")],
        [InlineKeyboardButton(text=_("more_lang"), callback_data=f"add_lang")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    if user_logged:
        keyboard.add(InlineKeyboardButton(text=_("back"), callback_data="settings_kb"))
    else:
        keyboard.add(InlineKeyboardButton(text=_("back"), callback_data="start_kb"))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def profile_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("buy_premium"), callback_data="buy_premium")],
        [InlineKeyboardButton(text=_("delete_all_info"), callback_data="profile_delete")],
        [InlineKeyboardButton(text=_("back"), callback_data="settings_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def delete_profile_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    import random
    num_btn = random.randint(0, 20)
    for i in range(0, 16):
        if i == num_btn:
            keyboard.button(text="🔥" + _("delete") + "🔥", callback_data="profile_delete_yes")
        else:
            keyboard.button(text=_("🟢"), callback_data="profile_delete_no")
    keyboard.adjust(4, 4, 4, 4)
    return keyboard.as_markup(resize_keyboard=True)


def loading() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("loading"), callback_data="ignore")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)
