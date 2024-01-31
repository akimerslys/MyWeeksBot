from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.callback_data import CallbackData
from keyboards.inline.menu import main_keyboard, setting_keyboard, language_keyboard, add_keyboard_first
from keyboards.inline.timezone import timezone_simple_keyboard, timezone_advanced_keyboard
from loguru import logger
from aiogram_calendar import SimpleCalendar, DialogCalendar, SimpleCalendarCallback, DialogCalendarCallback, \
    get_user_locale

from datetime import datetime


router = Router(name="menu")

#TODO FIX TODAY BUTTON, FIX RANGES (CALENDAR)

# MAIN
@router.callback_query(F.data == "main_kb")
async def menu_back(call: CallbackQuery):
    await call.message.edit_text("⤵️ Please choose an option from the menu below", reply_markup=main_keyboard())


# SETTINGS
@router.callback_query(F.data == 'settings_kb')
async def settings(call: CallbackQuery):
    await call.message.edit_text("🔧 Choose Settings", reply_markup=setting_keyboard())


@router.callback_query(F.data == "lang_kb")
async def choose_language(call: CallbackQuery):
    await call.message.edit_text("🌐 Choose your language", reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(call: CallbackQuery):
    print(call)
    await call.message.edit_text(
        f"🌐 Language changed to {call.data}\n\nif you see this message, everything ok, thank you :)",
        reply_markup=language_keyboard())


@router.callback_query(F.data == "timezone_kb")
async def choose_timezone(call: CallbackQuery):
    await call.message.edit_text("🕔 Choose your timezone", reply_markup=timezone_simple_keyboard())


@router.callback_query(F.data.startswith("set_timezone_"))
async def set_timezone(call: CallbackQuery):
    await call.message.edit_text(f"🕔 Timezone changed to {call.data[13:]}", reply_markup=setting_keyboard())


@router.callback_query(F.data == "show_all")
async def show_all_timezone(call: CallbackQuery):
    await call.message.edit_text("🕔 Choose your timezone", reply_markup=timezone_advanced_keyboard())


# MyWeeks
@router.callback_query(F.data == "add")
async def add_notification(call: CallbackQuery):
    await call.message.edit_text("🕔 Choose day", reply_markup=add_keyboard_first())


@router.callback_query(F.data.startswith("day_"))
async def choose_time(call: CallbackQuery):
    await call.message.edit_text(f"🕔 Choose time for {call.data[4:]}")


# CALENDAR
@router.callback_query(F.data == "open_calendar")
async def nav_cal_handler(call: CallbackQuery):
    await call.message.edit_text(
        "Please select a date: ",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(call.from_user)).start_calendar()
    )


# can be launched at specific year and month with allowed dates range
@router.message(F.text.lower() == 'navigation calendar w month')
async def nav_cal_handler_date(call: CallbackQuery):
    calendar = SimpleCalendar(
        locale=await get_user_locale(call.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime.today(), datetime(2025, 12, 31))
    await call.message.edit_text(
        "Calendar opened on feb 2023. Please select a date: ",
        reply_markup=await calendar.start_calendar(year=datetime.now().year, month=datetime.now().year)
    )


# simple calendar usage - filtering callbacks of calendar format
@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(call: CallbackQuery, callback_data: CallbackData):
    calendar = SimpleCalendar(
        locale=await get_user_locale(call.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime.now(), datetime(2025, 1, 1))
    selected, date = await calendar.process_selection(call, callback_data)
    if selected:
        await call.message.edit_text(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=main_keyboard()
        )


@router.message(F.text.lower() == 'dialog calendar')
async def dialog_cal_handler(call: CallbackQuery):
    await call.message.edit_text(
        "Please select a date: ",
        reply_markup=await DialogCalendar(
            locale=await get_user_locale(call.message.from_user)
        ).start_calendar()
    )


# starting calendar with year 1989
@router.message(F.text.lower() == 'dialog calendar w year')
async def dialog_cal_handler_year(message: Message):
    await message.answer(
        "Calendar opened years selection around 2024. Please select a date: ",
        reply_markup=await DialogCalendar(
            locale=await get_user_locale(message.from_user)
        ).start_calendar(2024)
    )


# starting dialog calendar with year 1989 & month
@router.message(F.text.lower() == 'dialog calendar w month')
async def dialog_cal_handler_month(message: Message):
    await message.answer(
        "Calendar opened on sep 1989. Please select a date: ",
        reply_markup=await DialogCalendar(
            locale=await get_user_locale(message.from_user)
        ).start_calendar(year=2024, month=1)
    )


# dialog calendar usage
@router.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=main_keyboard()
        )


@router.callback_query(F.data == "remove")
async def remove_notification(call: CallbackQuery):
    await call.answer("⚙️ This function is not available yet")


@router.callback_query()
async def found_callback(call: CallbackQuery):
    logger.error(f"Found unexpected callback: {call.data}, from {call.from_user.username} ({call.from_user.id})")
    await call.answer("⚙️ unexpected callback, please use /report", show_alert=True)
