from sqlalchemy import Integer, Column, sql, String

from database.database_load import TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, unique=True)
    name = Column(String(20))
    language = Column(String(5))
    Timezone = Column(String(32))

    query: sql.select
