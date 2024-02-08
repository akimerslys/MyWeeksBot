from sqlalchemy import Integer, Column, sql, String, Boolean, SmallInteger, BigInteger

from database.database import TimedBaseModel, db


class Notification(TimedBaseModel):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(db.DateTime(True))
    userid = Column(BigInteger)
    text = Column(String(20))
    repeat_day = Column(Boolean, default=False, nullable=False)
    repeat_week = Column(Boolean, default=False, nullable=False)
    repeat_month = Column(Boolean, default=False, nullable=False)
    query: sql.select
