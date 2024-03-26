"""
cd src/bot
pybabel extract --input-dirs=. -o locales/messages.pot --project=messages.
pybabel init -i locales/messages.pot -d locales -D messages -l en
pybabel init -i locales/messages.pot -d locales -D messages -l ru
pybabel init -i locales/messages.pot -d locales -D messages -l uk
pybabel compile -d locales -D messages --statistics
pybabel update -i locales/messages.pot -d locales --update
pybabel update -i locales/messages.pot -d locales -D messages
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

from aiogram.utils.i18n.middleware import I18nMiddleware

from src.database.services.users import get_language_code

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery, InlineQuery, Message
    from sqlalchemy.ext.asyncio import AsyncSession


class ACLMiddleware(I18nMiddleware):
    DEFAULT_LANGUAGE_CODE = "en"

    async def get_locale(self, event: Message | CallbackQuery | InlineQuery, data: dict[str, Any]) -> str:
        session: AsyncSession = data["session"]

        if not event.from_user:
            return self.DEFAULT_LANGUAGE_CODE

        user_id = event.from_user.id
        language_code: str | None = await get_language_code(session=session, user_id=user_id)

        return language_code or self.DEFAULT_LANGUAGE_CODE
