from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    TOKEN: str
    ADMINS_ID: list


#class DBSettings(EnvBaseSettings):
 #   DB_HOST: str


class Settings(BotSettings):
    DEBUG: bool = False


settings = Settings()

