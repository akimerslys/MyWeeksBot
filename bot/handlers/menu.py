from __future__ import annotations

import time
from datetime import datetime, timedelta
import pytz
from aiogram import Router, F, Bot
from aiogram.utils.i18n import gettext as _
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from timezonefinder import TimezoneFinder

from bot.core.config import settings
from bot.core.loader import lock
from bot.image_generator.images import generate_user_schedule_week
from bot.keyboards.inline import menu as mkb
from bot.keyboards.inline.calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from bot.keyboards.inline.timezone import timezone_simple_keyboard, timezone_advanced_keyboard, timezone_geo_reply, \
    ask_location_confirm
from bot.keyboards.reply.skip import skip_kb
from bot.services import users as dbuc, notifs as dbnc, schedule as dbsc
from bot.utils.last_commits import get_changelog
from bot.utils.states import AddNotif, AskLocation, ChangeNotif, AddSchedule
from bot.utils.time_localizer import localize_time_to_utc, localize_timenow_to_timezone, is_today, day_of_week_to_date

router = Router(name="menu")


# DO NOT SPLIT THIS FILE TO ROUTERS! IT WILL BE IMPLEMENTED IN THE FUTURE

# TODO ADD NOTIFICATIONS TO THE DATABASE                                        #DONE (NEED MORE TESTS)
# TODO ADD TIMEZONE TO THE NOTIFICATIONS                                        #DONE (NEED MORE TESTS)
# TODO ADD TIMEZONE SETTING FOR FIRST USER                                      #DONE (NEED MORE TESTS)
# TODO SORT WEEKDAYS BY TODAY'S DAY (IF WEDNESDAY, WEDNESDAY IS FIRST)          #DONE (NEED MORE TESTS)
# TODO FIX TODAY BUTTON, FIX RANGES (CALENDAR)                                  #DONE (NEED MORE TESTS)
# TODO INTEGRATE PROFILE TO MENU                                                #NEED CHANGES
# TODO DETERMINE SOLUTION FOR PREMIUM/EXTRA FEATURES                            # every 5$ gives you 10 notifications
# TODO MAKE ADMIN PANEL
# TODO LOCALIZATION
# TODO REWRITE ADD_NOTIF_REPEAT / OPTIMIZE ADD_NOTIF_COMPLETE
# TODO REWRITE MANAGE_NOTIF / TO CHOOSE NOTIFS BY DATE / OR CALENDAR (idk)
# TODO ADD FUNC DELETE ALL INFORMATION ABOUT USER IN PROFILE


# MAIN
@router.callback_query(F.data == "main_kb")
async def menu_back(call: CallbackQuery):
    await call.message.edit_text(_("please"), reply_markup=mkb.main_kb())


# MY WEEKS
# SCHEDULE
@router.callback_query(F.data == "schedule")
async def schedule_menu(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=mkb.schedule_kb())
    if await state.get_state():
        await state.clear()


@router.callback_query(F.data == "show_schedule_menu")
async def show_schedule_menu(call: CallbackQuery, bot: Bot, session: AsyncSession):
    start = time.time()
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    msg = await bot.send_message(call.message.chat.id, _("WAIT_MESSAGE"))
    try:
        async with lock:
            image_bytes = await generate_user_schedule_week(session, call.from_user.id)
            await bot.send_photo(call.message.chat.id,
                                 BufferedInputFile(image_bytes.getvalue(), filename=f"schedule_{call.from_user.id}.jpeg"))
    except Exception as e:
        logger.critical("WTF????\n" + e)
        await bot.send_message(settings.ADMIN_ID[1], f"ERROR IN GENERATION IMAGE\n{e}")
        await bot.send_message(call.message.chat.id, _("⚙️ Error, please use /report"))
    finally:
        await bot.delete_message(call.message.chat.id, msg.message_id)
        logger.info(f"generated schedule, it tooks: {time.time() - start}")
    await bot.send_message(call.message.chat.id, _("Please choose an option below"), reply_markup=mkb.schedule_kb(True))


@router.callback_query(F.data.startswith("schedule_add_day_"))
async def schedule_add(call: CallbackQuery, state: FSMContext):
    calldata = call.data[17:]
    logger.warning(f"calldata: {calldata}")

    if calldata != "0":
        if calldata == "workdays":
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        elif calldata == "weekends":
            days = ["Saturday", "Sunday"]
        else:
            data = await state.get_data()
            days = data.get('days', [])

            if calldata not in days:
                days.append(calldata)
            else:
                days.remove(calldata)

        await state.update_data(days=days)
        logger.warning(f"days: {days}")
        await call.message.edit_reply_markup(
            reply_markup=mkb.add_schedule_days_kb(days)
        )
    else:
        await state.set_state(AddSchedule.days)
        await call.message.edit_text("📅 Choose days", reply_markup=mkb.add_schedule_days_kb([]))


@router.callback_query(F.data == "schedule_add_go_to_hrs")
async def schedule_add_hours(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('days'):
        await call.answer(_("⚙️ Please choose at least one day"), show_alert=True)
        return
    await call.message.edit_text(_("🕔 Choose hours"), reply_markup=mkb.hours_schedule_kb())
    await state.set_state(AddSchedule.hours)


@router.callback_query(F.data.startswith("schedule_add_hours_"))
async def schedule_add_minutes(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(_("🕔 Choose minute"), reply_markup=mkb.minute_schedule_kb())
    await state.set_state(AddSchedule.minutes)
    if not call.data[17:] == "back":
        await state.update_data(hours=call.data[19:])


@router.callback_query(F.data.startswith("schedule_add_minute_"))
async def schedule_add_text(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.delete()
    tmp_msg = await bot.send_message(call.from_user.id, _("Please choose name"), reply_markup=skip_kb())
    await state.set_state(AddSchedule.text)
    await state.update_data(tmp_msg=tmp_msg.message_id)
    if not call.data[18:] == "back":
        await state.update_data(minutes=call.data[20:])


@router.message(AddSchedule.text)
async def schedule_text_complete(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await bot.delete_messages(message.from_user.id, [data.get('tmp_msg'), message.message_id])
    if message.text == _("Skip") or message.text == "Skip":
        await state.update_data(text=None)
    await state.update_data(text=message.text[:31])
    await bot.send_message(
        message.from_user.id,
        f"📅 Days: {data.get('days')}\n"
        f"⏰ Time: {data.get('hours')}:{data.get('minutes')}\n"
        f"📝 Text: {message.text}",
        reply_markup=mkb.schedule_complete_kb(False)
    )


@router.callback_query(F.data.startswith("schedule_add_complete_notify_"))
async def add_notifs_to_schedule(call: CallbackQuery, state: FSMContext):
    if call.data[29:] == "no":
        await state.update_data(notify=False)
        await call.message.edit_reply_markup(reply_markup=mkb.schedule_complete_kb(False))
    elif call.data[29:] == "yes":
        await state.update_data(notify=True)
        await call.message.edit_reply_markup(reply_markup=mkb.schedule_complete_kb(True))


@router.callback_query(F.data.startswith("schedule_add_complete"))
async def schedule_complete(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.message.edit_reply_markup(reply_markup=mkb.loading())
    if call.data[22:] == "no":
        await call.message.edit_text(_("Please choose an option below"), reply_markup=mkb.schedule_kb())
    else:
        data = await state.get_data()
        days = data.get('days')
        time = data.get('hours') + ":" + data.get('minutes')
        if data.get('notify'):
            user_notifs = await dbnc.count_user_notifs(session, call.from_user.id)
            if not await dbuc.is_premium(session, call.from_user.id) and user_notifs + len(days) >= settings.MAX_NOTIFS:
                await call.answer(_("Sorry, you reached the limit of your notifications"), show_alert=True)
                return
            if await dbuc.is_premium(session, call.from_user.id) and user_notifs + len(days) >= settings.MAX_NOTIFS_PREMIUM:
                await call.answer(_("Sorry, you reached the limit of your notifications"), show_alert=True)
                return
        for day in days:
            dtime = await day_of_week_to_date(day, time, await dbuc.get_timezone(session, call.from_user.id))
            dtime_to_utc = await localize_time_to_utc(dtime, await dbuc.get_timezone(session, call.from_user.id))
            await dbnc.add_notif(session, dtime_to_utc, call.from_user.id, data.get('text'), False, True)
        for day in days:
            await dbsc.add_schedule(session, call.from_user.id, day, time, data.get('text'))
        await call.answer(_("✅ Schedule updated"), show_alert=True)
        await call.message.edit_reply_markup(reply_markup=mkb.back_main_schedule())
    await state.clear()


# MANAGE SCHEDULE
@router.callback_query(F.data == "manage_schedule")
async def manage_schedule(call: CallbackQuery, session: AsyncSession):
    user_schedule = await dbsc.get_user_schedule(session, call.from_user.id)
    if not user_schedule:
        await call.answer(_("You don't have any schedules"), show_alert=True)
        return
    await call.message.edit_text(
        _("📝 Your schedules"),
        reply_markup=mkb.manage_schedule_kb(user_schedule)
    )


# NOTIFICATIONS
@router.callback_query(F.data == "notifications")
async def notifications_menu(call: CallbackQuery, state: FSMContext):
    if await state.get_state():
        await state.clear()
    await call.message.edit_reply_markup(reply_markup=mkb.notifications_kb())


@router.callback_query(F.data == "add_notif")
async def add_notification(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    if await state.get_state():
        await state.clear()
    await state.set_state(AddNotif.date)
    await call.message.edit_text(
        _("🕔 Choose day"),
        reply_markup=mkb.add_notif_first_kb(await dbuc.get_timezone(session, call.from_user.id)))


# CHOOSE DAY WITH CALENDAR

@router.callback_query(F.data == "open_calendar")
async def nav_cal_handler(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(AddNotif.date)
    user_time = pytz.timezone(await dbuc.get_timezone(session, call.from_user.id)).localize(
        datetime.utcnow()).astimezone(
        pytz.utc)
    await call.message.edit_text(
        _("Please select a date: "),
        reply_markup=await SimpleCalendar().start_calendar(user_time.year, user_time.month, user_time)
    )


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(call: CallbackQuery, state: FSMContext, callback_data: CallbackData,
                                  session: AsyncSession):
    calendar = SimpleCalendar(
        locale=await get_user_locale(call.from_user), show_alerts=True
    )
    user_time = await localize_timenow_to_timezone(await dbuc.get_timezone(session, call.from_user.id))
    calendar.set_dates_range(user_time - timedelta(days=1),
                             user_time + timedelta(days=365))
    selected, date = await calendar.process_selection(call, callback_data)
    if selected:
        await call.message.edit_text(
            f'🕔 {date.strftime("%d %m %Y")}, please select a time:',
            reply_markup=mkb.hours_kb()
        )
        print(date)
        await state.update_data(date=date.strftime("%Y %m %d"))
        await state.set_state(AddNotif.hours)


# CHOOSE DAY HOUR TIME
@router.callback_query(F.data.startswith("set_notif_day_"))
async def add_notif_ask_hour(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.update_data(date=call.data[14:])
    await state.set_state(AddNotif.hours)
    await call.message.edit_text("🕔 Choose time for {}".format(call.data[14:]))
    if not await is_today(datetime.strptime(f"{call.data[14:]}", "%Y %m %d"),
                          await dbuc.get_timezone(session, call.from_user.id)):
        await call.message.edit_reply_markup(reply_markup=mkb.hours_kb())
    else:
        date = await localize_timenow_to_timezone(await dbuc.get_timezone(session, call.from_user.id))
        await call.message.edit_reply_markup(reply_markup=mkb.hours_kb(int(date.strftime("%H"))))


@router.callback_query(F.data.startswith("set_notif_hour_"))
async def add_notif_ask_minute(call: CallbackQuery, state: FSMContext):
    await state.update_data(hours=call.data[15:])
    await state.set_state(AddNotif.minutes)
    await call.message.edit_text(
        _("Please select a minute: "),
        reply_markup=mkb.minute_kb(call.data[15:])
    )


@router.callback_query(F.data.startswith("set_notif_minute_"))
async def add_notif_ask_text(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(minutes=call.data[17:])
    await bot.delete_message(call.from_user.id, call.message.message_id)
    tmp_msg = await bot.send_message(
        call.from_user.id,
        _("Now name your notification: (max symbols: 34)"),
        reply_markup=skip_kb()
    )
    await state.set_state(AddNotif.text)
    await state.update_data(tmp_msg=tmp_msg.message_id)


@router.message(AddNotif.text)
async def add_notif_text(message: Message, bot: Bot, state: FSMContext):
    if message.text == _("Skip") or message.text == "Skip":
        await state.update_data(text=None)
    else:
        await state.update_data(text=message.text)
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data.get('tmp_msg'))
    full_date = datetime.strptime(f"{data.get('date')} {data.get('hours')}:{data.get('minutes')}", "%Y %m %d %H:%M")

    await bot.send_message(
        message.from_user.id,
        "📅 Date: {}\n⏰ Time: {}:{}\n📝 Text: {}".format(
            data.get('date'), data.get('hours'), data.get('minutes'), data.get('text')
        ),
        reply_markup=mkb.add_notif_repeat_kb(0)
    )
    await message.delete()
    await state.update_data(repeat_daily=False)
    await state.update_data(repeat_weekly=False)
    await state.set_state(AddNotif.repeat_daily)


@router.callback_query(F.data.startswith("repeatable_"))
async def add_notif_repeat(call: CallbackQuery, state: FSMContext):
    if call.data == "repeatable_day":
        await state.update_data(repeat_daily=True)
        await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_kb(1))  # every day
    elif call.data == "repeatable_week":
        await state.update_data(repeat_weekly=True)
        await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_kb(2))  # every_week
    elif call.data == "repeatable_month":
        await state.update_data(repeat_daily=True)
        await state.update_data(repeat_weekly=True)
        await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_kb(3))  # every_month
    else:
        await state.update_data(repeat_daily=False)
        await state.update_data(repeat_weekly=False)
        await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_kb(0))  # none


"""@router.callback_query(F.data == "repeatable_day")
async def add_notif_text_off(call: CallbackQuery, state: FSMContext):
    await state.update_data(repeat_daily=True)
    await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_day_kb())


@router.callback_query(F.data == "repeatable_week")
async def add_notif_text_off(call: CallbackQuery, state: FSMContext):
    await state.update_data(repeat_daily=False)
    await state.update_data(repeat_weekly=True)
    await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_week_kb())


@router.callback_query(F.data == "repeatable_month")
async def add_notification_text_off(call: CallbackQuery, state: FSMContext):
    await state.update_data(repeat_weekly=True)
    await state.update_data(repeat_daily=True)
    await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_month_kb())


@router.callback_query(F.data == "repeatable_none")
async def add_notification_text_off(call: CallbackQuery, state: FSMContext):
    await state.update_data(repeat_daily=False)
    await state.update_data(repeat_weekly=False)
    await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_none_kb())"""


@router.callback_query(F.data == "add_complete")
async def add_notification_finish(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.message.edit_reply_markup(reply_markup=mkb.loading())
    if not await state.get_state():
        await call.answer(_("⚙️ Error, please use /report"), show_alert=True)
        await call.message.edit_text(_("⤵️ Please choose an option from the menu below"), reply_markup=mkb.main_kb())
        return
    data = await state.get_data()
    repeat_daily = data.get('repeat_daily')
    repeat_weekly = data.get('repeat_weekly')
    if not await dbuc.is_premium(session, call.from_user.id) and repeat_daily and not repeat_weekly:
        await call.answer(_("Sorry, you need to buy premium to use this feature"), show_alert=True)
        return

    user_notifs_len = await dbuc.count_user_notifs(session, call.from_user.id)

    if user_notifs_len > settings.MAX_NOTIFS:
        if not await dbuc.is_premium(session, call.from_user.id) or user_notifs_len >= settings.MAX_NOTIFS_PREMIUM:
            await call.answer(_("You have reached the limit of notifications"), show_alert=True)
            await call.message.edit_reply_markup(reply_markup=mkb.back_main_premium())
            await state.clear()
            return

    await dbnc.add_notif(session,
                         await localize_time_to_utc(
                             datetime.strptime(f"{data.get('date')} {data.get('hours')} {data.get('minutes')}",
                                               # converts user's time to utc format
                                               "%Y %m %d %H %M"), await dbuc.get_timezone(session, call.from_user.id)),
                         call.from_user.id,
                         data.get('text'),
                         repeat_daily,
                         repeat_weekly)
    await call.answer(_("✅ Notification added"), show_alert=True)
    await call.message.edit_reply_markup(reply_markup=mkb.back_main_notif())
    await state.clear()


# MANAGE NOTIFICATIONS
@router.callback_query(F.data == "manage_notifs")
async def manage_notification(call: CallbackQuery, session: AsyncSession):
    user_notifs = await dbnc.get_user_notifs(session, call.from_user.id)
    if not user_notifs:
        await call.answer(_("You don't have any notifications"), show_alert=True)
        return
    await call.message.edit_text(
        "📝 Your notifications",
        reply_markup=mkb.manage_notifs_kb(user_notifs)
    )


@router.callback_query(F.data.startswith("notif_set_"))
async def manage_notif(call: CallbackQuery, session: AsyncSession):
    user_notif = await dbnc.get_notif(session, int(call.data[10:]))
    await call.message.edit_text(
        _("{status}\n📅 Date: {date}\n⏰ Time: {time}\n📝 Text: {text}\n🔔 Repeat: will be fixed").format(
            status=_('🟩 Active') if user_notif.active else _('🟥 Inactive'),
            date=user_notif.date.strftime('%d %m %Y'),
            time=user_notif.date.strftime('%H:%M'),
            text=user_notif.text
        ),
        reply_markup=mkb.notif_info_kb(user_notif)
    )


@router.callback_query(F.data.startswith("notif_text_"))
async def manage_notif_text(call: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeNotif.text)
    tmp_msg = await call.message.edit_text(_("Update name of your notification"), reply_markup=None)
    await state.update_data(tmp_msg=tmp_msg.message_id)
    await state.update_data(repeat_daily=int(call.data[11:]))


@router.message(ChangeNotif.text)
async def manage_notif_text_finish(message: Message, bot: Bot, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    notif_id = data.get('repeat_daily')
    await dbnc.update_notif_text(session, notif_id, message.text)
    await bot.delete_messages(message.from_user.id, data.get('tmp_msg'), message.message_id)
    await state.clear()
    user_notif = await dbnc.get_notif(session, notif_id)
    await bot.send_message(
        message.from_user.id,
        _("{status}\n📅 Date: {date}\n⏰ Time: {time}\n📝 Text: {text}\n🔔 Repeat: will be fixed").format(
            status=_('🟩 Active') if user_notif.active else _('🟥 Inactive'),
            date=user_notif.date.strftime('%d %m %Y'),
            time=user_notif.date.strftime('%H:%M'),
            text=user_notif.text
        ),
        reply_markup=mkb.notif_info_kb(user_notif))


@router.callback_query(F.data.startswith("notif_active_"))
async def manage_notif_active(call: CallbackQuery, session: AsyncSession):
    notif_id = int(call.data[13:])
    user_notif = await dbnc.get_notif(session, notif_id)
    if user_notif.active:
        await dbnc.update_notif_active(session, notif_id, False)
    else:
        await dbnc.update_notif_active(session, notif_id, True)

    user_notif = await dbnc.get_notif(session, notif_id)
    await call.message.edit_text(
        _("{status}\n📅 Date: {date}\n⏰ Time: {time}\n📝 Text: {text}\n🔔 Repeat: will be fixed").format(
            status=_('🟩 Active') if user_notif.active else _('🟥 Inactive'),
            date=user_notif.date.strftime('%d %m %Y'),
            time=user_notif.date.strftime('%H:%M'),
            text=user_notif.text
        ),
        reply_markup=mkb.notif_info_kb(user_notif)
    )


@router.callback_query(F.data.startswith("notif_delete_"))
async def manage_notif_delete(call: CallbackQuery, session: AsyncSession):
    notif_id = int(call.data[13:])
    await dbnc.delete_notif(session, notif_id)
    await call.answer(_("✅ Notification deleted"), show_alert=True)
    await call.message.edit_text(_("📝 Your notifications"), reply_markup=mkb.manage_notifs_kb(
        await dbnc.get_user_notifs(session, call.from_user.id)))


# PROFILE
@router.callback_query(F.data == "profile")
async def send_profile(call: CallbackQuery, session: AsyncSession):
    user_info = await dbuc.get_user(session, call.from_user.id)
    await call.message.edit_text(
        f"<b>{user_info.first_name}'s profile</b>:\n"
        f"{user_info.active_notifs} Active notifications\n"
        f"Extra features: {'Active' if user_info.is_premium else 'Inactive'}\n"
        f"{'' if not user_info.is_premium else 'Premium until: ' + user_info.premium_until.strftime('%d %m %Y')}\n"
        f"Language: {user_info.language_code}\n"
        f"Timezone: {user_info.timezone}",
        reply_markup=mkb.back_main_premium()
    )


# SETTINGS
@router.callback_query(F.data == 'settings_kb')
async def place_settings_kb(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=mkb.setting_kb())


@router.callback_query(F.data == "lang_kb")
async def choose_language_kb(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=mkb.language_kb())


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language_kb(call: CallbackQuery, session: AsyncSession):
    await call.message.edit_text(
        _("🌐 Language changed to {lang}").format(lang=call.data[9:]),
        reply_markup=mkb.setting_kb()
    )
    if await dbuc.get_language_code(session, call.from_user.id) != call.data[9:]:
        await dbuc.set_language_code(session, call.from_user.id, call.data[9:])


@router.callback_query(F.data == "add_lang")
async def add_language_kb(call: CallbackQuery):
    await call.answer(
        "⚙️ This function is not available yet\nSoon u will have ability to add your own language",
        show_alert=True)


@router.callback_query(F.data == "timezone_kb")
async def choose_timezone_kb(call: CallbackQuery):
    await call.message.edit_text(_("🕔 Choose your timezone"), reply_markup=timezone_simple_keyboard())


@router.callback_query(F.data.startswith("set_timezone_"))
async def set_timezone_kb(call: CallbackQuery, session: AsyncSession):
    try:
        pytz.timezone(call.data[13:])
    except pytz.exceptions.UnknownTimeZoneError:
        await call.answer(_("⚙️ Error, Invalid Timezone"), show_alert=True)
        await call.message.edit_text(_("⤵️ Please choose an option from the menu below"), reply_markup=mkb.main_kb())
        logger.error(f"User {call.from_user.id} tried to set invalid timezone: {call.data[13:]}")
        return
    await call.message.edit_text(_("🕔 Timezone changed to {}").format(call.data[13:]), reply_markup=mkb.setting_kb())
    if await dbuc.user_exists(session, call.from_user.id):
        await dbuc.set_timezone(session, call.from_user.id, call.data[13:])
    else:
        await dbuc.add_user(session, call.from_user.id, call.from_user.first_name, call.from_user.language_code)


@router.callback_query(F.data == "timezone_send_geo")
async def ask_for_location(call: CallbackQuery, bot: Bot, state: FSMContext):
    geo_msg = await bot.send_message(
        call.message.chat.id,
        _("Send your location or press the button below to send it\n<i>Important note: <u>We don't store your "
          "location!</u></i>"),
        reply_markup=timezone_geo_reply()
    )
    await state.set_state(AskLocation.ask_location)
    await state.update_data(ask_location=geo_msg.message_id)


@router.message(AskLocation.ask_location)
async def handle_location(message: Message, bot: Bot, state: FSMContext, AskLocation):
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
                _("Unexpected Error. Please, try again."),
                reply_markup=timezone_geo_reply()
            )
            await state.update_data(ask_location=tmp_msg.message_id)
            return

        tmp_msg = await bot.send_message(
            message.from_user.id,
            _("🕔 This timezone correct? {timezone_str}\nYour Time should be {dtime}").format(
                timezone_str=timezone_str, dtime=datetime.now(pytz.timezone(timezone_str)).strftime('%H:%M')),
            reply_markup=ask_location_confirm()
        )
        await state.update_data(ask_for_location=tmp_msg.message_id)
        await state.update_data(ask_location_confirm=timezone_str)
        await state.set_state(AskLocation.ask_location_confirm)


@router.callback_query(F.data == "confirm_location")
async def confirm_location(call: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if await dbuc.user_exists(session, call.from_user.id):
        await dbuc.set_timezone(session, call.from_user.id, call.data[13:])
    else:
        await dbuc.add_user(session, call.from_user.id, call.from_user.first_name, call.from_user.language_code)
    await bot.delete_message(call.from_user.id, data.get('ask_for_location'))
    await call.answer(_("✅ Timezone changed"))
    await state.clear()


@router.callback_query(F.data == "cancel_location")
async def cancel_location(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(call.from_user.id, data.get('ask_for_location'))
    await call.answer(_("📛 Timezone not set"))
    logger.warning(f"User {call.from_user.id} false location, timezone {data.get('ask_location_confirm')}")
    await state.clear()


@router.callback_query(F.data == "timezone_show_adv")
async def show_all_timezone(call: CallbackQuery):
    await call.answer(_("⚙️ This function is upgrading"), show_alert=True)


@router.callback_query(F.data == "show_all")
async def show_all_timezone(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=timezone_advanced_keyboard())


# CHANGELOG
@router.callback_query(F.data == "show_changelog")
async def send_changelog(call: CallbackQuery):
    message_changelog = "".join(await get_changelog(5))
    await call.message.edit_text(
        f"📝 Latest Updates\n\n{message_changelog}",
        reply_markup=mkb.back_main()
    )


# PREMIUM
@router.callback_query(F.data == "buy_premium")
async def buy_premium(call: CallbackQuery):
    await call.answer(
        "⚙️ This function is not available yet",
        show_alert=True
    )


@router.callback_query(F.data == "ignore")
async def found_callback(call: CallbackQuery):
    await call.answer("⚙️ Under construction", show_alert=True)


@router.callback_query()
async def found_callback(call: CallbackQuery):
    await call.answer("⚙️ Under construction", show_alert=True)


@router.callback_query()
async def found_callback(call: CallbackQuery):
    logger.error(f"Found unexpected callback: {call.data}, from {call.from_user.username} ({call.from_user.id})")
    await call.answer(_("⚙️ Error, please use /report"), show_alert=True)
    await call.message.edit_text(_("⤵️ Please choose an option from the menu below"), reply_markup=mkb.main_kb())


"""@router.message()
async def found_message(message: Message):
    logger.error(f"Found unexpected message: {message.text}, from {message.from_user.username} ({message.from_user.id})")
    await message.answer("⤵️ Please choose an option from the menu below", reply_markup=main_kb())"""
