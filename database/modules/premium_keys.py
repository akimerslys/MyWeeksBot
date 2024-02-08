from sqlalchemy import Integer, Column, sql, String, Boolean, SmallInteger, BigInteger

from database.database import TimedBaseModel, db


class PremiumKeys(TimedBaseModel):
    __tablename__ = 'premium_keys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(20))
    days = Column(SmallInteger, nullable=False)
    is_used = Column(Boolean, default=False)
    used_by = Column(BigInteger, nullable=True)
    query: sql.select
