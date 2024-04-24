from src.core.redis_loader import redis_client
from src.probot.loader import hltv

from loguru import logger
import ujson


async def get_cache(key):
    data_ = await redis_client.get(key)
    if data_:
        return ujson.loads(data_)


async def get_hltv(type: str,
                   id: str | int = None,
                   title: str = None,
                   team1: str = None,
                   team2: str = None,
                   update: bool = False):
    key = f"hltv:{type}{':' + id if id else ''}"
    data = await redis_client.get(key)
    if not update:
        if data:
            data = ujson.loads(data)
            return data

    data = await hltv.get(type, id, title, team1, team2)
    if data:
        await redis_client.set(key, ujson.dumps(data))

    return data


async def get_fevents(id, title: str = None):

    key = f"hltv:events:f"
    data = await get_cache(key)
    if data:
        return data


async def get_event(id, title: str = None):

    key = f"hltv:events:{id}"
    data = await get_cache(key)
    if data:
        return data


async def get_event_matches(id, update: bool = False):
    key = f"hltv:events:matches:{id}"
    if not update:
        data = await get_cache(key)
        if data:
            logger.debug(f'got data of event {id}: {data}')
            return data

    data = await hltv.get_event_matches(id)
    logger.debug(f'got data of event {id}: {data}')
    await redis_client.set(key, ujson.dumps(data))
    return data

