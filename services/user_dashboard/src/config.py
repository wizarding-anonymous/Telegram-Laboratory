from pydantic_settings import BaseSettings, SettingsConfigDict
from decouple import config


class Settings(BaseSettings):
    """
    Settings for the User Dashboard service.
    """

    SERVICE_NAME: str = config("SERVICE_NAME")
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")
    DEBUG: bool = config("DEBUG", default=True, cast=bool)
    APP_PORT: int = config("APP_PORT", cast=int)
    DATABASE_URL: str = config("DATABASE_URL")
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")
    AUTH_SERVICE_URL: str = config("AUTH_SERVICE_URL")
    LOGGING_MONITORING_URL: str = config("LOGGING_MONITORING_URL")
    REDIS_URL: str = config("REDIS_URL", default="redis://localhost:6379/0")
    API_GATEWAY_URL: str = config("API_GATEWAY_URL")
    SESSION_SECRET_KEY: str = config("SESSION_SECRET_KEY")
    SESSION_EXPIRE_MINUTES: int = config("SESSION_EXPIRE_MINUTES", default=30, cast=int)


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()