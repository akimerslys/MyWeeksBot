from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Column
import datetime
from bot.database.models.base import Base, created_at, updated_at, int_pk


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    user_id = Column(BigInteger, primary_key=True, unique=True)
    first_name: Mapped[str]
    language_code: Mapped[str | None]
    timezone: Mapped[str | None] = mapped_column(default="UTC")
    active_notifs: Mapped[int] = mapped_column(default=0)
    is_premium: Mapped[bool] = mapped_column(default=False)
    premium_until: Mapped[datetime.datetime | None] = mapped_column(default=None)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

