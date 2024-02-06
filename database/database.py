from aiogram import Dispatcher

from gino import Gino
import sqlalchemy as sa
from sqlalchemy import BigInteger, String
from typing import List
from loguru import logger
from datetime import datetime
from core.config import settings

db = Gino()


class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"


"""class TestModel(BaseModel):
    __tablename__ = "test_table"

    id = db.Column(BigInteger, primary_key=True)
    name = db.Column(String(100), primary_key=True)

    _column_name_map = {
        "id": "id",
        "name": "name",
    }"""


class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = db.Column(db.DateTime(True), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(True),
        default=datetime.utcnow(),
        onupdate=datetime.utcnow(),
        server_default=db.func.now()
    )


async def on_startup(dispatcher: Dispatcher):
    logger.warning("Connecting to PostgreSQL")
    await db.set_bind(settings.database_url)

