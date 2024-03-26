from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.i18n import gettext as _
from aiogram.utils.payload import decode_payload
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.keyboards.inline.guide import guide_start_kb, start_menu_kb, new_lang_kb
from src.bot.keyboards.inline.menu import main_kb
from src.bot.keyboards.inline.timezone import timezone_simple_keyboard
from src.database.services import users as dbuc
from src.database.services.notifs import add_notif, get_notif
from src.bot.utils.time_localizer import localize_datetime_to_timezone
from src.bot.utils.states import NewUser
from src.database.models import NotifModel
from src.bot.utils import error_manager as err

from datetime import datetime
from loguru import logger

router = Router(name="start")


# TODO OPTIMIZE !!! !! !! !! ! !! !! OR GAY
#  NOT GAY, EZ
# TRAAASH CODDEEEEEEEEEEEEEEEE REWRITE IT

async def send_menu(bot, id):
    await bot.send_message(
        id,
        _("please_ch_button"),
        reply_markup=main_kb()
    )


async def check_state(state: FSMContext):
    if await state.get_state() is not NewUser.new_user:
        await state.clear()
        await state.set_state(NewUser.new_user)
        await state.update_data(tz='UTC', lang='en')


async def send_start_menu(bot: Bot, state: FSMContext, id):
    data = await state.get_data()
    await bot.send_message(id,
                           _('start_menu').format(lang=data.get('lang'), tz=data.get('tz')),
                           reply_markup=start_menu_kb())


async def edit_start_menu(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(
        _('start_menu').format(lang=data.get('lang'), tz=data.get('tz')),
        reply_markup=start_menu_kb()
    )


async def new_user_menu(bot: Bot, state: FSMContext, id):
    await check_state(state)
    await send_start_menu(bot, state, id)


async def send_deeplink_notif(bot: Bot, state: FSMContext, session: AsyncSession, id, date: datetime, text, tz='UTC'):
    logger.debug(f"tz = {tz}, date = {date}")
    if not await dbuc.user_logged(session, id):
        await bot.send_message(id,
                               _("deeplink_got_notif").format(
                                   date=(localize_datetime_to_timezone(date, tz)).strftime("%d/%m/%Y %H:%M"),
                                   tz=tz,
                                   text=text))
        await check_state(state)
        await new_user_menu(bot, state, id)
    else:
        tz_usr = await dbuc.get_timezone(session, id)
        if tz != tz_usr:
            date = localize_datetime_to_timezone(date, tz_usr)
            tz = tz_usr

        await bot.send_message(id,
                               _("notif_deeplink_logged").format(
                                   date=date.strftime("%d/%m/%Y %H:%M"),
                                   tz=tz,
                                   text=text,
                               ))

        await add_notif(session, date, id, text)
        await send_menu(bot, id)


async def process_deeplink_date(bot, state, session, args, id):
    # _date_text_tz
    args_list = args.split("_", 3)
    #["", "date", "text", "tz"]
    logger.debug(f"got args list {args_list}")
    date_utc: datetime
    date_: datetime
    text: str = ''
    tz: str = 'UTC'

    if not await err.check_date(args_list[1], bot, id): return

    date_ = datetime.strptime(args_list[1], '%Y-%m-%d-%H-%M')

    # rounding minute to 0 or 5
    minute = (date_.minute + 2) // 5 * 5
    date_.replace(minute=minute)

    if len(args_list) > 2:          # checking for tz
        tz = args_list[2]
        if '-' in tz:
            tz = tz.replace('-', '/')
        logger.debug(f"tz: {tz}")
        if not await err.check_tz(tz, bot, id): return

        if len(args_list) > 3:      # checking for text
            text = args_list[3]
            if '_' in text:
                text = text.replace('_', ' ')

    logger.debug(date_)
    if not await err.check_date_ranges(date_, bot, id, tz): return

    await send_deeplink_notif(bot, state, session, id, date_, text, tz)
    logger.debug(f"deeplink sended for {id}")
    await state.update_data(notif_date=date_.timestamp(), notif_text=text)
    return


async def process_deeplink_shared(bot, state, session, args, id):
    try:
        payload = decode_payload(args)
    except ValueError:
        await bot.send_message(id, "Invalid link")
        return

    logger.debug(f"got payload {payload}")
    notif_args: list = payload.split("_", 2)
    logger.debug(notif_args)

    shared_notif: NotifModel | None
    notif_date: str

    shared_notif: bool | NotifModel = await err.check_notif(session, bot, id, int(notif_args[0]))
    if not shared_notif or not await err.check_date_ranges(shared_notif.date, bot, id): return

    await send_deeplink_notif(bot, state, session, id, shared_notif.date, shared_notif.text, notif_args[1])
    await state.update_data(notif_id=shared_notif.id)
    return


@router.message(CommandStart(deep_link=True))
async def start_message_deeplink(message: Message, bot: Bot, command: CommandObject, session: AsyncSession,
                                 state: FSMContext):
    id = message.from_user.id
    args = command.args
    logger.debug(f"got args {args}")

    if args == 'inline_new':
        await check_state(state)
        await send_start_menu(bot, state, id)
        return

    if args[0] == '_':
        await process_deeplink_date(bot, state, session, args, id)
    else:
        await process_deeplink_shared(bot, state, session, args, id)


@router.message(CommandStart(deep_link=False))
async def start_message(message: Message, bot: Bot, session: AsyncSession, state: FSMContext):
    if await dbuc.user_logged(session, message.from_user.id):
        await send_menu(bot, message.from_user.id)
    else:
        await check_state(state)
        await send_start_menu(bot, state, message.from_user.id)


"""@router.callback_query(F.data.startswith("set_new_lang_"))
async def set_new_lang(call: CallbackQuery, bot: Bot, session: AsyncSession):
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
async def guide_page(call: CallbackQuery):
    page = int(call.data.split("_")[-1])
    if page == 2:
        await call.message.edit_media(media=InputMediaAnimation(
            media="AgADCBcAAvxfAUo",
                                      reply_markup=main_kb()))
    await call.answer("meow!")
    logger.info(f"User {call.from_user.id} switched to guide page {page}")"""


@router.callback_query(F.data == "start_kb")
async def start_kb(call: CallbackQuery, state: FSMContext):
    await edit_start_menu(call, state)
    logger.info(f"User {call.from_user.id} switched to start menu")


@router.callback_query(F.data == "new_lang_kb")
async def new_lang(call: CallbackQuery):
    await call.message.edit_text(_("choose_lang"), reply_markup=new_lang_kb())


@router.callback_query(F.data == "new_timezone_kb")
async def new_timezone(call: CallbackQuery):
    await call.message.edit_text(_("choose_tz"), reply_markup=timezone_simple_keyboard(False))


@router.callback_query(F.data.startswith("set_new_lang_"))
async def set_new_lang(call: CallbackQuery, bot: Bot, session: AsyncSession, state: FSMContext):
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

    await bot.delete_messages(call.from_user.id, [tmp_msg.message_id])
    #await call.answer(_("Changes updated, Please Restart Menu"), show_alert=True)

    #await edit_start_menu(call, state)
    await call.message.edit_text("Please, Restart the menu (/start)")
    logger.info(f"New user {call.from_user.id} changed language to {lang}")


# TODO SPLIT TO GUIDE ROUTER

@router.callback_query(F.data.startswith("set_new_timezone_"))
async def set_new_lang(call: CallbackQuery, state: FSMContext):
    tz = call.data.split("_")[-1]

    await err.check_tz(tz, call, call.from_user.id)

    await state.update_data(tz=tz)

    await call.answer(_("tz_changed_answer").format(tz))

    await edit_start_menu(call, state)

    logger.info(f"New user {call.from_user.id} changed tz to {tz}")


@router.callback_query(F.data.startswith("guide_page_"))
async def guide_pg_1(call: CallbackQuery, bot: Bot):

    anims = [
        "",
        "CgACAgIAAxkBAAIOHmXgwmym4477hQdjneMJ0q_7GuFxAAJIBQACKeEJSgSS9v79LudONAQ",
        "CgACAgIAAxkBAAIOIGXgwm7gUBseAfejgmnR29UB1AwpAAIHQAACpeZxSuw82reLdn6DNAQ",
        "CgACAgIAAxkBAAIOHGXgwlwN11Qmbsd5hCOpy4KU9CiOAAIIFwAC_F8BSt4eEtjPnDroNAQ",
    ]

    page: str = (call.data.split("_")[-1])

    try:
        caption = "guide_page_" + page
        await bot.send_animation(call.from_user.id,
                                 animation=anims[int(page)],
                                 caption=_(caption),
                                 reply_markup=guide_start_kb(int(page)))
    except TelegramBadRequest as e:
        logger.error(f"Error while sending animation: {e}")
        await bot.send_message(call.from_user.id, _("ERROR_MESSAGE"))
        return

    logger.info(f"User {call.from_user.id} switched to guide page {page}")


@router.callback_query(F.data == "guide_complete")
async def guide_complete(call: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    await call.message.delete()
    await call.answer(_("thank_you_guide"))

    if await dbuc.get_user_active(session, call.from_user.id):
        await send_menu(bot, call.from_user.id)
    else:
        await send_start_menu(bot, state, call.from_user.id)

    logger.info(f"New user {call.from_user.id} completed guide")


@router.callback_query(F.data == "reg_complete")
async def complete_user_reg(call: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext):
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

    elif data.get('notif_date'):
        dt_ts = datetime.fromtimestamp(data.get('notif_date'))
        logger.debug(f"notif ts = {dt_ts}, notif date = {datetime.fromtimestamp(data.get('notif_date'))}")
        await add_notif(session, datetime.fromtimestamp(data.get('notif_date')), call.from_user.id,
                        data.get('notif_text'))
        await bot.send_message(call.from_user.id, _("deeplink_notif_added"))

    await state.clear()

    await call.answer(_("reg_completed"))

    await send_menu(bot, call.from_user.id)

    logger.info(f"User {call.from_user.id} completed registration")
