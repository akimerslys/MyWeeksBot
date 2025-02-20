from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Column, SmallInteger
from src.database.models.base import Base, created_at, int_pk, updated_at


class ScheduleModel(Base):
    __tablename__ = 'schedule'

    id: Mapped[int_pk]
    user_id = Column(BigInteger)
    day = Column(SmallInteger)
    time: Mapped[str]
    text: Mapped[str] = mapped_column(default=None, nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
