from src.core.redis_loader import redis_client
from src.probot.loader import hltv

from loguru import logger
import ujson


async def get_hltv(type: str,
                   id: str | int = None,
                   title: str = None,
                   team1: str = None,
                   team2: str = None,
                   update: bool = False):
    key = f"hltv:{type}{':' + id if id else ''}"
    data = await redis_client.get(key)
    if data is None or update:
        data = await hltv.get(type, id, title, team1, team2)
        await redis_client.set(key, ujson.dumps(data))
    data = ujson.loads(data)
    return data

