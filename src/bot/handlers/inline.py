from aiogram import Router, F, Bot, html
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultCachedPhoto
from aiogram.utils.i18n import gettext as _
from aiogram.utils.deep_linking import create_start_link
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.services.notifs import get_user_notifs_sorted
from src.bot.services.schedule import count_user_schedule
from src.bot.services.users import user_logged, get_timezone
from src.bot.keyboards.inline.inline import inline_add

from datetime import datetime

from loguru import logger


router = Router(name="inline")


@router.inline_query()
async def show_user_notifs(query: InlineQuery, bot: Bot, session: AsyncSession):
    if not await user_logged(session, query.from_user.id):
        await query.answer(
            results=[],
            is_personal=True,
            switch_pm_text=_("sign_in_inline"),
            switch_pm_parameter="inline_new"
        )
        return

    results = []

    if await count_user_schedule(session, query.from_user.id) != 0:
        results.append(InlineQueryResultArticle(
            id="0",
            title=_("share_my_schedule"),
            description=_("schedule_description"),
            input_message_content=InputTextMessageContent(
                message_text=_("generated with @myweeksbot")
            ),
            thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
            parse_mode="HTML"
        ))

        results.append(InlineQueryResultArticle(
            id="1",
            title=_("share_my_today_schedule"),
            description=_("schedule_description"),
            input_message_content=InputTextMessageContent(
                message_text=_("generated with @myweeksbot")
            ),
            thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
            parse_mode="HTML"
        ))

    user_notifs = await get_user_notifs_sorted(session, query.from_user.id)

    tz = await get_timezone(session, query.from_user.id)

    for date, text, id in user_notifs:
        payload = f"{id}_{tz}"
        logger.debug("payload: " + payload)

        link = await create_start_link(bot, payload, encode=True)
        date_str = date.strftime("%d/%m/%Y %H:%M")
        text_str = text

        results.append(InlineQueryResultArticle(
            id=str(id),            # may cause problems, so idk
            title=date_str,
            description=text_str + _("Share"),
            input_message_content=InputTextMessageContent(
                message_text=_("🗓 <b>{date}</b> ({tz})\n\n💬 {text}").format(date=date_str, tz=tz, text=text_str)
            ),
            thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
            parse_mode="HTML",
            reply_markup=inline_add(link)
        ))

    await query.answer(results, is_personal=True)
