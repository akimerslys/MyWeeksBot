from datetime import datetime, tzinfo

from aiogram import Bot
from arq import cron
from loguru import logger
from bot.core.config import settings
from bot.database.engine import sessionmaker, engine
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.notifs import get_notifs_by_date, update_notif_auto


async def startup(ctx):
    ctx["bot"] = Bot(token=settings.TOKEN)


async def shutdown(ctx):
    await ctx["bot"].session.close()


async def send_message(ctx, chat_id, text):
    await ctx["bot"].send_message(chat_id, text)


async def fetch_and_send_notifications(ctx): # Assuming shared engine access
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    dtime = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    logger.info(f"doint stuff {dtime}")
    async with sessionmaker() as session:
        notifications = await get_notifs_by_date(session, dtime)
        for notification in notifications:
            await send_notif(ctx, notification.user_id, notification.text)
            await update_notif_auto(session, notification.id)


async def send_notif(ctx, chat_id, text):
    await ctx["bot"].send_message(chat_id, f"Hey!\n{text}")
    logger.success("SENT NOTIF TO USER {chat_id}")


class WorkerSettings:
    logger.info('initializing scheduler')
    redis_settings = settings.redis_pool
    on_startup = startup
    on_shutdown = shutdown
    functions = [send_message, fetch_and_send_notifications, ]
    cron_jobs = [
        cron(fetch_and_send_notifications, minute={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}, second=1)
    ]
