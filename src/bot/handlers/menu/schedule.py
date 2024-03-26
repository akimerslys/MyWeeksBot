from __future__ import annotations

from aiogram import Router, F, Bot
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger
from src.core.config import settings
from src.bot.loader import lock
from src.image_generator.images import generate_user_schedule_week
from src.bot.keyboards.inline import menu as mkb
from src.bot.keyboards.reply.skip import skip_kb
from src.database.services import users as dbuc, schedule as dbsc, notifs as dbnc
from src.bot.utils.states import AddSchedule, ConfigSchedule
from src.bot.utils import time_localizer as timecom


router = Router(name="schedule")


@router.callback_query(F.data == "schedule")
async def schedule_menu(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    if not await dbuc.get_schedule_time(session, call.from_user.id):
        await call.message.edit_text(
            _("schedule_configure"),
            reply_markup=mkb.config_schedule_hrs()
        )
    else:
        await call.message.edit_reply_markup(reply_markup=mkb.schedule_kb())
    if await state.get_state():
        await state.clear()


@router.callback_query(F.data == "show_schedule_menu")
async def show_schedule_menu(call: CallbackQuery, bot: Bot, session: AsyncSession):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    msg = await bot.send_message(call.message.chat.id, _("WAIT_MESSAGE"))
    user_list: list[tuple] = await dbsc.get_user_schedule_day_time_text(session, call.from_user.id)
    try:
        async with lock:
            image_bytes = await generate_user_schedule_week(user_list)
            await bot.send_photo(call.message.chat.id,
                                 BufferedInputFile(image_bytes.getvalue(),
                                                   filename=f"schedule_{call.from_user.id}.jpeg"))
    except Exception as e:
        logger.critical("WTF????\n" + e)
        await bot.send_message(settings.ADMIN_ID[0], f"ERROR IN GENERATION IMAGE\n{e}")
        await bot.send_message(call.message.chat.id, _("ERROR_MESSAGE"))
    finally:
        await bot.delete_message(call.message.chat.id, msg.message_id)
        logger.info(f"generated schedule")
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
        _("add_schedule_info").format(days=', '.join(map(str, data.get('days'))),
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
        days: list | None = data.get('days')
        time_ = data.get('hours') + ":" + data.get('minutes')

        if data.get('notify'):
            user_notifs: int = await dbuc.count_user_notifs(session, call.from_user.id)
            max_user_notifs: int = await dbuc.get_user_max_notifs(session, call.from_user.id)
            logger.debug(f"type - {type(days)}")
            user_notifs = user_notifs + len(days)
            logger.debug(f"got: {user_notifs})")
            #logger.debug(f"should be {user_notifs}/{max_user_notifs} ({max_user_notifs}<={user_notifs} + {len(days)}")
            #logger.debug(f"{}({type(user_notifs + len(days))} and {max_user_notifs}({type(max_user_notifs)}"
            if max_user_notifs <= user_notifs:
                await call.answer(_("limit_notifs"), show_alert=True)
                await call.message.edit_reply_markup(reply_markup=mkb.schedule_complete_kb(False))
                return

            for day in days:
                dtime = timecom.day_of_week_to_date(day, time_, await dbuc.get_timezone(session, call.from_user.id))
                dtime_to_utc = timecom.localize_datetime_to_utc(dtime, await dbuc.get_timezone(session, call.from_user.id))
                await dbnc.add_notif(session, dtime_to_utc, call.from_user.id, data.get('text'), False, True)

        for day in days:
            await dbsc.add_schedule(session, call.from_user.id, day, time_, data.get('text'))

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


#config schedule
@router.callback_query(F.data == "config_schedule")
async def config_schedule(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        _("schedule_configure"),
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
        _("schedule_configure_confirm").format(hrs=data.get('hours'), min=minutes),
        reply_markup=mkb.config_schedule_confirm()
    )
    await state.set_state(ConfigSchedule.minutes)
    await state.update_data(minutes=minutes)


@router.callback_query(F.data.startswith("config_schedule_confirm_"))
async def config_schedule_confirm(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    if call.data.split("_")[-1] == "yes":
        await call.message.edit_reply_markup(reply_markup=mkb.loading())

        data = await state.get_data()
        config_time = timecom.localize_time_to_utc(data.get('hours'), data.get('minutes'),
                                                   await dbuc.get_timezone(session, call.from_user.id))

        await dbuc.set_schedule_time(session, call.from_user.id, config_time)
        await call.answer(_("schedule_updated"), show_alert=True)
        await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.schedule_kb())
    else:

        await call.message.edit_text(_("please_ch_button"), reply_markup=mkb.main_kb())

    await state.clear()
