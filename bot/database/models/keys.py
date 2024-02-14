from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Column
from bot.database.models.base import Base, created_at, int_pk, updated_at


class KeyModel(Base):
    __tablename__ = 'keys'

    id: Mapped[int_pk]
    key: Mapped[str] = mapped_column(primary_key=True)
    days: Mapped[int] = mapped_column(default=7, nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False)
    used_by = Column(BigInteger, default=None, nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

