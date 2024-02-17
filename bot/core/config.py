from __future__ import annotations
from pathlib import Path
from typing import ClassVar

from arq.connections import RedisSettings
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    TOKEN: str
    RATE_LIMIT: float
    ADMINS_ID: list
    DEBUG: bool = True


class DBSettings(EnvBaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: str
    DB_NAME: str

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}{''if not self.DB_PASS else ':' + self.DB_PASS}" \
               f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class KeyGenSettings(EnvBaseSettings):
    TYPE: str
    CAPITAL: str
    EXTRAS: list


class CacheSettings(EnvBaseSettings):

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASS: str | None

    DEFAULT_TTL: int = 10

    @property
    def redis_pool(self) -> RedisSettings:
        return RedisSettings(host=self.REDIS_HOST, port=self.REDIS_PORT, password=self.REDIS_PASS)

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.REDIS_PASS + '@' if self.REDIS_PASS else ''}{self.REDIS_HOST}:{self.REDIS_PORT}"


class UserSettings(EnvBaseSettings):
    MAX_NOTIFS: int = 5
    MAX_NOTIFS_PREMIUM: int = 10


class Settings(BotSettings, DBSettings, KeyGenSettings, CacheSettings, UserSettings):
    PATH_DIR: Path = Path(__file__).absolute().parent.parent.parent
    BOT_DIR: Path = Path(__file__).absolute().parent.parent
    LOCALES_DIR: str = f"{BOT_DIR}/locales"
    I18N_DOMAIN: str = "messages"


settings = Settings()
