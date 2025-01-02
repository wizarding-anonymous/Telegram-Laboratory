from pydantic_settings import BaseSettings, SettingsConfigDict
from decouple import config


class Settings(BaseSettings):
    """
    Settings for the Data Storage Service.
    """

    DATABASE_URL: str = config("DATABASE_URL")
    SERVICE_DISCOVERY_URL: str = config("SERVICE_DISCOVERY_URL")
    AUTH_SERVICE_URL: str = config("AUTH_SERVICE_URL")
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()