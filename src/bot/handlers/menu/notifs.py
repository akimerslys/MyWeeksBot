from __future__ import annotations

from aiogram import Router, F, Bot
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.i18n import gettext as _
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger
from datetime import datetime, timedelta
import pytz

from src.core.config import settings
from src.bot.keyboards.inline import menu as mkb
from src.bot.keyboards.inline.calendar import SimpleCalendar, SimpleCalendarCallback
from src.bot.keyboards.reply.skip import skip_kb
from src.database.services import users as dbuc, notifs as dbnc
from src.bot.utils.states import AddNotif, ChangeNotif
from src.bot.utils import time_localizer as timecom


router = Router(name="notifs")


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
    user_time = timecom.localize_datetimenow_to_timezone(await dbuc.get_timezone(session, call.from_user.id))
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
    await call.message.edit_text(_("choose_time_for_date").format(date=call.data[14:]))
    if not timecom.is_today(datetime.strptime(f"{call.data[14:]}", "%Y %m %d"),
                            await dbuc.get_timezone(session, call.from_user.id)):
        await call.message.edit_reply_markup(reply_markup=mkb.hours_kb())
    else:
        date = timecom.localize_datetimenow_to_timezone(await dbuc.get_timezone(session, call.from_user.id))
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

    try:
        id = await dbnc.add_notif(session,
                                  timecom.localize_datetime_to_utc(
                                      datetime.strptime(f"{data.get('date')} {data.get('hours')} {data.get('minutes')}",
                                                        # converts user's time to utc format
                                                        "%Y %m %d %H %M"),
                                      await dbuc.get_timezone(session, call.from_user.id)),
                                  call.from_user.id,
                                  data.get('text'),
                                  repeat_daily,
                                  repeat_weekly)
        if not id:
            await call.answer(_("limit_notifs"), show_alert=True)
            await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.main_kb())
            await state.clear()
            return
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
    user_notif = await dbnc.get_notif(session, int(call.data.split("_")[-1]))
    if not user_notif:
        await call.answer("Notification does not exist")
        return
    await call.message.edit_text(
        _("manage_one_notif").format(
            status=_('active') if user_notif.active else _('inactive'),
            date=user_notif.date.strftime('%d %m %Y'),
            time=user_notif.date.strftime('%H:%M'),
            text=user_notif.text,
            #repeat=repeat_to_str(user_notif.repeat_daily, user_notif.repeat_weekly)
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
    await bot.delete_messages(message.from_user.id, [data.get('tmp_msg'), message.message_id])
    await state.clear()
    user_notif = await dbnc.get_notif(session, notif_id)
    await bot.send_message(
        message.from_user.id,
        _("manage_one_notif").format(
            status=_('active') if user_notif.active else _('inactive'),
            date=user_notif.date.strftime('%d %m %Y'),
            time=user_notif.date.strftime('%H:%M'),
            text=user_notif.text[:31],
            #repeat=_(repeat_to_str(user_notif.repeat_daily, user_notif.repeat_weekly))
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
    await dbnc.delete_notif(session, notif_id, call.from_user.id)
    await call.answer(_("notif_deleted"), show_alert=True)
    await call.message.edit_text(_("your_notifs"), reply_markup=mkb.manage_notifs_kb(
        await dbnc.get_user_notifs(session, call.from_user.id)))

