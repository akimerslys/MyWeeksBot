from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    TOKEN: str
    ADMINS_ID: list


class DBSettings(EnvBaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    POSTGRES_URI: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


class Settings(BotSettings, DBSettings):
    DEBUG: bool = False


settings = Settings()

