from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    TOKEN: str
    RATE_LIMIT: float
    ADMINS_ID: list
    PATH_DIR: str


class DBSettings(EnvBaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: str
    DB_NAME: str

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}{''if not self.DB_PASSWORD else ':' + self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class KeyGenSettings(EnvBaseSettings):
    TYPE: str
    CAPITAL: str
    EXTRAS: list


class CacheSettings(EnvBaseSettings):
    USE_REDIS: bool = False

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASS: str | None = None

    DEFAULT_TTL: int = 10

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_PASS + '@' if self.REDIS_PASS else ''}{self.REDIS_HOST}:{self.REDIS_PORT}"


class Settings(BotSettings, DBSettings, KeyGenSettings, CacheSettings):
    DEBUG: bool = True


settings = Settings()
