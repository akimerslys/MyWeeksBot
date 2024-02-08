from loguru import logger
from database.modules.premium_keys import PremiumKeys
from database.database import db
from core.config import settings

from datetime import datetime, timedelta

from key_generator.key_generator import generate

"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(20))
    valid_until = Column(db.DateTime(True), nullable=False)
    is_used = Column(Boolean, default=False)
    used_by = Column(BigInteger, nullable=True)
"""


async def add_key(days: int = 7):
    key = generate(4, '-', 4, 4,
                   type_of_value=settings.TYPE,
                   capital=settings.CAPITAL,
                   extras=settings.EXTRAS,
                   seed=None).get_key()
    logger.info('Generated new key')
    premium_key = PremiumKeys(
        key=key,
        days=days,
    )
    await premium_key.create()
    return key


async def select_all_keys() -> list[PremiumKeys]:
    return await PremiumKeys.query.gino.all()


async def select_key(key: str) -> PremiumKeys:
    return await PremiumKeys.query.where(PremiumKeys.key == key).gino.first()


async def is_key_used(key: str) -> bool:
    key = await select_key(key)
    return key.is_used


async def is_key(key: str) -> bool:
    return await select_key(key) is not None


async def get_days(key: str) -> int:
    key = await select_key(key)
    return key.days


async def use_key(key: str, userid: int):

    if not await is_key(key) or await is_key_used(key):
        return False
    key = await select_key(key)
    key.is_used = True
    key.used_by = userid
    key.update()
    logger.info(f'Key {key.id} was used by {userid}')
    return True
