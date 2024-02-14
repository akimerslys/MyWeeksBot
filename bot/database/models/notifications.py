from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Column
from bot.database.models.base import Base, created_at, int_pk, updated_at, dtime


class NotifModel(Base):
    __tablename__ = 'notifs'

    id: Mapped[int_pk]
    date: Mapped[dtime]
    user_id = Column(BigInteger)
    text: Mapped[str]
    repeat_daily: Mapped[bool] = mapped_column(default=False)
    repeat_weekly: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
