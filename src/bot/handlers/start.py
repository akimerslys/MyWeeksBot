import pytz
from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.i18n import gettext as _
from aiogram.utils.payload import decode_payload
from aiogram.exceptions import TelegramBadRequest
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, ProgrammingError

from src.bot.keyboards.inline.guide import guide_start_kb, start_menu_kb, new_lang_kb
from src.bot.keyboards.inline.menu import main_kb
from src.bot.keyboards.inline.timezone import timezone_simple_keyboard
from src.bot.services import users as dbuc
from src.bot.services.notifs import add_notif, get_notif
from src.bot.utils.time_localizer import localize_datetime_to_timezone
from src.bot.utils.states import NewUser
from src.database.models import NotifModel

router = Router(name="start")


# TODO OPTIMIZE !!! !! !! !! ! !! !! OR GAY
# TRAAASH CODDEEEEEEEEEEEEEEEE REWRITE IT


@router.message(CommandStart(deep_link=True))
async def start_message_deeplink(message: Message, bot: Bot, command: CommandObject, session: AsyncSession,
                                 state: FSMContext):
    args = command.args
    logger.debug(f"got args {args}")

    payload = args

    if args[0] or args != '_':
        payload = decode_payload(args)

    logger.debug(f"got payload {payload}")
    notif_args: list = payload.split("_", 2)
    logger.debug(notif_args)

    shared_notif: NotifModel | None
    notif_date: str

    try:

        shared_notif = await get_notif(session, int(notif_args[0]))

        if not shared_notif:
            logger.error(f"Error while getting notif from payload: {payload}")
            await bot.send_message(message.from_user.id, _("ERROR_MESSAGE"))
            return

    except (IntegrityError, ProgrammingError) as e:

        logger.error(f"Error while getting notif from payload: {e}")
        await bot.send_message(message.from_user.id, _("ERROR_MESSAGE"))
        return

    if not await dbuc.user_logged(session, message.from_user.id):

        await bot.send_message(message.from_user.id,
                               _("deeplink_got_notif").format(
                                   date=(localize_datetime_to_timezone(shared_notif.date, notif_args[1])).strftime(
                                       "%d/%m/%Y %H:%M"),
                                   tz=notif_args[1],
                                   text=shared_notif.text)
                               )
        if await state.get_state() is not NewUser.new_user:
            await state.clear()
            await state.set_state(NewUser.new_user)
            await state.update_data(tz='UTC', lang='en', notif_id=int(notif_args[0]))

        data = await state.get_data()

        await bot.send_message(message.from_user.id, _('start_menu').format(lang=data.get('lang'), tz=data.get('tz')),
                               reply_markup=start_menu_kb())
    else:
        tz_usr: str = await dbuc.get_timezone(session, message.from_user.id)
        await bot.send_message(message.from_user.id,
                               _("notif_deeplink_logged").format(
                                   date_usr=(localize_datetime_to_timezone(shared_notif.date, tz_usr)).strftime(
                                       "%d/%m/%Y %H:%M"),
                                   tz_usr=tz_usr,
                                   date=shared_notif.date.strftime("%d/%m/%Y %H:%M"),
                                   tz=notif_args[1],
                                   text=shared_notif.text))
        await add_notif(session, shared_notif.date, message.from_user.id, shared_notif.text)
        await bot.send_message(
            message.from_user.id,
            _("please_ch_button"),
            reply_markup=main_kb()
        )


@router.message(CommandStart(deep_link=False))
async def start_message(message: Message, bot: Bot, session: AsyncSession, state: FSMContext):
    if not await dbuc.user_logged(session, message.from_user.id):
        if await state.get_state() is not NewUser.new_user:
            await state.clear()
            await state.set_state(NewUser.new_user)
            await state.update_data(tz='UTC', lang='en')

        data = await state.get_data()

        await bot.send_message(
            message.from_user.id,
            _('start_menu').format(
                lang=data.get('lang'), tz=data.get('tz')),
            reply_markup=start_menu_kb()
        )

    else:
        await bot.send_message(
            message.from_user.id,
            _("please_ch_button"),
            reply_markup=main_kb()
        )


"""@router.callback_query(F.data.startswith("set_new_lang_"))
async def set_new_lang(call: F.CallbackQuery, bot: Bot, session: AsyncSession):
    lang = call.data.split("_")[-1]
    await call.answer(_("lang_changed_to{}").format(lang))
    await set_language_code(session, call.from_user.id, lang)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_animation(call.from_user.id,
                             animation="AgACAgQAAxkDAAILJ2XToPF21rkdS-ga9-QSbSEgYchiAAI0wTEbD9KQUlbT9tpTV-ICAQADAgADdwADNAQ",
                             caption=_("guide_caption"),
                             reply_markup=guide_start_kb())
    logger.info(f"New user {call.from_user.id} changed language to {lang}")


@router.callback_query(F.data.startswith("guide_page_"))
async def guide_page(call: F.CallbackQuery):
    page = int(call.data.split("_")[-1])
    if page == 2:
        await call.message.edit_media(media=InputMediaAnimation(
            media="AgADCBcAAvxfAUo",
                                      reply_markup=main_kb()))
    await call.answer("meow!")
    logger.info(f"User {call.from_user.id} switched to guide page {page}")"""


@router.callback_query(F.data == "start_kb")
async def start_kb(call: F.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(
        text=_('start_menu').format(lang=data.get('lang'), tz=data.get('tz')),
        reply_markup=start_menu_kb())
    logger.info(f"User {call.from_user.id} switched to start menu")


@router.callback_query(F.data == "new_lang_kb")
async def new_lang(call: F.CallbackQuery):
    await call.message.edit_text(_("choose_lang"), reply_markup=new_lang_kb())


@router.callback_query(F.data == "new_timezone_kb")
async def new_timezone(call: F.CallbackQuery):
    await call.message.edit_text(_("choose_tz"), reply_markup=timezone_simple_keyboard(False))


@router.callback_query(F.data.startswith("set_new_lang_"))
async def set_new_lang(call: F.CallbackQuery, bot: Bot, session: AsyncSession, state: FSMContext):
    await call.message.edit_text(_("WAIT_MESSAGE"))
    tmp_msg = await bot.send_message(call.from_user.id, _("WAIT_MESSAGE"))
    lang = call.data.split("_")[-1]
    if lang == "add":
        await call.answer(_("pls_do_registration"), show_alert=True)
        return

    await state.update_data(lang=lang)

    if not await dbuc.user_exists(session, call.from_user.id):

        await dbuc.add_user(session, call.from_user.id, call.from_user.first_name, lang)
    else:

        await dbuc.set_language_code(session, call.from_user.id, lang)

    data = await state.get_data()
    await call.answer(_("lang_changed_to") + _("lang"))

    await bot.delete_messages(call.from_user.id, [tmp_msg.message_id, call.message.message_id])
    await bot.send_message(
        call.from_user.id,
        text=_('start_menu').format(lang=lang, tz=data.get('tz')),
        reply_markup=start_menu_kb())

    logger.info(f"New user {call.from_user.id} changed language to {lang}")


# TODO SPLIT TO GUIDE ROUTER

@router.callback_query(F.data.startswith("set_new_timezone_"))
async def set_new_lang(call: F.CallbackQuery, state: FSMContext):
    tz = call.data.split("_")[-1]

    try:
        pytz.timezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        await call.answer(_("ERROR_MESSAGE"), show_alert=True)
        await call.message.edit_text(_("please_ch_button"), reply_markup=start_menu_kb())
        logger.error(f"User {call.from_user.id} tried to set invalid timezone: {tz}")
        return

    await state.update_data(tz=tz)
    data = await state.get_data()
    await call.answer(_("tz_changed_answer").format(tz))
    await call.message.edit_text(text=_('start_menu').format(
        lang=data.get('lang'), tz=tz),
        reply_markup=start_menu_kb())
    logger.info(f"New user {call.from_user.id} changed tz to {tz}")


@router.callback_query(F.data == "guide_page_1")
async def guide_pg_1(call: F.CallbackQuery, bot: Bot):
    await call.message.delete()
    try:
        await bot.send_animation(call.from_user.id,
                                 animation="CgACAgIAAxkBAAIOHmXgwmym4477hQdjneMJ0q_7GuFxAAJIBQACKeEJSgSS9v79LudONAQ",
                                 caption=_("guide_page_1"), reply_markup=guide_start_kb(1))
    except TelegramBadRequest as e:
        logger.error(f"Error while sending animation: {e}")
        await bot.send_message(call.from_user.id, _("ERROR_MESSAGE"))
        return
    logger.info(f"User {call.from_user.id} switched to guide page 1")


@router.callback_query(F.data == "guide_page_2")
async def guide_pg_2(call: F.CallbackQuery, bot: Bot):
    await call.message.delete()
    await bot.send_animation(call.from_user.id,
                             animation="CgACAgIAAxkBAAIOIGXgwm7gUBseAfejgmnR29UB1AwpAAIHQAACpeZxSuw82reLdn6DNAQ",
                             caption=_("guide_page_2"), reply_markup=guide_start_kb(2))
    logger.info(f"User {call.from_user.id} switched to guide page 2")


@router.callback_query(F.data == "guide_page_3")
async def guide_pg_3(call: F.CallbackQuery, bot: Bot):
    await call.message.delete()
    await bot.send_animation(call.from_user.id,
                             animation="CgACAgIAAxkBAAIOHGXgwlwN11Qmbsd5hCOpy4KU9CiOAAIIFwAC_F8BSt4eEtjPnDroNAQ",
                             caption=_("guide_page_3"), reply_markup=guide_start_kb(3))
    logger.info(f"User {call.from_user.id} switched to guide page 3")


@router.callback_query(F.data == "guide_complete")
async def guide_complete(call: F.CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.delete()
    await call.answer(_("thank_you_guide"))
    if await state.get_state():
        data = await state.get_data()
        await bot.send_message(call.from_user.id,
                               text=_("start_menu").format(lang=data.get('lang'), tz=data.get('tz')),
                               reply_markup=start_menu_kb())
    else:
        await bot.send_message(call.from_user.id, text=_("please_ch_button"), reply_markup=main_kb())
    logger.info(f"New user {call.from_user.id} completed guide")


@router.callback_query(F.data == "reg_complete")
async def complete_user_reg(call: F.CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext):
    id = await bot.send_message(call.from_user.id, _("WAIT_MESSAGE"))
    data = await state.get_data()

    if await dbuc.user_exists(session, call.from_user.id):

        await dbuc.set_user_active(session, call.from_user.id, True)
        await dbuc.set_language_code(session, call.from_user.id, data.get('lang'))
        await dbuc.set_timezone(session, call.from_user.id, data.get('tz'))

    else:
        await dbuc.add_user(session, call.from_user.id, call.from_user.first_name,
                            data.get('lang'), data.get('tz'), True)

    await bot.delete_messages(call.from_user.id, [id.message_id, call.message.message_id])

    if data.get('notif_id'):
        notif = await get_notif(session, data.get('notif_id'))
        await add_notif(session, notif.date, call.from_user.id, notif.text)
        await bot.send_message(call.from_user.id, _("deeplink_notif_added"))

    await state.clear()

    await call.answer(_("reg_completed"))

    await bot.send_message(call.from_user.id, _("please_ch_button"), reply_markup=main_kb())

    logger.info(f"User {call.from_user.id} completed registration")
