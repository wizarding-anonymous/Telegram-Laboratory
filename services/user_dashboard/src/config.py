# user_dashboard/src/config.py
import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Конфигурационные параметры для микросервиса User Dashboard.
    """
    # Основные настройки приложения
    APP_NAME: str = "User Dashboard Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Настройки базы данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/db_user_dashboard")
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"

    # Настройки интеграции с Auth Service через API Gateway
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://api-gateway/auth")
    AUTH_SERVICE_TIMEOUT: int = int(os.getenv("AUTH_SERVICE_TIMEOUT", 10))

    # Настройки API Gateway
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://api-gateway")
    GATEWAY_TIMEOUT: int = int(os.getenv("GATEWAY_TIMEOUT", 10))

    # Логирование
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Настройки CORS
    ALLOW_ORIGINS: list = os.getenv("ALLOW_ORIGINS", "*").split(",")
    ALLOW_METHODS: list = os.getenv("ALLOW_METHODS", "*").split(",")
    ALLOW_HEADERS: list = os.getenv("ALLOW_HEADERS", "*").split(",")

    # Настройки Redis для кэширования
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_TIMEOUT: int = int(os.getenv("REDIS_TIMEOUT", 5))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Экземпляр конфигурации
settings = Settings()
