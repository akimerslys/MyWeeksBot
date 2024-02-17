from datetime import datetime, timedelta
from pytz import timezone as tz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def main_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("schedule"), callback_data="schedule")],
        [InlineKeyboardButton(text=_("notifications"), callback_data="notifications")],
        [InlineKeyboardButton(text=_("profile"), callback_data="profile")],
        [InlineKeyboardButton(text=_("settings"), callback_data="settings_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def schedule_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("schedule"), callback_data="schedule_add_day_0")],
        # OR
        [InlineKeyboardButton(text=_("📈 Your schedule"), callback_data="schedule123")],
        [InlineKeyboardButton(text=_("📊 Manage schedule"), callback_data="schedule123")],
        [InlineKeyboardButton(text=_("back"), callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_schedule_days_kb(chosen_days: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for day in days_of_week:
        if day == "Sunday":
            builder.button(text=_("👨‍💻 WorkDays"), callback_data="schedule_add_day_workdays")
        if day in chosen_days:
            builder.button(
                text="✅ " + _(day),
                callback_data=f"schedule_add_day_{day}"
            )
        else:
            builder.button(
                text=_(day),
                callback_data=f"schedule_add_day_{day}")
    builder.button(text=_("🛌 Weekends"), callback_data="schedule_add_day_weekends")
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
            text=f"{index * 5}",
            callback_data=f"schedule_add_minute_{index * 5}"
        )
    builder.button(text=_("back"), callback_data="schedule_add_day_back")
    builder.adjust(1, 2, 1, 2, 1, 2, 1, 2)
    return builder.as_markup(resize_keyboard=True)


def schedule_complete_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("notify"), callback_data="schedule_add_complete_notify")],
        [InlineKeyboardButton(text=_("cancel"), callback_data="schedule_add_complete_no")],
        [InlineKeyboardButton(text=_("complete"), callback_data="schedule_add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1, 2)
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

    days_of_week = [_("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"), _("Friday"), _("Saturday"), _("Sunday")]
    sorted_days = days_of_week[current_day_index:] + days_of_week[:current_day_index]

    for i, day in enumerate(sorted_days):
        builder.button(
            text=f"{day}{' (Today)' if i == 0 else ' (' + (time_now + timedelta(days=i)).strftime('%d.%m') + ')'} ",
            callback_data=f"set_notif_day_{(time_now + timedelta(days=i)).strftime('%Y %m %d')}"
        )
    builder.button(text=_("calendar"), callback_data="open_calendar")
    builder.button(text=_("back"), callback_data="main_kb")

    builder.adjust(1, 2, 2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def hours_kb(hour: int = 0) -> InlineKeyboardMarkup:
    if hour != 0:
        hour += 1  # TODO CHANGE TO +1
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
    #builder.button(text=_("back"), callback_data="set_notif_day_back")
    builder.adjust(1, 2, 1, 2, 1, 2, 1, 2)
    return builder.as_markup(resize_keyboard=True)


def add_notif_repeat_none_kb() -> InlineKeyboardMarkup:
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
    return keyboard.as_markup(resize_keyboard=True)


def back_main_notif() -> InlineKeyboardMarkup:
    buttons = [
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
            keyboard.button(text=f"🔔 {dtime} | {user_notif.text[:20]}", callback_data=f"notif_set_{user_notif.id}")
    keyboard.button(text=_("back"), callback_data="main_kb")
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def notif_info_kb(user_notif):
    buttons = [
        [InlineKeyboardButton(text=f"{'🟩 Active' if user_notif.active else '🟥 Inactive'}",
                              callback_data=f"notif_active_{user_notif.id}")],
        [InlineKeyboardButton(text=_("notif_text"), callback_data=f"notif_text_{user_notif.id}")],
        [InlineKeyboardButton(text=_("notif_repeat"), callback_data=f"notif_repeat_{user_notif.id}")],
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
        [InlineKeyboardButton(text=_("changelog"), callback_data="show_changelog")],
        [InlineKeyboardButton(text=_("buy_premium_donate"), callback_data="buy_premium")],
        [InlineKeyboardButton(text="back", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def language_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="set_lang_uk")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton(text=_("add_lang"), callback_data="add_lang")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="settings_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)
