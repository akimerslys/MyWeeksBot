from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.probot.keyboards.inline.guide import start_menu_kb
from src.probot.keyboards.inline.menu import main_kb, lang_kb
from src.probot.keyboards.inline.timezone import timezone_simple_keyboard
from src.database.services import prousers as dbuc
from src.probot.utils.states import NewUser
from src.probot.utils import error_manager as err

from datetime import datetime
from loguru import logger


router = Router(name="start")


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


@router.message(CommandStart(deep_link=False))
async def start_message(message: Message, bot: Bot, session: AsyncSession, state: FSMContext):
    if await dbuc.user_logged(session, message.from_user.id):
        await send_menu(bot, message.from_user.id)
    else:
        await check_state(state)
        await send_start_menu(bot, state, message.from_user.id)


@router.callback_query(F.data == "start_kb")
async def start_kb(call: CallbackQuery, state: FSMContext):
    await edit_start_menu(call, state)


@router.callback_query(F.data == "lang_kb")
async def lang_kb_show(call: CallbackQuery, session: AsyncSession):
    new_user = await dbuc.get_user_active(session, call.from_user.id)
    await call.message.edit_text(_("choose_lang"), reply_markup=lang_kb(new_user))


@router.callback_query(F.data == "timezone_kb")
async def timezone_kb_show(call: CallbackQuery, session: AsyncSession):
    new_user = await dbuc.get_user_active(session, call.from_user.id)
    await call.message.edit_text(_("choose_tz"), reply_markup=timezone_simple_keyboard(new_user))


@router.callback_query(F.data.startswith("set_lang_"))
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
    await call.message.edit_text("Please, Restart the menu (/start)")
    logger.info(f"New user {call.from_user.id} changed language to {lang}")


@router.callback_query(F.data.startswith("set_tz_"))
async def set_new_lang(call: CallbackQuery, state: FSMContext):
    tz = call.data.split("_")[-1]

    await err.check_tz(tz, call, call.from_user.id)

    await state.update_data(tz=tz)

    await call.answer(_("tz_changed_answer").format(tz))

    await edit_start_menu(call, state)

    logger.info(f"New user {call.from_user.id} changed tz to {tz}")


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

    await state.clear()

    await call.answer(_("reg_completed"))

    await send_menu(bot, call.from_user.id)

    logger.info(f"User {call.from_user.id} completed registration")
