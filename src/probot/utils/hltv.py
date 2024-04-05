from src.core.redis_loader import redis_client
from src.probot.loader import hltv
import ujson


async def get_hltv(type: str, update: bool = False):
    if not update:
        r = await redis_client.get(f"{type}")
        if r:
            return r

    if type == "matches":
        r = await hltv.get_matches()
    elif type == "events":
        r = await hltv.get_events()
    elif type == "news":
        r = await hltv.get_last_news()
    elif type == "results":
        r = await hltv.get_results()
    else:
        return None

