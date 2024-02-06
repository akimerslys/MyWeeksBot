from sqlalchemy import Integer, Column, sql, String, Boolean

from database.database import TimedBaseModel, db


class User(TimedBaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, unique=True)
    name = Column(String(20))
    language = Column(String(5))
    timezone = Column(String(32))
    is_premium = Column(Boolean, default=False)
    premium_until = Column(db.DateTime(True), nullable=True)
    query: sql.select
