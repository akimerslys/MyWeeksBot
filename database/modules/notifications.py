from sqlalchemy import Integer, Column, sql, String, Boolean, SmallInteger, BigInteger

from database.database import TimedBaseModel, db


class Notification(TimedBaseModel):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(db.DateTime(True))
    userid = Column(BigInteger)
    text = Column(String(20))
    repeat = Column(Boolean, default=False)
    week_repeat = Column(Boolean, default=False)
    next_date = Column(db.DateTime(True), nullable=True)
    query: sql.select
