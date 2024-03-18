from redis.asyncio import Redis, ConnectionPool
from loguru import logger

from src.core.config import settings

logger.info("loading redis")


redis_client = Redis(
    connection_pool=ConnectionPool.from_url(settings.redis_url)
)

logger.success("redis loaded")