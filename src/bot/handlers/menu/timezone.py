from __future__ import annotations

from typing import Union

from aiogram import Router, F, Bot
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

from src.bot.keyboards.inline import menu as mkb
from src.bot.keyboards.inline.guide import start_menu_kb
from src.bot.keyboards.inline import timezone as tzm
from src.database.services import users as dbuc
from src.bot.utils.states import AskLocation, NewUser, AskCountry

router = Router(name="timezone")


@router.callback_query(F.data == "timezone_kb")
async def choose_timezone_kb(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_logged: bool = await dbuc.user_logged(session, call.from_user.id)
    if user_logged:
        await state.clear()

    await call.message.edit_text(_("choose_timezone"), reply_markup=tzm.timezone_simple_keyboard(user_logged))


@router.callback_query(F.data.startswith("set_timezone_"))
async def set_timezone_kb(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    tz = call.data.split('_')[-1]
    try:
        pytz.timezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        await call.answer(_("ERROR_MESSAGE"), show_alert=True)
        logger.error(f"User {call.from_user.id} tried to set invalid timezone: {tz}")
        await call.message.edit_text(_("choose_timezone"), reply_markup=tzm.timezone_simple_keyboard(True))
        return
    await call.message.edit_text(_("timezone_changed").format(tz), reply_markup=mkb.setting_kb())
    if await dbuc.user_exists(session, call.from_user.id):
        await dbuc.set_timezone(session, call.from_user.id, tz)
    else:
        await dbuc.add_user(session, call.from_user.id, call.from_user.first_name, call.from_user.language_code,
                            tz)


@router.callback_query(F.data.startswith("timezone_send_geo_"))
async def ask_for_location(call: CallbackQuery, bot: Bot, state: FSMContext):
    geo_msg = await bot.send_message(
        call.message.chat.id,
        _("send_geo_location"),
        reply_markup=tzm.timezone_geo_reply()
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
            reply_markup=tzm.timezone_geo_reply()
        )
        await state.update_data(tmp_msg=tmp_msg.message_id)
        return

    tmp_msg = await bot.send_message(
        message.from_user.id,
        _("timezone_geo_confirm").format(
            timezone_str=timezone_str, dtime=datetime.now(pytz.timezone(timezone_str)).strftime('%H:%M')),
        reply_markup=tzm.ask_location_confirm()
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
        await bot.send_message(call.from_user.id, _('start_menu').format(lang=data.get('lang'), tz=data.get('tz_pre')),
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


@router.callback_query(F.data.startswith("timezone_show_adv_"))
async def show_all_timezone(call: CallbackQuery):
    await call.asnwer("⚙️ Under construction", show_alert=True)
    """fp = True
    if call.data.split("_")[-1] == 2:
        fp = False

    await call.message.edit_reply_markup(reply_markup=tzm.timezone_advanced_keyboard(fp))"""


def check_country_tz(code: str) -> bool | list:
    a = False
    try:
        a = pytz.country_timezones(code)
    except KeyError:
        pass
    finally:
        return a


@router.callback_query(F.data == "timezone_country")
async def show_country_timezone(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_code = await dbuc.get_language_code(session, call.from_user.id)
    bad_codes = {'uk': 'ua', 'en': 'gb'}
    if user_code in bad_codes:
        user_code = bad_codes[user_code]

    tzs = check_country_tz(user_code)

    user_logged = await dbuc.user_logged(session, call.from_user.id)

    msg = await call.message.edit_text(text=_("timezone_contry_menu"),
                                       reply_markup=tzm.timezone_country_kb(tzs, False, user_logged),
                                       disable_web_page_preview=True)

    if user_logged:
        await state.set_state(AskCountry.ask_country)
    else:
        await state.set_state(NewUser.ask_location)

    await state.update_data(tmp_id=msg.message_id)


@router.callback_query(F.data == 'timezone_country_extended')
async def show_country_tz_ext(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=tzm.timezone_country_kb(extended=True))


@router.message(AskCountry.ask_country)
@router.message(NewUser.ask_location)
@router.callback_query(F.data.startswith("timezone_country_"))
async def show_country_timezones(event: Union[CallbackQuery, Message], bot: Bot, state: FSMContext):
    if isinstance(event, CallbackQuery):
        call_data = event.data.split('/')[-1]
        user_id = event.from_user.id
        message_id = event.message.message_id
        chat_id = event.message.chat.id
    elif isinstance(event, Message):
        call_data = event.text
        user_id = event.from_user.id
        message_id = event.message_id
        chat_id = event.chat.id
    else:
        return  # Invalid event type

    tz_list = check_country_tz(call_data)
    if not tz_list:
        await bot.send_message(user_id, _("timezone_country_invalide_code"))
        return

    state_ = await state.get_state()
    new_user = await dbuc.user_logged()

    if (not new_user or state_ == AskCountry.ask_country) and isinstance(event, Message):
        data = await state.get_data()
        await bot.delete_message(chat_id, message_id)
        await bot.edit_message_text(_("choose_timezone"), chat_id, data.get("tmp_id"),
                                    reply_markup=tzm.timezone_country_list_kb(tz_list, new_user))
    else:
        await event.message.edit_text(_("choose_timezone"), reply_markup=tzm.timezone_country_list_kb(tz_list, new_user))

