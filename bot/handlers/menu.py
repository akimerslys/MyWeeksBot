from __future__ import annotations

import time
from datetime import datetime, timedelta, time
import pytz
from aiogram import Router, F, Bot
from aiogram.utils.deep_linking import create_start_link
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
from bot.keyboards.inline.calendar import SimpleCalendar, SimpleCalendarCallback
from bot.keyboards.inline.guide import start_menu_kb
from bot.keyboards.inline.timezone import timezone_simple_keyboard, timezone_advanced_keyboard, timezone_geo_reply, \
    ask_location_confirm
from bot.keyboards.reply.skip import skip_kb
from bot.services import users as dbuc, notifs as dbnc, schedule as dbsc
from bot.utils.last_commits import get_changelog
from bot.utils.states import AddNotif, AskLocation, ChangeNotif, AddSchedule, NewUser, ConfigSchedule
from bot.utils import time_localizer as timecom          # timecommands
from bot.utils.notif_repeat import repeat_to_str

router = Router(name="menu")


# DO NOT SPLIT THIS FILE TO ROUTERS! IT WILL BE IMPLEMENTED IN THE FUTURE

# TODO ADD NOTIFICATIONS TO THE DATABASE                                        #DONE
# TODO ADD TIMEZONE TO THE NOTIFICATIONS                                        #DONE
# TODO ADD TIMEZONE SETTING FOR FIRST USER                                      #DONE (NEED MORE TESTS)
# TODO SORT WEEKDAYS BY TODAY'S DAY (IF WEDNESDAY, WEDNESDAY IS FIRST)          #DONE (NEED MORE TESTS)
# TODO FIX TODAY BUTTON, FIX RANGES (CALENDAR)                                  #DONE (NEED MORE TESTS)
# TODO INTEGRATE PROFILE TO MENU                                                #NEED CHANGES
# TODO DETERMINE SOLUTION FOR PREMIUM/EXTRA FEATURES                            # every 5$ gives you 10 notifications
# TODO MAKE ADMIN PANEL(in tg or on the web, prefer tg)
# TODO LOCALIZATION
# TODO REWRITE ADD_NOTIF_REPEAT / OPTIMIZE ADD_NOTIF_COMPLETE                   # DONE (NEED MORE TESTS)
# TODO REWRITE MANAGE_NOTIF / TO CHOOSE NOTIFS BY DATE / OR CALENDAR (idk)
# TODO ADD FUNC DELETE ALL INFORMATION ABOUT USER IN PROFILE                    # DONE
# TODO SHARE NOTIF BUTTON                                                       # DONE (NEED MORE TESTS)
# TODO INLINE MOD (CREATE NOTIFICATION/SHARE SCHEDULE)
# TODO BLOCK USER COMMAND + BLOCK MIDDLEWARE                                    # DONE
# TODO REMAKE CHANGELOG
# TODO MAKE INFO WHEN NOTIF WILL BE SENT (IN 5 hrs, in 2 days, etc)
# TODO MAKE INFO HOW MANY PEOPLE ADDED YOUR NOTIFICATION
# TODO CONNECT NOTIFS TO SCHEDULE                                               # NO NEEDED
# TODO SHARE SCHEDULE BUTTON                                                    # NO NEEDED
# TODO ADD TOTAL SHARED TO EVERY NOTIF

# MAIN
@router.callback_query(F.data == "main_kb")
async def menu_back(call: CallbackQuery):
    await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.main_kb())


# MY WEEKS
# SCHEDULE
@router.callback_query(F.data == "schedule")
async def schedule_menu(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    if not await dbuc.get_schedule_time(session, call.from_user.id):
        await call.message.edit_text(
            _("Lets configure your schedule\nWhen we should send your schedule? (everyday)"),
            reply_markup=mkb.config_schedule_hrs()
        )
    else:
        await call.message.edit_reply_markup(reply_markup=mkb.schedule_kb())
    if await state.get_state():
        await state.clear()


@router.callback_query(F.data == "show_schedule_menu")
async def show_schedule_menu(call: CallbackQuery, bot: Bot, session: AsyncSession):
    start = time.time()
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    msg = await bot.send_message(call.message.chat.id, _("WAIT_MESSAGE"))
    user_list = await dbsc.get_user_schedule_day_time_text(session, call.from_user.id)
    try:
        async with lock:
            image_bytes = await generate_user_schedule_week(session, user_list)
            await bot.send_photo(call.message.chat.id,
                                 BufferedInputFile(image_bytes.getvalue(),
                                                   filename=f"schedule_{call.from_user.id}.jpeg"))
    except Exception as e:
        logger.critical("WTF????\n" + e)
        await bot.send_message(settings.ADMIN_ID[1], f"ERROR IN GENERATION IMAGE\n{e}")
        await bot.send_message(call.message.chat.id, _("ERROR_MESSAGE"))
    finally:
        await bot.delete_message(call.message.chat.id, msg.message_id)
        logger.info(f"generated schedule, it tooks: {time.time() - start}")
    await bot.send_message(call.message.chat.id, _("please_ch_button"), reply_markup=mkb.schedule_kb(True))


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
        await call.message.edit_text(_("choose_days"), reply_markup=mkb.add_schedule_days_kb([]))


@router.callback_query(F.data == "schedule_add_go_to_hrs")
async def schedule_add_hours(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('days'):
        await call.answer(_("choose_one_day"), show_alert=True)
        return
    await call.message.edit_text(_("choose_hours"), reply_markup=mkb.hours_schedule_kb())
    await state.set_state(AddSchedule.hours)


@router.callback_query(F.data.startswith("schedule_add_hours_"))
async def schedule_add_minutes(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(_("choose_minute"), reply_markup=mkb.minute_schedule_kb())
    await state.set_state(AddSchedule.minutes)
    if not call.data[17:] == "back":
        await state.update_data(hours=call.data[19:])


@router.callback_query(F.data.startswith("schedule_add_minute_"))
async def schedule_add_text(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.delete()
    tmp_msg = await bot.send_message(call.from_user.id, _("add_text"), reply_markup=skip_kb())
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
        _("add_schedule_info").format(days=data.get('days'),
                                      hours=data.get('hours'),
                                      minutes=data.get('minutes'),
                                      text=message.text),
        reply_markup=mkb.schedule_complete_kb(False)
    )
    await state.update_data(notify=False)


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
        await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.schedule_kb())
    else:
        data = await state.get_data()
        days = data.get('days')
        time = data.get('hours') + ":" + data.get('minutes')
        if data.get('notify') is True:
            user_notifs = await dbnc.count_user_notifs(session, call.from_user.id)
            max_user_notifs = await dbuc.get_user_max_notifs(session, call.from_user.id)
            if max_user_notifs <= user_notifs + len(days):
                await call.answer(_("limit_notifs"), show_alert=True)
                await call.message.edit_reply_markup(reply_markup=mkb.schedule_complete_kb(False))
                return
            for day in days:
                dtime = await timecom.day_of_week_to_date(day, time, await dbuc.get_timezone(session, call.from_user.id))
                dtime_to_utc = await timecom.localize_datetime_to_utc(dtime, await dbuc.get_timezone(session, call.from_user.id))
                await dbnc.add_notif(session, dtime_to_utc, call.from_user.id, data.get('text'), False, True)
        for day in days:
            await dbsc.add_schedule(session, call.from_user.id, day, time, data.get('text'))
        await call.answer(_("schedule_updated"), show_alert=True)
        await call.message.edit_reply_markup(reply_markup=mkb.back_main_schedule())
    await state.clear()


# MANAGE SCHEDULE
@router.callback_query(F.data == "manage_schedule")
async def manage_schedule(call: CallbackQuery, session: AsyncSession):
    user_schedule = await dbsc.get_user_schedule(session, call.from_user.id)
    if not user_schedule:
        await call.answer(_("no_schedule"), show_alert=True)
        return
    await call.message.edit_text(
        _("your_schedule"),
        reply_markup=mkb.manage_schedule_kb()
    )


@router.callback_query(F.data.startswith("manage_schedule_day_"))
async def manage_schedule_day(call: CallbackQuery, session: AsyncSession):
    day = call.data.split("_")[-1]
    user_day_schedule = await dbsc.get_user_schedule_by_day(session, call.from_user.id, day)
    await call.message.edit_text("📆 " + _(day) + ":",
                                 reply_markup=mkb.manage_schedule_day_kb(user_day_schedule)
                                 )


@router.callback_query(F.data.startswith("manage_schedule_id_"))
async def manage_schedule_id(call: CallbackQuery, session: AsyncSession):
    id = int(call.data.split("_")[-1])
    user_schedule = await dbsc.get_one_schedule(session, id)
    await call.message.edit_text(
        _("manage_one_schedule").format(
            day=_(user_schedule.day),
            time=user_schedule.time,
            text=user_schedule.text
        ), reply_markup=mkb.manage_schedule_info_kb(id))


@router.callback_query(F.data.startswith("schedule_delete_"))
async def manage_schedule_delete(call: CallbackQuery, session: AsyncSession):
    id = int(call.data.split("_")[-1])
    await dbsc.delete_one_schedule(session, id)
    await call.answer(_("schedule_deleted"))
    await call.message.edit_text(_("your_schedule"), reply_markup=mkb.manage_schedule_kb())


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
        _("choose_day"),
        reply_markup=mkb.add_notif_first_kb(await dbuc.get_timezone(session, call.from_user.id)))


# CHOOSE DAY WITH CALENDAR

@router.callback_query(F.data == "open_calendar")
async def nav_cal_handler(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(AddNotif.date)
    user_time = pytz.timezone(await dbuc.get_timezone(session, call.from_user.id)).localize(
        datetime.utcnow()).astimezone(
        pytz.utc)
    await call.message.edit_text(
        _("select_date"),
        reply_markup=await SimpleCalendar().start_calendar(user_time.year, user_time.month, user_time)
    )


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(call: CallbackQuery, state: FSMContext, callback_data: CallbackData,
                                  session: AsyncSession):
    calendar = SimpleCalendar(
        locale=await dbuc.get_language_code(session, call.from_user.id), show_alerts=True
    )
    user_time = await timecom.localize_datetimenow_to_timezone(await dbuc.get_timezone(session, call.from_user.id))
    calendar.set_dates_range(user_time - timedelta(days=1),
                             user_time + timedelta(days=365))
    selected, date = await calendar.process_selection(call, callback_data)
    if selected:
        await call.message.edit_text(
            _('choose_time_for_date').format(date=date.strftime("%d %m %Y")),
            reply_markup=mkb.hours_kb()
        )
        await state.update_data(date=date.strftime("%Y %m %d"))
        await state.set_state(AddNotif.hours)


# CHOOSE DAY HOUR TIME
@router.callback_query(F.data.startswith("set_notif_day_"))
async def add_notif_ask_hour(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.update_data(date=call.data[14:])
    await state.set_state(AddNotif.hours)
    await call.message.edit_text("choose_time_for_date".format(date=call.data[14:]))
    if not await timecom.is_today(datetime.strptime(f"{call.data[14:]}", "%Y %m %d"),
                          await dbuc.get_timezone(session, call.from_user.id)):
        await call.message.edit_reply_markup(reply_markup=mkb.hours_kb())
    else:
        date = await timecom.localize_datetimenow_to_timezone(await dbuc.get_timezone(session, call.from_user.id))
        await call.message.edit_reply_markup(reply_markup=mkb.hours_kb(int(date.strftime("%H"))))


@router.callback_query(F.data.startswith("set_notif_hour_"))
async def add_notif_ask_minute(call: CallbackQuery, state: FSMContext):
    await state.update_data(hours=call.data[15:])
    await state.set_state(AddNotif.minutes)
    await call.message.edit_text(
        _("choose_minute"),
        reply_markup=mkb.minute_kb(call.data[15:])
    )


@router.callback_query(F.data.startswith("set_notif_minute_"))
async def add_notif_ask_text(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(minutes=call.data[17:])
    await bot.delete_message(call.from_user.id, call.message.message_id)
    tmp_msg = await bot.send_message(
        call.from_user.id,
        _("add_text_notif"),
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
    # full_date = datetime.strptime(f"{data.get('date')} {data.get('hours')}:{data.get('minutes')}", "%Y %m %d %H:%M")

    await bot.send_message(
        message.from_user.id,
        _("add_notif_info").format(
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
    query = call.data[11:]
    if query == "1":
        await state.update_data(repeat_daily=True)
        await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_kb(1))
    elif query == "2":
        await state.update_data(repeat_weekly=True)
        await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_kb(2))
    elif query == "3":
        await state.update_data(repeat_daily=True)
        await state.update_data(repeat_weekly=True)
        await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_kb(3))
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
async def add_notification_finish(call: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    await call.message.edit_reply_markup(reply_markup=mkb.loading())
    if not await state.get_state():
        await call.answer(_("ERROR_MESSAGE"), show_alert=True)
        await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.main_kb())
        return
    data = await state.get_data()
    repeat_daily = data.get('repeat_daily')
    repeat_weekly = data.get('repeat_weekly')
    if not await dbuc.is_premium(session, call.from_user.id) and repeat_daily and not repeat_weekly:
        await call.answer(_("need_premium"), show_alert=True)
        await state.clear()
        await call.message.edit_reply_markup(reply_markup=mkb.add_notif_repeat_kb(0))
        return

    user_notifs_len = await dbuc.count_user_notifs(session, call.from_user.id)
    max_user_notifs = await dbuc.get_user_max_notifs(session, call.from_user.id)
    if user_notifs_len >= max_user_notifs:
        await call.answer(_("limit_notifs"), show_alert=True)
        await call.message.edit_reply_markup(reply_markup=mkb.back_main_premium())
        return

    try:
        id = await dbnc.add_notif(session,
                                  await timecom.localize_datetime_to_utc(
                                      datetime.strptime(f"{data.get('date')} {data.get('hours')} {data.get('minutes')}",
                                                        # converts user's time to utc format
                                                        "%Y %m %d %H %M"),
                                      await dbuc.get_timezone(session, call.from_user.id)),
                                  call.from_user.id,
                                  data.get('text'),
                                  repeat_daily,
                                  repeat_weekly)

    # TODO IF REPEAT_WEEK ASK TO ADD TO SCHEDULE

    except Exception as e:
        logger.critical("WTF????\n" + e)
        await bot.send_message(settings.ADMIN_ID[1], f"ERROR IN COMPLETE NOTIFICATION\n{e}")
        await call.answer(_("ERROR_MESSAGE"), show_alert=True)
        await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.main_kb())
        await state.clear()
        return

    await call.answer(_("notif_added"), show_alert=True)
    await call.message.edit_reply_markup(reply_markup=mkb.back_main_notif(id))
    await state.clear()


@router.callback_query(F.data.startswith("share_notif_"))
async def share_notification(call: CallbackQuery, bot: Bot, session: AsyncSession):
    tz = await dbuc.get_timezone(session, call.from_user.id)
    payload = f"{call.data[12:]}_{tz}"
    logger.debug("payload: " + payload)
    link = await create_start_link(bot, payload, encode=True)
    logger.info("created link: " + link + "    id: " + call.data[12:])
    await call.message.edit_text(_("share_notif_link") + f'\n\n<code>{link}</code>', reply_markup=mkb.share_kb(link))


# MANAGE NOTIFICATIONS
@router.callback_query(F.data == "manage_notifs")
async def manage_notification(call: CallbackQuery, session: AsyncSession):
    user_notifs = await dbnc.get_user_notifs(session, call.from_user.id)
    if not user_notifs:
        await call.answer(_("no_notifs"), show_alert=True)
        return
    await call.message.edit_text(
        _("your_notifs"),
        reply_markup=mkb.manage_notifs_kb(user_notifs)
    )


@router.callback_query(F.data.startswith("notif_set_"))
async def manage_notif(call: CallbackQuery, session: AsyncSession):
    user_notif = await dbnc.get_notif(session, int(call.data[10:]))
    await call.message.edit_text(
        _("manage_one_notif").format(
            date=user_notif.date.strftime('%d %m %Y'),
            time=user_notif.date.strftime('%H:%M'),
            text=user_notif.text,
        ),
        reply_markup=mkb.notif_info_kb(user_notif)
    )


@router.callback_query(F.data.startswith("notif_text_"))
async def manage_notif_text(call: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeNotif.text)
    tmp_msg = await call.message.edit_text(_("add_text_notif"), reply_markup=None)
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
        _("manage_one_notif").format(
            status=_('active') if user_notif.active else _('inactive'),
            date=user_notif.date.strftime('%d %m %Y'),
            time=user_notif.date.strftime('%H:%M'),
            text=user_notif.text[:31],
            repeat=_(repeat_to_str(user_notif.repeat_daily, user_notif.repeat_weekly))
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
        _("manage_one_notif").format(
            status=_('active') if user_notif.active else _('inactive'),
            date=user_notif.date.strftime('%d %m %Y'),
            time=user_notif.date.strftime('%H:%M'),
            text=user_notif.text
        ),
        reply_markup=mkb.notif_info_kb(user_notif)
    )


@router.callback_query(F.data.startswith("notif_delete_"))
async def manage_notif_delete(call: CallbackQuery, session: AsyncSession):
    notif_id = int(call.data[13:])
    await dbnc.delete_notif_fake(session, notif_id)
    await call.answer(_("notif_deleted"), show_alert=True)
    await call.message.edit_text(_("your_notifs"), reply_markup=mkb.manage_notifs_kb(
        await dbnc.get_user_notifs(session, call.from_user.id)))


# PROFILE
@router.callback_query(F.data == "profile")
async def send_profile(call: CallbackQuery, session: AsyncSession):
    user_info = await dbuc.get_user(session, call.from_user.id)
    await call.message.edit_text(
        f"👤 <b>{user_info.first_name}'s profile</b>:\n"
        f"🔔 Notifications {user_info.active_notifs}/{user_info.max_notifs}\n"
        f"⭐️ Extra features: {'Active' if user_info.is_premium else 'Inactive'}\n"
        f"{'' if not user_info.is_premium else '🕔 Premium until: ' + user_info.premium_until.strftime('%d %m %Y')}\n"
        f"🇬🇧 Language: {user_info.language_code}\n"
        f"🕔 Timezone: {user_info.timezone}\n"
        f"{'🕔 Schedule time: ' + str(user_info.schedule_time) if user_info.schedule_time else ''}",
        reply_markup=mkb.profile_kb()
    )


@router.callback_query(F.data == "profile_delete")
async def delete_profile(call: CallbackQuery):
    await call.message.edit_text(_("profile_delete_confirm"), reply_markup=mkb.delete_profile_kb())


@router.callback_query(F.data.startswith("profile_delete_"))
async def delete_profile_confirm(call: CallbackQuery, session: AsyncSession):
    if call.data.split("_")[-1] == "yes":
        await call.message.edit_reply_markup(reply_markup=mkb.loading())
        await dbuc.delete_user(session, call.from_user.id)
        await dbsc.delete_all_user_schedule(session, call.from_user.id)
        await dbnc.delete_all_user_notifs(session, call.from_user.id)
        await call.answer("Profile deleted, Thank you! ❤️‍🔥", show_alert=True)
    else:
        await call.answer("😳😳😳")
        await call.message.edit_reply_markup(reply_markup=mkb.profile_kb())



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
        _("lang_changed") + ' ' + _("language"),
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
    await call.message.edit_text(_("choose_timezone"), reply_markup=timezone_simple_keyboard(True))


@router.callback_query(F.data.startswith("set_timezone_"))
async def set_timezone_kb(call: CallbackQuery, session: AsyncSession):
    try:
        pytz.timezone(call.data[13:])
    except pytz.exceptions.UnknownTimeZoneError:
        await call.answer(_("ERROR_MESSAGE"), show_alert=True)
        await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.main_kb())
        logger.critical(f"User {call.from_user.id} tried to set invalid timezone: {call.data[13:]}")
        return
    await call.message.edit_text(_("timezone_changed").format(call.data[13:]), reply_markup=mkb.setting_kb())
    if await dbuc.user_exists(session, call.from_user.id):
        await dbuc.set_timezone(session, call.from_user.id, call.data[13:])
    else:
        await dbuc.add_user(session, call.from_user.id, call.from_user.first_name, call.from_user.language_code)


@router.callback_query(F.data.startswith("timezone_send_geo_"))
async def ask_for_location(call: CallbackQuery, bot: Bot, state: FSMContext):
    geo_msg = await bot.send_message(
        call.message.chat.id,
        _("send_geo_location"),
        reply_markup=timezone_geo_reply()
    )
    if await state.get_state():
        await state.set_state(NewUser.ask_location)
        await state.update_data(tmp_msg2=call.message.message_id)
    else:
        await state.set_state(AskLocation.ask_location)
    await state.update_data(tmp_msg=geo_msg.message_id)


@router.message(F.location)
async def handle_location(message: Message, bot: Bot, state: FSMContext):
    if await state.get_state():
        data = await state.get_data()
        await bot.delete_messages(
            message.from_user.id,
            [data.get('tmp_msg'), message.message_id]
        )
    else:
        await state.set_state(AskLocation.ask_location)

    try:
        timezone_str = TimezoneFinder().timezone_at(lng=message.location.longitude, lat=message.location.latitude)
    except Exception as e:
        logger.error(f"Error processing location: {e}\n {message.location.longitude} {message.location.latitude}")
        tmp_msg = await bot.send_message(
            message.from_user.id,
            _("ERROR_MESSAGE"),
            reply_markup=timezone_geo_reply()
        )
        await state.update_data(tmp_msg=tmp_msg.message_id)
        return

    tmp_msg = await bot.send_message(
        message.from_user.id,
        _("timezone_geo_confirm").format(
            timezone_str=timezone_str, dtime=datetime.now(pytz.timezone(timezone_str)).strftime('%H:%M')),
        reply_markup=ask_location_confirm()
    )
    await state.update_data(tmp_msg=tmp_msg.message_id)
    await state.update_data(tz_pre=timezone_str)


@router.message(AskLocation.ask_location)
async def ask_location_cancel(message: Message, bot: Bot, state: FSMContext):
    if message.text == _("cancel_location_btn"):
        data = await state.get_data()
        await bot.delete_messages(message.from_user.id, [message.message_id, data.get('tmp_msg')])
        await state.clear()


@router.message(NewUser.ask_location)
async def ask_location_cancel(message: Message, bot: Bot, state: FSMContext):
    if message.text == _("cancel_location_btn"):
        data = await state.get_data()
        await bot.delete_messages(message.from_user.id, [message.message_id, data.get('tmp_msg')])
        await state.set_state(NewUser.new_user)


@router.callback_query(F.data == "confirm_location")
async def confirm_location(call: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    delete_msgs = [data.get('tmp_msg'), call.message.message_id]

    await call.answer(_("timezone_changed"))
    if await state.get_state() == NewUser.ask_location:
        await state.update_data(tz=data.get('tz_pre'))
        delete_msgs.append(data.get('tmp_msg2'))
        await bot.send_message(call.from_user.id, _('start_menu').format(lang=data.get('lang'), tz=data.get('tz')),
                               reply_markup=start_menu_kb())
    else:
        await dbuc.set_timezone(session, call.from_user.id, data.get('tz_pre'))
        await state.clear()
    await bot.delete_messages(call.from_user.id, delete_msgs)


@router.callback_query(F.data == "cancel_location")
async def cancel_location(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await bot.delete_messages(call.from_user.id, [data.get('tmp_msg'), call.message.message_id])
    await call.answer(_("timezone_not_changed"))
    logger.warning(f"User {call.from_user.id} false location, timezone {data.get('ask_location_confirm')}")
    if not await state.get_state() == NewUser.ask_location:
        await state.clear()


@router.callback_query(F.data == "timezone_show_adv")
async def show_all_timezone(call: CallbackQuery):
    await call.answer(_("⚙️ This function is upgrading"), show_alert=True)


@router.callback_query(F.data == "show_all")
async def show_all_timezone(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=timezone_advanced_keyboard())


#config schedule
@router.callback_query(F.data == "config_schedule")
async def config_schedule(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        _("Lets configure your schedule\nWhen we should send your schedule? (everyday)"),
        reply_markup=mkb.config_schedule_hrs()
    )
    if not await state.get_state():
        await state.set_state(ConfigSchedule.hours)

@router.callback_query(F.data.startswith("schedule_config_hrs_"))
async def config_schedule_hrs(call: CallbackQuery, state: FSMContext):
    hrs = call.data.split("_")[-1]
    await call.message.edit_reply_markup(
        reply_markup=mkb.config_schedule_min(hrs)
    )
    if not await state.get_state():
        await state.set_state(ConfigSchedule.hours)
    await state.update_data(hours=hrs)


@router.callback_query(F.data.startswith("schedule_config_min_"))
async def config_schedule_min(call: CallbackQuery, state: FSMContext):
    minutes = call.data.split("_")[-1]
    data = await state.get_data()
    await call.message.edit_text(
        _("We will send your schedule everyday at {hrs}:{min}, right?").format(hrs=data.get('hours'), min=minutes),
        reply_markup=mkb.config_schedule_confirm()
    )
    await state.set_state(ConfigSchedule.minutes)
    await state.update_data(minutes=minutes)


@router.callback_query(F.data.startswith("config_schedule_confirm_"))
async def config_schedule_confirm(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    if call.data.split("_")[-1] == "yes":
        await call.message.edit_reply_markup(reply_markup=mkb.loading())

        data = await state.get_data()
        config_time = await timecom.localize_time_to_utc(data.get('hours'), data.get('minutes'),
                                                   await dbuc.get_timezone(session, call.from_user.id))

        await dbuc.set_schedule_time(session, call.from_user.id, config_time)
        await call.answer(_("schedule_updated"), show_alert=True)

    await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.main_kb())
    await state.clear()


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
async def ignore(call: CallbackQuery):
    return


@router.callback_query()
async def found_callback(call: CallbackQuery):
    await call.answer("⚙️ Under construction", show_alert=True)


@router.callback_query()
async def found_callback(call: CallbackQuery):
    logger.error(f"Found unexpected callback: {call.data}, from {call.from_user.username} ({call.from_user.id})")
    await call.answer(_("ERROR"), show_alert=True)
    await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.main_kb())


"""@router.message()
async def found_message(message: Message):
    logger.error(f"Found unexpected message: {message.text}, from {message.from_user.username} ({message.from_user.id})")
    print(message)
    await message.answer("⤵️ Please choose an option from the menu below", reply_markup=mkb.main_kb())"""
