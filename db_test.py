from arq import cron, create_pool
from src.core.config import settings
from hltv_async_api import Hltv
from src.core.config import settings
from src.core.redis_loader import redis_client
import ujson


async def startup(ctx):
    ctx["hltv"] = Hltv()
    ctx["redis"] = redis_client


async def shutdown(ctx):
    ctx["redis"].close()
    pass


async def parse_events(ctx):
    print('im here')
    hltv = ctx["hltv"]
    redis = ctx["redis"]

    events = await hltv.get_events(max_events=10)
    await redis.set('events', ujson.dumps(events))


class WorkerSettings:
    redis_settings = settings.redis_pool
    on_startup = startup
    on_shutdown = shutdown
    functions = [parse_events]
    cron_jobs = [
        cron(parse_events, second={0, 15, 30, 45})
    ]
