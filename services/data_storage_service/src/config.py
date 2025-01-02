from pydantic_settings import BaseSettings, SettingsConfigDict
from decouple import config


class Settings(BaseSettings):
    """
    Settings for the Data Storage Service.
    """

    DATABASE_URL: str = config("DATABASE_URL")
    AUTH_SERVICE_URL: str = config("AUTH_SERVICE_URL")
    REDIS_URL: str = config("REDIS_URL", default="redis://localhost:6379/0")
    MODE: str = config("MODE", default="development")


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()