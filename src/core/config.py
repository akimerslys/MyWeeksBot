from __future__ import annotations
from pathlib import Path
from typing import ClassVar

from arq.connections import RedisSettings
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import List


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    TOKEN: str
    RATE_LIMIT: float
    ADMINS_ID: list
    DEBUG: bool = True
    BACKUP_CHAT_ID: int
    LOGS_CHAT_ID: int
    MAX_NOTIFS: int = 5
    MAX_NOTIFS_PREMIUM: int = 10


class ProBotSettings(EnvBaseSettings):
    PROBOT_TOKEN: str
    USE_PROXY: bool = False
    if USE_PROXY:
        PROXY_MAIN: str
        PROXY_LIST: list


class WebhookSettings(EnvBaseSettings):
    WEBHOOK_BASE_URL: str
    WEBHOOK_SECRET: str
    WEBHOOK_HOST: str = "localhost"
    WEBHOOK_PORT: int

    @property
    def webhook_uri(self) -> str:
        return f"{self.WEBHOOK_BASE_URL}{self.WEBHOOK_PATH}"

    USE_WEBHOOK: bool = False

class DBSettings(EnvBaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: int = 5432
    DB_NAME: str

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}{':' + self.DB_PASS if self.DB_PASS else ''}" \
               f"@{self.DB_HOST}:{str(self.DB_PORT)}/{self.DB_NAME}"


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


class Settings(BotSettings, WebhookSettings, DBSettings, KeyGenSettings, CacheSettings, ProBotSettings):
    PROJ_DIR: Path = Path(__file__).absolute().parent.parent.parent
    BOT_DIR: Path = Path(__file__).absolute().parent.parent / "bot"
    MEDIA_DIR: str = f"{PROJ_DIR}/media"
    FONTS_DIR: str = f"{PROJ_DIR}/fonts"
    LOCALES_DIR: str = f"{PROJ_DIR}/src/bot/locales"
    LOGS_DIR: str = f"{PROJ_DIR}/logs"

    PROBOT_DIR: Path = Path(__file__).absolute().parent.parent / "probot"
    I18N_DOMAIN: str = "messages"
    I18N_DOMAIN_PRO: str = "messages_pro"

    WEBHOOK_PATH: str = f"/bot/"


settings = Settings()
