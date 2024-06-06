from aiogram import Router, F, Bot
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.i18n import gettext as _
from aiogram.utils.deep_linking import create_start_link

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.services.notifs import get_user_notifs_sorted
from src.database.services.schedule import count_user_schedule, get_user_schedule_day_time_text, \
    get_user_schedule_by_day
from src.database.services.users import user_logged, get_timezone
from src.bot.keyboards.inline.inline import inline_add, inline_schedule_add
from src.bot.utils.time_localizer import localize_datetime_to_timezone, localize_datetimenow_to_timezone, is_past, \
    is_future, round_minute
from src.bot.utils.img_to_url import imgbytes_to_url
from src.image_generator.generator import generate_user_schedule_week, generate_user_schedule_day

from datetime import datetime, timedelta

from loguru import logger

router = Router(name="inline")


async def invalid_date(query: InlineQuery) -> None:
    results = [InlineQueryResultArticle(
        id="0",
        title=_("wrong_date"),
        description=_("inline_create_notif_description"),
        input_message_content=InputTextMessageContent(
            message_text=_("inline_create_notif_description")
        ),
        thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
    )]

    await query.answer(results, is_personal=True, cache_time=5)
    return


async def invalid_text(query: InlineQuery) -> None:
    results = [InlineQueryResultArticle(
        id="0",
        title=_("Wrong text"),
        description=_("inline_wrong_text_description"),
        input_message_content=InputTextMessageContent(
            message_text=_("inline_wrong_text_description")
        ),
        thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
    )]

    await query.answer(results, is_personal=True, cache_time=5)
    return


async def send_sign_in(query: InlineQuery) -> None:
    await query.answer(
        results=[],
        is_personal=True,
        switch_pm_text=_("sign_in_inline"),
        switch_pm_parameter="inline_new",
        cache_time=5,
    )


async def process_date(bot, query, date, text, tz, today: bool = False):
    if is_past(date, tz) or is_future(date):
        await invalid_date(query)
        return

    date_str = date.strftime("%d/%m/%Y %H:%M") if not today else _('Today')

    tz_mod = tz.replace('/', '-')

    payload = f"_{date.strftime('%Y-%m-%d-%H-%M')}_{tz_mod}_{text}"
    logger.info(f"payload: {payload}")

    try:
        link = await create_start_link(bot, payload=payload)
    except Exception:
        logger.info(f"user {query.from_user.id} tried to create a inline notif with a wrong text")
        await invalid_text(query)
        return

    results = [InlineQueryResultArticle(
        id="0",
        title=date_str,
        description=text,
        input_message_content=InputTextMessageContent(
            message_text=_("inline_notif").format(date=date_str, tz=tz, text=text)
        ),
        thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
        parse_mode="HTML",
        reply_markup=inline_add(link)
    )]

    await query.answer(results, is_personal=True)


@router.inline_query(F.query.regexp(r"^\d{2}:\d{2}"))
async def create_short_notif(query: InlineQuery, bot: Bot, session: AsyncSession):
    if not await user_logged(session, query.from_user.id):
        await send_sign_in(query)
        return

    query_ = query.query.split(' ', 1)
    logger.warning(query_)
    text = ''
    if len(query_) > 1:
        text = query_[1]
    tz = await get_timezone(session, query.from_user.id)

    try:
        hour, minute = map(int, query_[0].split(':'))
        hour, minute = round_minute(hour, minute)
        logger.debug(f'{hour}:{minute}')
        now = localize_datetimenow_to_timezone(tz)
        date = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if date < now:
            date += timedelta(days=1)

    except ValueError:
        await invalid_date(query)
        return

    await process_date(bot, query, date, text, tz)


@router.inline_query(F.query.regexp(r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2} .+"))
async def create_notif(query: InlineQuery, bot: Bot, session: AsyncSession):
    if not await user_logged(session, query.from_user.id):
        await send_sign_in(query)
        return

    #25/12/2025 00:00 Merry Christmas!
    query_ = query.query.split(" ", 2)

    date_str = query_[0]
    logger.info(f"Inline date str: <{date_str}>")
    time_str = query_[1]
    logger.info(f"Inline time str: <{time_str}>")
    text = query_[2][:32]
    logger.info(f"Inline text str: <{text}>")

    try:
        date = datetime.strptime(date_str + time_str, "%d/%m/%Y%H:%M")
    except ValueError:
        await invalid_date(query)
        return

    tz = await get_timezone(session, query.from_user.id)
    await process_date(bot, query, date, text, tz)


@router.inline_query()
async def show_user_notifs(query: InlineQuery, bot: Bot, session: AsyncSession):
    if not await user_logged(session, query.from_user.id):
        await send_sign_in(query)
        return

    results = [InlineQueryResultArticle(
        id="0",
        title=_("inline_create_notif"),
        description=_("inline_create_notif_description"),
        input_message_content=InputTextMessageContent(
            message_text=_("inline_create_notif_description")
        ),
        thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
    )]

    tz = await get_timezone(session, query.from_user.id)

    if await count_user_schedule(session, query.from_user.id) != 0:
        # TODO URL CACHING ?
        user_schedule = await get_user_schedule_day_time_text(session, query.from_user.id)
        b = await generate_user_schedule_week(user_schedule)
        schedule_url = await imgbytes_to_url(b)

        payload = f'schedule_{query.from_user.id}'
        link = await create_start_link(bot, payload, encode=True)

        results.append(InlineQueryResultArticle(
            id="1",
            title=_("share_my_schedule"),
            description=_("schedule_description"),
            input_message_content=InputTextMessageContent(
                message_text=f"<a href='{schedule_url}'>🕔</a> {_('My Week Schedule')}\n\n"
                             f"{_('generated with @myweeksbot')}",
                disable_web_page_preview=False,
            ),
            thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
            reply_markup=inline_schedule_add(link),
        ))

        d = localize_datetimenow_to_timezone(tz).weekday()
        user_schedule = await get_user_schedule_by_day(session, query.from_user.id, d)
        b = await generate_user_schedule_day(user_schedule, d, tz=tz)
        schedule_url = await imgbytes_to_url(b)

        payload = f'schedule_{query.from_user.id}_{d}'
        link = await create_start_link(bot, payload, encode=True)

        results.append(InlineQueryResultArticle(
            id="2",
            title=_("share_today's_schedule"),
            description=_("schedule_description_today"),
            input_message_content=InputTextMessageContent(
                message_text=f"<a href='{schedule_url}'>🕔</a> {_('My Today Schedule')} \n"
                             f"{_('generated with @myweeksbot')}",
                disable_web_page_preview=False,
            ),
            thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
            reply_markup=inline_schedule_add(link),
        ))

    user_notifs = await get_user_notifs_sorted(session, query.from_user.id)

    for date, text, id in user_notifs:
        payload = f"notif_{id}_{tz}"

        link = await create_start_link(bot, payload, encode=True)
        date_str: str = (localize_datetime_to_timezone(date, tz)).strftime("%d/%m/%Y %H:%M")
        text_str: str = text

        results.append(InlineQueryResultArticle(
            id=str(id),  # may cause errors
            title=date_str,
            description=text_str,
            input_message_content=InputTextMessageContent(
                message_text=_("inline_notif").format(date=date_str, tz=tz, text=text_str)
            ),
            thumbnail_url="https://telegra.ph/file/6df6cb1ae5021970a8d69.jpg",
            reply_markup=inline_add(link)
        ))

    await query.answer(results, is_personal=True, cache_time=300)
