from datetime import datetime, timedelta
from pytz import timezone as tz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📈 Schedule", callback_data="schedule")],
        [InlineKeyboardButton(text="📊 Notifications", callback_data="notifications")],
        [InlineKeyboardButton(text="🙍‍♂️ Profile", callback_data="profile")],
        [InlineKeyboardButton(text="⚙️ Extra features", callback_data="settings_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def schedule_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📈 Configure schedule", callback_data="schedule")],
            # OR
        [InlineKeyboardButton(text="📈 Your schedule", callback_data="schedule123")],
        [InlineKeyboardButton(text="📊 Manage schedule", callback_data="schedule123")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def notifications_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📈 Add Notification", callback_data="add_notif")],
        [InlineKeyboardButton(text="📊 Notifications", callback_data="manage_notifs")],
        [InlineKeyboardButton(text="⬅️ back", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_notif_first_kb(timezone_str: str = "UTC") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    time_now = datetime.now(tz(timezone_str))
    current_day_index = time_now.weekday()

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    sorted_days = days_of_week[current_day_index:] + days_of_week[:current_day_index]

    for i, day in enumerate(sorted_days):
        builder.button(
            text=f"{day}{' (Today)' if i == 0 else ' (' + (time_now + timedelta(days=i)).strftime('%d.%m') + ')'} ",
            callback_data=f"day_{(time_now + timedelta(days=i)).strftime('%Y %m %d')}"
        )
    builder.button(text="Calendar", callback_data="open_calendar")
    builder.button(text="⬅️ Back", callback_data="main_kb")

    builder.adjust(1, 2, 2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def hours_kb(hour: int = 0) -> InlineKeyboardMarkup:
    if hour != 0:
        hour += 0    # TODO CHANGE TO +1
    builder = InlineKeyboardBuilder()
    if hour < 23:
        for index in range(hour, 24):
            builder.button(
                text=f"{index}:00",
                callback_data=f"set_hours_{index}"
            )
    builder.button(text="⬅️ Back", callback_data="add_notif")
    builder.adjust(4, 1, 4, 1, 4, 1, 4, 1, 4, 1, 1)         # TODO normal sort
    return builder.as_markup(resize_keyboard=True)


def minute_kb(hour) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index in range(0, 12):
        builder.button(
            text=f"{hour}:{'0' if index<=1 else ''}{index*5}",
            callback_data=f"set_minute_{'0' if index<=1 else ''}{index*5}"
        )
    builder.adjust(1, 2, 1, 2, 1, 2, 1, 2)
    return builder.as_markup(resize_keyboard=True)


def add_notif_repeat_none_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🕔 Do not repeat", callback_data="repeatable_day")],
        [InlineKeyboardButton(text="✅ Complete", callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


# TODO ADD PREMIUM BUTTON IF USER NOT PREMIUM
def add_notif_repeat_day_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=" 🔒 Every Day ", callback_data="repeatable_week")],
        [InlineKeyboardButton(text="✅ Complete", callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_notif_repeat_week_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="  🕔 Every Week", callback_data="repeatable_month")],
        [InlineKeyboardButton(text="✅ Complete", callback_data="add_complete")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def add_notif_repeat_month_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=" 🕔 Every Month", callback_data="repeatable_none")],
        [InlineKeyboardButton(text="✅ Complete", callback_data="add_complete")],
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
    keyboard.button(text="📚 back", callback_data="main_kb")
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def notif_info_kb(user_notif):
    buttons = [
        [InlineKeyboardButton(text=f"{'🟩 Active' if user_notif.active else '🟥 Inactive'}",
                              callback_data=f"notif_active_{user_notif.id}")],
        [InlineKeyboardButton(text="🔔 Change text", callback_data=f"notif_text_{user_notif.id}")],
        [InlineKeyboardButton(text="🔔 Change repeat", callback_data=f"notif_repeat_{user_notif.id}")],
        [InlineKeyboardButton(text="❌ Delete", callback_data=f"notif_delete_{user_notif.id}")],
        [InlineKeyboardButton(text="⬅️ back", callback_data="notifications")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def back_main() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def back_main_premium() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🔑 Buy Premium", callback_data="buy_premium")],
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def setting_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🌐 Set Language", callback_data="lang_kb")],
        [InlineKeyboardButton(text="🕔 Set Timezone", callback_data="timezone_kb")],
        [InlineKeyboardButton(text="🔑 Show Changelog", callback_data="show_changelog")],
        [InlineKeyboardButton(text="🔑 Donate", callback_data="buy_premium")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_kb")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def language_kb() -> InlineKeyboardMarkup:
    buttons = [
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
            [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="set_lang_uk")],
            [InlineKeyboardButton(text="🏳️ Руzzкий", callback_data="set_lang_ru")],
            [InlineKeyboardButton(text="ADD YOUR LANGUAGE!", callback_data="add_lang")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="settings_kb")],
        ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)



