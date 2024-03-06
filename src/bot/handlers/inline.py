from aiogram import Router, F, html
from aiogram.types import InlineQuery, InlineQueryResultArticle
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.services.notifs import get_user_notifs_sorted
from src.bot.services.users import user_logged, get_timezone
from src.bot.keyboards.inline.inline import inline_add

from datetime import datetime

router = Router(name="inline")


@router.inline_query(F.query == "notifs")
async def show_user_notifs(query: InlineQuery, session: AsyncSession):
    if not await user_logged(session, query.from_user.id):
        await query.answer(
            results=[],
            is_personal=True,
            switch_pm_text=_("sign_in_inline"),
            switch_pm_parameter="inline_new"
        )
        return
    logger.info("im here")

    user_notifs = await get_user_notifs_sorted(session, query.from_user.id)
    results = []
    tz = await get_timezone(session, query.from_user.id)

    for notif in user_notifs:
        payload = f"{notif.id}_{tz}"
        logger.debug("payload: " + payload)
        link = await create_start_link(bot, payload, encode=True)
        logger.info("created link: " + link + "    id: " + notif.id)
        date_str = html.bold(html.quote(datetime(notif.date).strftime("%d/%m/%Y %H:%M")))
        text_str = html.quote(_("{text}\n").format(text=notif.text))
        results.append(InlineQueryResultArticle(
            id=notif.id,            # may cause problems, so idk
            title=date_str,
            description=text_str + _("Share"),
            input_message_content=InputTextMessageContent(
                message_text=_("{date_str}\n{text_str}")
            ),
            parse_mode="HTML",
            replymarkup=inline_add(link)
        ))
        
    await query.aswer(results, is_personal=True)

@router.inline_query()
async def show_inline_menu(query: InlineQuery, session: AsyncSession):
    if not await user_logged(session, query.from_user.id):
        await query.answer(
            results=[],
            is_personal=True,
            switch_pm_text=_("You are not signed! Tap to sign in to @myweeksbot"),
            switch_pm_parameter = "inline_new"
        )
        return




