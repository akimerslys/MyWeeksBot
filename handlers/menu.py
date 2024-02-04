from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from keyboards.inline.menu import main_kb, setting_kb, language_kb, add_keyboard_first, \
    add_notif_repeat_week_kb, add_notif_repeat_none_kb, back_main, hours_kb, minute_kb, add_notif_repeat_month_kb
from keyboards.inline.timezone import timezone_simple_keyboard, timezone_advanced_keyboard
from keyboards.inline.calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from loguru import logger
from utils.states import AddNotif
from datetime import datetime


router = Router(name="menu")

# TODO FIX TODAY BUTTON, FIX RANGES (CALENDAR)
# TODO ADD TIMEZONE TO THE NOTIFICATION
# TODO ADD TIMEZONE SETTING FOR FIRST USER


# MAIN

@router.callback_query(F.data == "main_kb")
async def menu_back(call: CallbackQuery):
    await call.message.edit_text("⤵️ Please choose an option from the menu below", reply_markup=main_kb())


# SETTINGS
@router.callback_query(F.data == 'settings_kb')
async def settings(call: CallbackQuery):
    await call.message.edit_text("🔧 Choose Settings", reply_markup=setting_kb())


@router.callback_query(F.data == "lang_kb")
async def choose_language(call: CallbackQuery):
    await call.message.edit_text("🌐 Choose your language", reply_markup=language_kb())


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(call: CallbackQuery):
    print(call)
    await call.message.edit_text(
        f"🌐 Language changed to {call.data}\n\nif you see this message, everything ok, thank you :)",
        reply_markup=language_kb())


@router.callback_query(F.data == "timezone_kb")
async def choose_timezone(call: CallbackQuery):
    await call.message.edit_text("🕔 Choose your timezone", reply_markup=timezone_simple_keyboard())


@router.callback_query(F.data.startswith("set_timezone_"))
async def set_timezone(call: CallbackQuery):
    await call.message.edit_text(f"🕔 Timezone changed to {call.data[13:]}", reply_markup=setting_kb())


@router.callback_query(F.data == "show_all")
async def show_all_timezone(call: CallbackQuery):
    await call.message.edit_text("🕔 Choose your timezone", reply_markup=timezone_advanced_keyboard())


# MY WEEKS
# CHOOSE DAY

@router.callback_query(F.data == "add")
async def add_notification(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddNotif.day)
    await call.message.edit_text("🕔 Choose day", reply_markup=add_keyboard_first())


# CHOOSE DAY WITH CALENDAR

@router.callback_query(F.data == "open_calendar")
async def nav_cal_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddNotif.date)
    await call.message.edit_text(
        "Please select a date: ",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(call.from_user)).start_calendar()
    )


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(call: CallbackQuery, state: FSMContext, callback_data: CallbackData):
    calendar = SimpleCalendar(
        locale=await get_user_locale(call.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime.now(), datetime(2025, 1, 1))
    selected, date = await calendar.process_selection(call, callback_data)
    if selected:
        await call.message.edit_text(
            f'🕔 {date.strftime("%d/%m/%Y")}, please select a time:',
            reply_markup=hours_kb()
        )
        await state.update_data(day=date.strftime("%d/%m/%Y"))
        await state.set_state(AddNotif.hours)


# CHOOSE TIME
@router.callback_query(F.data.startswith("day_"))
async def add_notif_ask_hour(call: CallbackQuery, state: FSMContext):
    await state.update_data(day=call.data[4:])
    await state.set_state(AddNotif.hours)
    await call.message.edit_text(f"🕔 Choose time for {call.data[4:]}", reply_markup=hours_kb())


@router.callback_query(F.data.startswith("set_hours_"))
async def add_notif_ask_minute(call: CallbackQuery, state: FSMContext):
    await state.update_data(hours=call.data[10:])
    await state.set_state(AddNotif.minutes)
    await call.message.edit_text(
        "Please select a minute: ",
        reply_markup=minute_kb()
    )


@router.callback_query(F.data.startswith("set_minute_"))
async def add_notif_ask_text(call: CallbackQuery, state: FSMContext):
    await state.update_data(minutes=call.data[11:])
    tmp_msg = await call.message.edit_text(
        "Now write name of your notification:",
    )
    await state.set_state(AddNotif.text)
    await state.update_data(tmp_msg=tmp_msg.message_id)


@router.message(AddNotif.text)
async def add_notif_text(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data.get('tmp_msg'))
    if data.get('date'):
        await bot.send_message(
            message.from_user.id,
            f"📅 Date: {data.get('date')}\n"
            f"⏰ Time: {data['hours']}:{data['minutes']}\n"
            f"📝 Text: {data['text']}",
            reply_markup=add_notif_repeat_none_kb()
        )
    else:
        await bot.send_message(
            message.from_user.id,
            f"📅 Date: {data.get('day')}\n"
            f"⏰ Time: {data.get('hours')}:{data.get('minutes')}\n"
            f"📝 Text: {data.get('text')}",
            reply_markup=add_notif_repeat_none_kb()
        )
    await message.delete()
    await state.set_state(AddNotif.repeat)


@router.callback_query(F.data == "repeatable_week")
async def add_notif_text_off(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=add_notif_repeat_week_kb())


@router.callback_query(F.data == "repeatable_month")
async def add_notification_text_off(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=add_notif_repeat_month_kb())


@router.callback_query(F.data == "repeatable_none")
async def add_notification_text_off(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=add_notif_repeat_none_kb())

@router.callback_query(F.data == "add_complete")
async def add_notification_finish(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer("✅ Notification added", show_alert=True)
    await call.message.edit_reply_markup(reply_markup=back_main())


# REMOVE NOTIFICATION

@router.callback_query(F.data == "remove")
async def remove_notification(call: CallbackQuery):
    await call.answer("⚙️ This function is not available yet")


@router.callback_query()
async def found_callback(call: CallbackQuery):
    logger.error(f"Found unexpected callback: {call.data}, from {call.from_user.username} ({call.from_user.id})")
    await call.answer("⚙️ Error, please use /report", show_alert=True)
    await call.message.edit_text("⤵️ Please choose an option from the menu below", reply_markup=main_kb())


@router.message()
async def found_message(message: Message):
    logger.error(f"Found unexpected message: {message.text}, from {message.from_user.username} ({message.from_user.id})")
    await message.answer("⤵️ Please choose an option from the menu below", reply_markup=main_kb())
