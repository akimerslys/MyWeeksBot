import os
import time
import ujson

import asyncio
from aiogram.types import BufferedInputFile, FSInputFile
from sqlalchemy import select, func

#from src.scheduler.ignore import token2, send_gr
from src.bot.utils.csv_converter import convert_to_csv
from src.database.engine import sessionmaker
from src.database.models import UserModel, NotifModel, ScheduleModel

from datetime import datetime
from aiogram import Bot
from arq import cron
from hltv_async_api import Hltv

from loguru import logger
from src.core.config import settings
from src.core.redis_loader import redis_client
from src.image_generator.generator import generate_user_schedule_day
from src.database.services.users import get_schedule_users_by_time
from src.database.services.schedule import get_user_schedule_by_day
from src.database.services.notifs import get_notifs_by_date, update_notif_auto


async def startup(ctx):
    async with sessionmaker() as session:
        ctx["session"] = session
    proxy_path = f'{settings.PROJ_DIR}/{settings.PROXY}'
    async with Hltv(timeout=5, proxy_path=proxy_path, proxy_protocol='http', debug=True) as hltv:
        ctx["hltv"] = hltv

    ctx["bot"] = Bot(token=settings.TOKEN)
    #ctx["bot2"] = Bot(token=token2)
    ctx["lock"] = asyncio.Lock()
    ctx["redis"] = redis_client
    logger.success(f"Scheduler started. UTC time {datetime.utcnow()}")


async def shutdown(ctx):
    await ctx["session"].close()
    await ctx["redis"].close()
    logger.success(f"Scheduler stopped. UTC time {datetime.utcnow()}")


async def send_notif(ctx, chat_id, text):
    await ctx["bot"].send_message(chat_id, f"🔔 {text}")
    logger.success("SENT NOTIF TO USER {chat_id}")


async def fetch_and_send_notifications(ctx):     # Assuming shared engine access
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
    matches = await hltv.get_matches(1, 1)
    if matches:
        await redis.set("hltv:matches", ujson.dumps(matches))
        for match in matches:
            match_ = await hltv.get_match_info(match["id"], match['team1'], match['team2'], match['event'])
            await redis.set(f"hltv:matches:{match['id']}", ujson.dumps(match_))
    else:
        logger.error("error parsing matches")


async def parse_events(ctx):
    logger.info("parsing events")
    hltv = ctx["hltv"]
    redis = ctx["redis"]
    events = await hltv.get_events(future=False)
    if events:
        await redis.set("hltv:events", ujson.dumps(events))
        await redis.set("hltv:events:f", ujson.dumps(events[0]))
        for event in events[1:]:
            event_ = await hltv.get_event_info(event["id"], event["title"])
            await redis.set(f"hltv:events:{event['id']}", ujson.dumps(event_))

    major_events = await hltv.get_events(outgoing=False, future=True)
    if major_events:
        await redis.set("hltv:fevents", ujson.dumps(major_events))
        for event in major_events:
            event_ = await hltv.get_event_info(event["id"], event["title"])
            await redis.set(f"hltv:events:{event['id']}", ujson.dumps(event_))


async def parse_top_teams(ctx):
    logger.info("parsing top teams")
    hltv = ctx["hltv"]
    redis = ctx["redis"]
    top_teams = await hltv.get_top_teams(30)
    if top_teams:
        await redis.set("hltv:teams", ujson.dumps(top_teams))
        for team in top_teams:
            team_ = await hltv.get_team_info(team["id"], team['title'])
            await redis.set(f"hltv:teams:{team['id']}", ujson.dumps(team_))
    else:
        logger.error("error parsing top teams")


async def parse_top_players(ctx):
    logger.info("parsing top players")
    hltv = ctx["hltv"]
    redis = ctx["redis"]
    top_players = await hltv.get_best_players(30)
    if top_players:
        await redis.set("hltv:players", ujson.dumps(top_players))
        """for player in top_players:
            player = hltv.get_player_info(player["id"])
            redis.set(f"hltv:players:{player['id']}", ujson.dumps(player))"""
    else:
        logger.error("error parsing top players")


async def parse_last_news(ctx):
    logger.info("parsing last news")
    hltv = ctx["hltv"]
    redis = ctx["redis"]
    news = await hltv.get_last_news(only_today=True, max_reg_news=4)
    if news:
        await redis.set("hltv:news", ujson.dumps(news))
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
        #cron(parse_matches, minute=59),
        #cron(parse_events, hour=1, minute=1, second=15),
        #cron(parse_top_teams, weekday=0, hour=18, minute=1, second=30),
        #cron(parse_top_players, weekday=0, hour=20, minute=0, second=0),
        #cron(parse_last_news, minute=55),
    ]


#if __name__ == "__main__":

    #run_worker(functions=worker_settings.functions, settings_cls=worker_settings.redis_settings,
    #          on_startup=worker_settings.on_startup, on_shutdown=worker_settings.on_shutdown, cron_jobs=worker_settings.cron_jobs)
