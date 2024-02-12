from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline.menu import main_kb, setting_kb, language_kb, add_keyboard_first, \
    add_notif_repeat_week_kb, add_notif_repeat_none_kb, back_main, hours_kb, minute_kb, add_notif_repeat_month_kb, \
    back_main_premium, add_notif_repeat_day_kb
from keyboards.inline.timezone import timezone_simple_keyboard, timezone_advanced_keyboard, timezone_geo_reply, \
    ask_location_confirm
from keyboards.inline.calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale

from utils.states import AddNotif, AskLocation
from services import users as dbuc  # DataBase UserCommands
from services import notifs as dbnc  # DataBase NotificationCommands

from loguru import logger
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz

router = Router(name="menu")


# TODO FIX TODAY BUTTON, FIX RANGES (CALENDAR)
# TODO ADD NOTIFICATIONS TO THE DATABASE                                        #DONE (NEED MORE TESTS)
# TODO INTEGRATE PROFILE TO MENU
# TODO ADD TIMEZONE TO THE NOTIFICATIONS                                        #DONE (NEED MORE TESTS)
# TODO ADD TIMEZONE SETTING FOR FIRST USER                                      #ADDED BUT NOT TESTED
# TODO MOVE TIMEZONE SETTING TO ANOTHER FILE (IF NEEDED)
# TODO SORT WEEKDAYS BY TODAYS DAY (IF WEDNESDAY, WEDNESDAY IS FIRST)           #DONE (NEED MORE TESTS)


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
async def set_language(call: CallbackQuery, session: AsyncSession):
    await call.message.edit_text(
        f"🌐 Language changed to {call.data[9:]}",
        reply_markup=setting_kb()
    )
    if await dbuc.get_language_code(session, call.from_user.id) != call.data[9:]:
        await dbuc.set_language_code(session, call.from_user.id, call.data[9:])


@router.callback_query(F.data == "add_lang")
async def add_language(call: CallbackQuery):
    await call.answer(
        "⚙️ This function is not available yet\nSoon u will have ability to add your own language",
        show_alert=True)


@router.callback_query(F.data == "timezone_kb")
async def choose_timezone(call: CallbackQuery):
    await call.message.edit_text("🕔 Choose your timezone", reply_markup=timezone_simple_keyboard())


@router.callback_query(F.data.startswith("set_timezone_"))
async def set_timezone(call: CallbackQuery, session: AsyncSession):
    try:
        pytz.timezone(call.data[13:])
    except pytz.exceptions.UnknownTimeZoneError:
        await call.answer("⚙️ Invalid Timezone, please use /report", show_alert=True)
        await call.message.edit_text("⤵️ Please choose an option from the menu below", reply_markup=main_kb())
        logger.error(f"User {call.from_user.id} tried to set invalid timezone: {call.data[13:]}")
        return
    await call.message.edit_text(f"🕔 Timezone changed to {call.data[13:]}", reply_markup=setting_kb())
    await dbuc.set_timezone(session, call.from_user.id, call.data[13:])


@router.callback_query(F.data.startswith("send_geo"))
async def ask_for_location(call: CallbackQuery, bot: Bot, state: FSMContext):
    geo_msg = await bot.send_message(
        call.message.chat.id,
        f"Send your location\n<b>WE DONT SAVE YOUR LOCATION</b>",
        reply_markup=timezone_geo_reply()
    )
    await state.set_state(AskLocation.ask_location)
    await state.update_data(ask_location=geo_msg.message_id)


@router.message(AskLocation.ask_location)
async def handle_location(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await bot.delete_messages(
        message.from_user.id,
        [data.get('ask_location'), message.message_id]
    )
    if message.location:
        try:
            timezone_str = TimezoneFinder().timezone_at(lng=message.location.longitude, lat=message.location.latitude)
        except Exception as e:
            logger.error(f"Error processing location: {e}")
            tmp_msg = await bot.send_message(
                message.from_user.id,
                "Unexpected Error. Please, try again.",
                reply_markup=timezone_geo_reply()
            )
            await state.update_data(ask_location=tmp_msg.message_id)
            return

        tmp_msg = await bot.send_message(
            message.from_user.id,
            f"🕔 This timezone correct? {timezone_str}\nYour Time should be {datetime.now(pytz.timezone(timezone_str)).strftime('%H:%M')}",
            reply_markup=ask_location_confirm()
        )
        await state.update_data(ask_for_location=tmp_msg.message_id)
        await state.update_data(ask_location_confirm=timezone_str)
        await state.set_state(AskLocation.ask_location_confirm)


@router.callback_query(F.data == "confirm_location")
async def confirm_location(call: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await dbuc.set_timezone(session, call.from_user.id, data.get('ask_location_confirm'))
    await bot.delete_message(call.from_user.id, data.get('ask_for_location'))
    await call.answer("✅ Timezone changed")
    await state.clear()


@router.callback_query(F.data == "cancel_location")
async def cancel_location(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(call.from_user.id, data.get('ask_for_location'))
    await call.answer("📛 Timezone not set")
    logger.warning(f"User {call.from_user.id} false location, timezone {data.get('ask_location_confirm')}")
    await state.clear()


@router.callback_query(F.data == "show_all")
async def show_all_timezone(call: CallbackQuery):
    await call.message.edit_text("🕔 Choose your timezone", reply_markup=timezone_advanced_keyboard())


# MY WEEKS
# CHOOSE DAY

@router.callback_query(F.data == "add")
async def add_notification(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(AddNotif.date)
    await call.message.edit_text(
        "🕔 Choose day",
        reply_markup=add_keyboard_first(await dbuc.get_timezone(session, call.from_user.id)))


# CHOOSE DAY WITH CALENDAR

@router.callback_query(F.data == "open_calendar")
async def nav_cal_handler(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(AddNotif.date)
    user_time = pytz.timezone(await dbuc.get_timezone(session, call.from_user.id)).localize(
        datetime.utcnow()).astimezone(
        pytz.utc)
    await call.message.edit_text(
        "Please select a date: ",
        reply_markup=await SimpleCalendar().start_calendar(user_time.year, user_time.month, user_time)
    )


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(call: CallbackQuery, state: FSMContext, callback_data: CallbackData,
                                  session: AsyncSession):
    calendar = SimpleCalendar(
        locale=await get_user_locale(call.from_user), show_alerts=True
    )
    user_time = pytz.timezone(await dbuc.get_timezone(session, call.from_user.id)).localize(
        datetime.utcnow()).astimezone(
        pytz.utc)
    calendar.set_dates_range(user_time.replace(tzinfo=None) - timedelta(days=1),
                             user_time.replace(tzinfo=None) + timedelta(days=365))
    selected, date = await calendar.process_selection(call, callback_data)
    if selected:
        await call.message.edit_text(
            f'🕔 {date.strftime("%d %m %Y")}, please select a time:',
            reply_markup=hours_kb()
        )
        await state.update_data(date=date.strftime("%Y %m %d"))
        await state.set_state(AddNotif.hours)


# CHOOSE DAY HOUR TIME
@router.callback_query(F.data.startswith("day_"))
async def add_notif_ask_hour(call: CallbackQuery, state: FSMContext):
    await state.update_data(date=call.data[4:])
    await state.set_state(AddNotif.hours)
    await call.message.edit_text(f"🕔 Choose time for {call.data[4:]}", reply_markup=hours_kb())


@router.callback_query(F.data.startswith("set_hours_"))
async def add_notif_ask_minute(call: CallbackQuery, state: FSMContext):
    await state.update_data(hours=call.data[10:])
    await state.set_state(AddNotif.minutes)
    await call.message.edit_text(
        "Please select a minute: ",
        reply_markup=minute_kb(call.data[10:])
    )


@router.callback_query(F.data.startswith("set_minute_"))
async def add_notif_ask_text(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(minutes=call.data[11:])
    tmp_msg = await call.message.edit_text(
        "Now write name of your notification: (skip button TBA)",  # TODO ADD SKIP BUTTON
    )
    await state.set_state(AddNotif.text)
    await state.update_data(tmp_msg=tmp_msg.message_id)


@router.message(AddNotif.text)
async def add_notif_text(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data.get('tmp_msg'))
    full_date = datetime.strptime(f"{data.get('date')} {data.get('hours')}:{data.get('minutes')}", "%Y %m %d %H:%M")
    await bot.send_message(
        message.from_user.id,
        f"full_date: {full_date}\n"
        f"📅 Date: {data.get('date')}\n"
        f"⏰ Time: {data.get('hours')}:{data.get('minutes')}\n"
        f"📝 Text: {data.get('text')}",
        reply_markup=add_notif_repeat_none_kb()
    )
    await message.delete()
    await state.update_data(repeat_daily=False)
    await state.update_data(repeat_weekly=False)
    await state.set_state(AddNotif.repeat_daily)


@router.callback_query(F.data == "repeatable_day")
async def add_notif_text_off(call: CallbackQuery, state: FSMContext):
    await state.update_data(repeat_daily=True)
    await call.message.edit_reply_markup(reply_markup=add_notif_repeat_day_kb())


@router.callback_query(F.data == "repeatable_week")
async def add_notif_text_off(call: CallbackQuery, state: FSMContext):
    await state.update_data(repeat_daily=False)
    await state.update_data(repeat_weekly=True)
    await call.message.edit_reply_markup(reply_markup=add_notif_repeat_week_kb())


@router.callback_query(F.data == "repeatable_month")
async def add_notification_text_off(call: CallbackQuery, state: FSMContext):
    await state.update_data(repeat_weekly=True)
    await state.update_data(repeat_daily=True)
    await call.message.edit_reply_markup(reply_markup=add_notif_repeat_month_kb())


@router.callback_query(F.data == "repeatable_none")
async def add_notification_text_off(call: CallbackQuery, state: FSMContext):
    await state.update_data(repeat_daily=False)
    await state.update_data(repeat_weekly=False)
    await call.message.edit_reply_markup(reply_markup=add_notif_repeat_none_kb())


@router.callback_query(F.data == "add_complete")
async def add_notification_finish(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    if not await state.get_state():
        await call.answer("⚙️ Error, please use /report", show_alert=True)
        await call.message.edit_text("⤵️ Please choose an option from the menu below", reply_markup=main_kb())
        return
    data = await state.get_data()
    repeat_daily = data.get('repeat_daily')
    repeat_weekly = data.get('repeat_weekly')
    if not await dbuc.is_premium(session, call.from_user.id) and repeat_daily and not repeat_weekly:
        await call.answer("Sorry, you need to buy premium to use this feature", show_alert=True)
        return

    user_notifs_len = await dbuc.count_user_notifs(session, call.from_user.id)

    if user_notifs_len > 5:
        if not await dbuc.is_premium(session, call.from_user.id) or user_notifs_len >= 10:
            await call.answer("You have reached the limit of 10 notifications", show_alert=True)
            await call.message.edit_reply_markup(reply_markup=back_main_premium())
            await state.clear()
            return

    full_date = datetime.strptime(f"{data.get('date')} {data.get('hours')} {data.get('minutes')}", "%Y %m %d %H %M")
    user_timezone = pytz.timezone(await dbuc.get_timezone(session, call.from_user.id))

    await dbnc.add_notif(session, user_timezone.localize(full_date).astimezone(pytz.utc).replace(tzinfo=None),
                    call.from_user.id,
                    data.get('text'),
                    repeat_daily,
                    repeat_weekly)
    await dbuc.inc_user_notifs(session, call.from_user.id)
    await call.answer(f"✅ Notification added", show_alert=True)
    await call.message.edit_reply_markup(reply_markup=back_main())
    await state.clear()


@router.callback_query(F.data == "manage")
async def buy_premium(call: CallbackQuery):
    await call.answer(
        "⚙️ This function is not available yet",
        show_alert=True
    )
# MANAGE NOTIFICATIONS
@router.callback_query(F.data == "manage")
async def manage_notification(call: CallbackQuery, session: AsyncSession):
    user_notifs = await (session, call.from_user.id)
    if not user_notifs:
        await call.answer("You don't have any notifications", show_alert=True)
        return
    await call.message.edit_text(
        "📝 Your notifications",
        reply_markup=ReplyKeyboardRemove()
    )
    for notif in user_notifs:
        await call.message.answer(
            f"📅 Date: {notif.date.strftime('%d %m %Y')}\n"
            f"⏰ Time: {notif.date.strftime('%H:%M')}\n"
            f"📝 Text: {notif.text}\n"
            f"🔁 Repeat: {'Daily' if notif.repeat_daily else 'Weekly' if notif.repeat_weekly else 'None'}"
        )


# PREMIUM
@router.callback_query(F.data == "buy_premium")
async def buy_premium(call: CallbackQuery):
    await call.answer(
        "⚙️ This function is not available yet",
        show_alert=True
    )


@router.callback_query()
async def found_callback(call: CallbackQuery):
    logger.error(f"Found unexpected callback: {call.data}, from {call.from_user.username} ({call.from_user.id})")
    await call.answer("⚙️ Error, please use /report", show_alert=True)
    await call.message.edit_text("⤵️ Please choose an option from the menu below", reply_markup=main_kb())


"""@router.message()
async def found_message(message: Message):
    logger.error(f"Found unexpected message: {message.text}, from {message.from_user.username} ({message.from_user.id})")
    await message.answer("⤵️ Please choose an option from the menu below", reply_markup=main_kb())"""
