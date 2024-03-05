from redis.asyncio import Redis, ConnectionPool
from bot.core.config import settings

redis_client = Redis(
    connection_pool=ConnectionPool.from_url(settings.redis_url)
)
