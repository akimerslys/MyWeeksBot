from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Column, ARRAY, String
import datetime
from src.database.models.base import Base, created_at, updated_at, int_pk


class ProUserModel(Base):
    __tablename__ = "prousers"

    id: Mapped[int_pk]
    user_id = Column(BigInteger, primary_key=True, unique=True)
    first_name: Mapped[str]
    language_code: Mapped[str | None] = mapped_column(default='en')
    timezone: Mapped[str | None] = mapped_column(default="UTC")
    tier: Mapped[int] = mapped_column(default=1)
    tournaments = Column(ARRAY(String), default=[])
    is_premium: Mapped[bool] = mapped_column(default=False)
    premium_until: Mapped[datetime.datetime | None] = mapped_column(default=None, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=False)
    active: Mapped[bool] = mapped_column(default=False, nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

