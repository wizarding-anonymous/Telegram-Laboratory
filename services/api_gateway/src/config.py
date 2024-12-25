# services\api_gateway\src\config.py
from typing import Dict, List, Optional, Union
from pathlib import Path
import secrets
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn, Field, validator


class Settings(BaseSettings):
    """
    Конфигурация API Gateway.
    Загружает настройки из переменных окружения и .env файла.
    """
    
    # Базовые настройки приложения
    APP_NAME: str = "api-gateway"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Настройки API
    API_V1_PREFIX: str = "/api/v1"
    OPENAPI_URL: str = "/openapi.json"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # Секреты и безопасность
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Настройки JWT
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # База данных PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "api_gateway"
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # Настройки пула соединений с БД
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO_LOG: bool = False
    
    # Redis настройки
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_URL: Optional[RedisDsn] = None
    
    # Настройки кэширования
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300  # 5 минут
    
    # Настройки rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Настройки балансировщика нагрузки
    LOAD_BALANCER_STRATEGY: str = "round_robin"
    HEALTH_CHECK_INTERVAL_SECONDS: int = 30
    HEALTH_CHECK_TIMEOUT_SECONDS: int = 5
    
    # Настройки прокси
    PROXY_TIMEOUT_SECONDS: int = 60
    PROXY_CONNECT_TIMEOUT_SECONDS: int = 5
    PROXY_MAX_RETRIES: int = 3
    PROXY_RETRY_DELAY_SECONDS: int = 1
    
    # Конфигурация микросервисов
    SERVICES: Dict[str, Dict[str, Union[str, int]]] = {
        "auth": {
            "host": "auth-service",
            "port": 8001,
            "health_check_url": "/health"
        },
        "users": {
            "host": "users-service",
            "port": 8002,
            "health_check_url": "/health"
        },
        "products": {
            "host": "products-service",
            "port": 8003,
            "health_check_url": "/health"
        },
        "orders": {
            "host": "orders-service",
            "port": 8004,
            "health_check_url": "/health"
        }
    }
    
    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: Optional[Path] = None
    
    # Настройки метрик и мониторинга
    METRICS_ENABLED: bool = True
    METRICS_HOST: str = "localhost"
    METRICS_PORT: int = 9090
    
    # Настройки трейсинга
    TRACING_ENABLED: bool = True
    JAEGER_HOST: str = "jaeger"
    JAEGER_PORT: int = 6831
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_url(cls, v: Optional[str], values: Dict[str, str]) -> str:
        """Сборка URL базы данных из компонентов."""
        if isinstance(v, str):
            return v
            
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB', '')}"
        )

    @validator("REDIS_URL", pre=True)
    def assemble_redis_url(cls, v: Optional[str], values: Dict[str, str]) -> str:
        """Сборка URL Redis из компонентов."""
        if isinstance(v, str):
            return v
            
        password_part = f":{values.get('REDIS_PASSWORD')}@" if values.get('REDIS_PASSWORD') else ""
        
        return f"redis://{password_part}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"

    def get_service_url(self, service_name: str) -> str:
        """
        Получение URL сервиса по его имени.

        Args:
            service_name: Имя сервиса

        Returns:
            str: URL сервиса
        
        Raises:
            KeyError: Если сервис не найден
        """
        if service_name not in self.SERVICES:
            raise KeyError(f"Service {service_name} not found in configuration")
            
        service_config = self.SERVICES[service_name]
        return f"http://{service_config['host']}:{service_config['port']}"

    def get_service_health_check_url(self, service_name: str) -> Optional[str]:
        """
        Получение URL для проверки здоровья сервиса.

        Args:
            service_name: Имя сервиса

        Returns:
            Optional[str]: URL для health check
        """
        if service_name not in self.SERVICES:
            return None
            
        return self.SERVICES[service_name].get("health_check_url")

    @property
    def is_development(self) -> bool:
        """Проверка режима разработки."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Проверка production режима."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """Проверка тестового режима."""
        return self.ENVIRONMENT.lower() == "testing"


@lru_cache()
def get_settings() -> Settings:
    """
    Получение настроек приложения.
    Использует кэширование для оптимизации.

    Returns:
        Settings: Объект с настройками
    """
    return Settings()


# Создание экземпляра настроек для использования в приложении
settings = get_settings()