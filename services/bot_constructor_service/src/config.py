import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import string


class Settings(BaseSettings):
    """
    Configuration settings for the Bot Constructor microservice.
    """

    # General settings
    SERVICE_NAME: str = Field("BotConstructor", env="SERVICE_NAME")
    ENVIRONMENT: str = Field(
        "development", env="ENVIRONMENT"
    )  # "development", "production", "testing"
    DEBUG: bool = Field(True, env="DEBUG")  # Enable/Disable debug mode

    # Application settings
    APP_PORT: int = Field(8000, env="APP_PORT")  # Application port

    # Database settings
    DATABASE_USER: str = Field("bot_user", env="DATABASE_USER")
    DATABASE_PASSWORD: str = Field("bot_password", env="DATABASE_PASSWORD")
    DATABASE_HOST: str = Field("localhost", env="DATABASE_HOST")
    DATABASE_PORT: int = Field(5432, env="DATABASE_PORT")
    DATABASE_NAME: str = Field("bot_constructor", env="DATABASE_NAME")
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")  # Full database URL

    @property
    def full_database_url(self) -> str:
        """
        Dynamically generate the database URL if not provided explicitly.
        If DATABASE_URL contains placeholders, replace them with actual values.
        """
        # First, check if DATABASE_URL is already provided
        if self.DATABASE_URL:
            # Replace placeholders with environment variable values
            template = string.Template(self.DATABASE_URL)
            return template.substitute(
                DATABASE_USER=self.DATABASE_USER,
                DATABASE_PASSWORD=self.DATABASE_PASSWORD,
                DATABASE_HOST=self.DATABASE_HOST,
                DATABASE_PORT=self.DATABASE_PORT,
                DATABASE_NAME=self.DATABASE_NAME,
            )
        else:
            return (
                f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            )

    # Redis settings
    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    REDIS_TIMEOUT: int = Field(5, env="REDIS_TIMEOUT")

    # Auth Service settings
    AUTH_SERVICE_URL: str = Field("http://localhost:8002", env="AUTH_SERVICE_URL")
    AUTH_SERVICE_TIMEOUT: int = Field(10, env="AUTH_SERVICE_TIMEOUT")

    # Data Storage Service settings
    DATA_STORAGE_SERVICE_URL: str = Field(
        "http://localhost:8001", env="DATA_STORAGE_SERVICE_URL"
    )
    DATA_STORAGE_SERVICE_TIMEOUT: int = Field(10, env="DATA_STORAGE_SERVICE_TIMEOUT")

    # Logging Service settings
    LOGGING_SERVICE_URL: str = Field(
        "http://localhost:8003", env="LOGGING_SERVICE_URL"
    )
    LOGGING_SERVICE_TIMEOUT: int = Field(10, env="LOGGING_SERVICE_TIMEOUT")

    # Telegram API settings
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")

    # Telegram bot library
    TELEGRAM_BOT_LIBRARY: str = Field(
        "telegram_api", env="TELEGRAM_BOT_LIBRARY"
    )  # telegram_api, aiogram, telebot

    # Logging settings
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # API Version
    API_VERSION: str = Field("v1", env="API_VERSION")

    # Connection pool settings
    MAX_CONNECTIONS_COUNT: int = Field(10, env="MAX_CONNECTIONS_COUNT")
    MIN_CONNECTIONS_COUNT: int = Field(1, env="MIN_CONNECTIONS_COUNT")

    # CORS settings
    ALLOWED_ORIGINS: str = Field(
        "http://localhost,http://127.0.0.1", env="ALLOWED_ORIGINS"
    )
    ALLOWED_METHODS: list = Field(["*"], env="ALLOWED_METHODS")
    ALLOWED_HEADERS: list = Field(["*"], env="ALLOWED_HEADERS")

    class Config:
        env_file = ".env"  # Use a .env file to load environment variables
        env_file_encoding = "utf-8"


# Load configuration
settings = Settings()

# Example Usage
if __name__ == "__main__":
    print("Service Name:", settings.SERVICE_NAME)
    print("Environment:", settings.ENVIRONMENT)
    print("Debug Mode:", settings.DEBUG)
    print("App Port:", settings.APP_PORT)
    print("Database URL:", settings.full_database_url)
    print("Redis URL:", settings.REDIS_URL)
    print("Auth Service URL:", settings.AUTH_SERVICE_URL)
    print("Telegram Bot Token:", settings.TELEGRAM_BOT_TOKEN)
    print("Allowed Origins:", settings.ALLOWED_ORIGINS)
    print("Data Storage Service URL:", settings.DATA_STORAGE_SERVICE_URL)
    print("Logging Service URL:", settings.LOGGING_SERVICE_URL)
    print("Telegram bot library:", settings.TELEGRAM_BOT_LIBRARY)
    print("Allowed Methods:", settings.ALLOWED_METHODS)
    print("Allowed Headers:", settings.ALLOWED_HEADERS)