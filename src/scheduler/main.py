import time
from email.message import Message
from typing import TYPE_CHECKING

from aiogram.types import BufferedInputFile, FSInputFile
from sqlalchemy import select, func

from src.bot.utils.csv_converter import convert_to_csv
from src.database.models import UserModel, NotifModel, ScheduleModel

if TYPE_CHECKING:
    pass

import asyncio

from datetime import datetime
from aiogram import Bot
from arq import cron
from loguru import logger
from src.core.config import settings
from src.database.engine import sessionmaker
from src.image_generator.images import generate_user_schedule_day
from src.bot.services.users import get_schedule_users_by_time
from src.bot.services.schedule import get_user_schedule_by_day
from src.bot.services.notifs import get_notifs_by_date, update_notif_auto


async def startup(ctx):
    ctx["bot"] = Bot(token=settings.TOKEN)
    async with sessionmaker() as session:
        ctx["session"] = session
    ctx["lock"] = asyncio.Lock()


async def shutdown(ctx):
    await ctx["bot"].session.close()


async def send_message(ctx, chat_id, text):
    await ctx["bot"].send_message(chat_id, text)


async def send_notif(ctx, chat_id, text):
    await ctx["bot"].send_message(chat_id, f"🔔 {text}")
    logger.success("SENT NOTIF TO USER {chat_id}")


async def fetch_and_send_notifications(ctx):     # Assuming shared engine access
    start = time.time()
    session = ctx["session"]
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    dtime = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    logger.info(f"doint stuff {dtime}")
    notifications = await get_notifs_by_date(session, dtime)
    for notification in notifications:
        await send_notif(ctx, notification.user_id, notification.text)
        await update_notif_auto(session, notification.id)
    logger.info(f"sent notifications in {round(time.time() - start, 4)} seconds")


async def generate_and_send_schedule(ctx):
    logger.info("generating and sending schedules")
    start = time.time()
    session = ctx["session"]
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    dtime = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    users_list = await get_schedule_users_by_time(session, dtime.time())
    for user in users_list:
        schedule_list = await get_user_schedule_by_day(session, user.user_id, days_of_week[dtime.weekday()])
        async with ctx["lock"]:
            image_bytes = await generate_user_schedule_day(schedule_list, dtime, user.timezone)
            await ctx["bot"].send_photo(user.user_id,
                                 BufferedInputFile(image_bytes.getvalue(),
                                                   filename=f"schedule_{user.user_id}.jpeg"))
    logger.info(f"generated and sent schedules in {round(time.time() - start, 4)} seconds")


async def backup_tables(ctx) -> None:

    types = {
        "users": UserModel,
        "notifs": NotifModel,
        "schedule": ScheduleModel
    }

    start_time = time.time()

    logger.warning(f"everyday backup started")
    session = ctx["session"]

    for name, model in types.items():
        logger.warning(f"exporting {name}")

        objects = await session.execute(select(model))

        objects = objects.scalars().all()

        document = await convert_to_csv(objects, name)

        count = await session.execute(select(func.count(model.id)))

        count_int = int(count.scalar())

        await ctx["bot"].send_document(settings.BACKUP_CHAT_ID, document=document, caption=f"total {name}: {count_int}")

        logger.success(f"{name} exported")

    time_end = round(time.time() - start_time, 4)
    logger.success(f"exported all in {time_end} seconds")


"""async def send_logs(ctx):
    await ctx["bot"].send_document(settings.LOGS_CHAT_ID, FSInputFile("logs/myweeksbot.log", filename="myweeksbot.log"))
    logger.success("sent logs")"""


class WorkerSettings:
    logger.info('initializing scheduler')
    redis_settings = settings.redis_pool
    on_startup = startup
    on_shutdown = shutdown
    functions = [send_message, fetch_and_send_notifications, generate_and_send_schedule, backup_tables]
    cron_jobs = [
        cron(fetch_and_send_notifications, minute={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}, second=1),
        cron(generate_and_send_schedule, minute={0, 15, 30, 45}, second=55),
        cron(backup_tables, hour=0, minute=1, second=0)
    ]

