import os
import time
from typing import TYPE_CHECKING
import ujson

import asyncio
from aiogram.types import BufferedInputFile, FSInputFile
from sqlalchemy import select, func

from src.bot.utils.csv_converter import convert_to_csv
from src.database.engine import sessionmaker
from src.database.models import UserModel, NotifModel, ScheduleModel

if TYPE_CHECKING:
    pass

from datetime import datetime
from aiogram import Bot
from arq import cron
from hltv_async_api import Hltv

from loguru import logger
from src.core.config import settings
from src.core.redis_loader import redis_client
from src.image_generator.images import generate_user_schedule_day
from src.database.services.users import get_schedule_users_by_time
from src.database.services.schedule import get_user_schedule_by_day
from src.database.services.notifs import get_notifs_by_date, update_notif_auto


async def startup(ctx):
    ctx["bot"] = Bot(token=settings.TOKEN)
    ctx["lock"] = asyncio.Lock()
    async with sessionmaker() as session:
        ctx["session"] = session
    ctx["hltv"] = Hltv(max_delay=5, use_proxy=True, proxy_list=[settings.PROXY_MAIN, ''], true_session=True, debug=True)
    ctx["redis"] = redis_client
    logger.success(f"Scheduler started. UTC time {datetime.utcnow()}")


async def shutdown(ctx):
    await ctx["bot"].session.close()
    await ctx["session"].close()
    await ctx["hltv"].close_session()
    await ctx["redis"].close()
    logger.success(f"Scheduler stopped. UTC time {datetime.utcnow()}")

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


async def send_logs(ctx) -> None:
    logger.info(f"everyday log backup started")
    log_dir = os.path.join(settings.LOGS_DIR, "myweeks.log")
    document = FSInputFile(path=log_dir, filename="myweeks.log")
    await ctx["bot"].send_document(settings.LOGS_CHAT_ID,
                                   document=document,
                                   caption=f"{datetime.date(datetime.now())}")


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


async def parse_matches(ctx):
    logger.info("parsing matches")
    hltv = ctx["hltv"]
    redis = ctx["redis"]
    matches = await hltv.get_upcoming_matches(1, 1)
    if matches:
        await redis.set("matches", ujson.dumps(matches))
    else:
        logger.error("error parsing matches")


async def parse_events(ctx):
    logger.info("parsing events")
    hltv = ctx["hltv"]
    redis = ctx["redis"]
    events = await hltv.get_events()
    if events:
        await redis.set("events", ujson.dumps(events))
    else:
        logger.error("error parsing events")


async def parse_top_teams(ctx):
    logger.info("parsing top teams")
    hltv = ctx["hltv"]
    redis = ctx["redis"]
    top_teams = await hltv.get_top_teams(30)
    if top_teams:
        await redis.set("top_teams", ujson.dumps(top_teams))
    else:
        logger.error("error parsing top teams")


async def parse_top_players(ctx):
    logger.info("parsing top players")
    hltv = ctx["hltv"]
    redis = ctx["redis"]
    top_players = await hltv.get_best_players(30)
    if top_players:
        await redis.set("top_teams", ujson.dumps(top_players))
    else:
        logger.error("error parsing top players")


async def parse_last_news(ctx):
    logger.info("parsing last news")
    hltv = ctx["hltv"]
    redis = ctx["redis"]
    news = await hltv.get_last_news(only_today=True, max_reg_news=4)
    if news:
        await redis.set("news", ujson.dumps(news))
    else:
        logger.error("error parsing news")


class WorkerSettings:
    redis_settings = settings.redis_pool
    on_startup = startup
    on_shutdown = shutdown
    functions = [fetch_and_send_notifications,
                 generate_and_send_schedule,
                 backup_tables,
                 parse_matches,
                 parse_events,
                 parse_top_teams,
                 parse_top_players,
                 parse_last_news,
                 ]
    cron_jobs = [
        cron(fetch_and_send_notifications, minute={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}, second=1),
        cron(generate_and_send_schedule, minute={0, 15, 30, 45}, second=55),
        cron(backup_tables, hour=0, minute=1, second=0),
        cron(parse_matches, minute=59),
        cron(parse_events, hour=0, minute=0, second=0),
        cron(parse_top_teams, weekday=0, hour=18, minute=1, second=30),
        cron(parse_top_players, weekday=0, hour=20, minute=0, second=0),
        cron(parse_last_news, minute=55),
    ]


#if __name__ == "__main__":

    #run_worker(functions=worker_settings.functions, settings_cls=worker_settings.redis_settings,
    #          on_startup=worker_settings.on_startup, on_shutdown=worker_settings.on_shutdown, cron_jobs=worker_settings.cron_jobs)
