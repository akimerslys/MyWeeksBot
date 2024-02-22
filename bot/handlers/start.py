from aiogram import Router, Bot, F
from aiogram.types import Message, InputMediaAnimation
from aiogram.types.input_file import FSInputFile
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline.guide import guide_start_kb
from bot.keyboards.inline.menu import language_kb, main_kb
from bot.services.users import user_exists, set_language_code, add_user

router = Router(name="start")


@router.message(CommandStart())
async def start_message(message: Message, bot: Bot, session: AsyncSession):
    if not await user_exists(session, message.from_user.id):
        await bot.send_message(
            message.from_user.id,
            _("start msg + choose_language"),
            reply_markup=language_kb(True)
        )
    else:
        await bot.send_message(
            message.from_user.id,
            _("pls_choose_option"),
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


@router.callback_query(F.data.startswith("set_new_lang_"))
async def set_new_lang(call: F.CallbackQuery, session: AsyncSession):
    lang = call.data.split("_")[-1]
    await call.answer(_("lang_changed_to{}").format(lang))
    await add_user(session, call.from_user.id, lang)
    await call.message.edit_text(_("Please choose btn bellow"), reply_markup=main_kb())
    logger.info(f"New user {call.from_user.id} changed language to {lang}")