# services\data_storage_service\src\config.py
from typing import List, Optional
import string
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, validator

class Settings(BaseSettings):
    SERVICE_NAME: str = Field("DataStorageService", env="SERVICE_NAME")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(True, env="DEBUG")
    APP_PORT: int = Field(8001, env="APP_PORT")
    APP_HOST: str = Field("0.0.0.0", env="APP_HOST")
    API_VERSION: str = Field("v1", env="API_VERSION")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE_PATH: str = Field("./logs/data_storage_service.log", env="LOG_FILE_PATH")
    WORKERS_COUNT: int = Field(1, env="WORKERS_COUNT")
    DATABASE_USER: str = Field("bot_user", env="DATABASE_USER")
    DATABASE_PASSWORD: str = Field("bot_password", env="DATABASE_PASSWORD")
    DATABASE_HOST: str = Field("localhost", env="DATABASE_HOST")
    DATABASE_PORT: int = Field(5432, env="DATABASE_PORT")
    DATABASE_NAME: str = Field("data_storage_service", env="DATABASE_NAME")
    DATABASE_URL: PostgresDsn = Field(
        "postgresql+asyncpg://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}",
        env="DATABASE_URL",
    )
    BOT_DATABASE_PREFIX: str = Field("db_bot_", env="BOT_DATABASE_PREFIX")
    ALEMBIC_URL: PostgresDsn = Field(
        "postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}",
        env="ALEMBIC_URL",
    )
    ALEMBIC_SCRIPT_LOCATION: str = Field("src/db/migrations", env="ALEMBIC_SCRIPT_LOCATION")
    DB_CONNECTION_TIMEOUT: int = Field(30, env="DB_CONNECTION_TIMEOUT")
    DB_POOL_SIZE: int = Field(20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(10, env="DB_MAX_OVERFLOW")
    TEST_DATABASE_URL: PostgresDsn = Field(
        "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db",
        env="TEST_DATABASE_URL"
    )
    AUTH_SERVICE_URL: str = Field("http://localhost:8001", env="AUTH_SERVICE_URL")
    API_GATEWAY_URL: str = Field("http://localhost:8000", env="API_GATEWAY_URL")
    SERVICE_DISCOVERY_URL: str = Field("http://localhost:8500", env="SERVICE_DISCOVERY_URL")
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    SECRET_KEY: str = Field("your_strong_secret_key_here_at_least_32_chars", env="SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ENCRYPTION_KEY: str = Field("your_strong_encryption_key_here_32_chars", env="ENCRYPTION_KEY")
    CORS_ALLOWED_ORIGINS: str = Field(
        "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000",
        env="CORS_ALLOWED_ORIGINS"
    )
    ALLOWED_ORIGINS: str = Field(
        "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000",
        env="ALLOWED_ORIGINS"
    )
    PROMETHEUS_METRICS_ENABLED: bool = Field(True, env="PROMETHEUS_METRICS_ENABLED")
    PROMETHEUS_METRICS_PORT: int = Field(8003, env="PROMETHEUS_METRICS_PORT")
    MAX_BOTS_PER_USER: int = Field(10, env="MAX_BOTS_PER_USER")
    MAX_REQUESTS_PER_MINUTE: int = Field(100, env="MAX_REQUESTS_PER_MINUTE")
    MAX_DATABASE_SIZE_MB: int = Field(1000, env="MAX_DATABASE_SIZE_MB")
    HTTP_TIMEOUT: int = Field(30, env="HTTP_TIMEOUT")
    BACKUP_ENABLED: bool = Field(False, env="BACKUP_ENABLED")
    BACKUP_PATH: str = Field("/backups", env="BACKUP_PATH")
    BACKUP_RETENTION_DAYS: int = Field(30, env="BACKUP_RETENTION_DAYS")
    TELEGRAM_BOT_TOKEN: str = Field("your_telegram_bot_token_here", env="TELEGRAM_BOT_TOKEN")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    @validator("DATABASE_URL", pre=True)
    def assemble_database_url(cls, v, values):
        if isinstance(v, str) and "${" in v:
            template = string.Template(v)
            return template.safe_substitute(values)
        return v

    @validator("ALEMBIC_URL", pre=True)
    def assemble_alembic_url(cls, v, values):
        if isinstance(v, str) and "${" in v:
            template = string.Template(v)
            return template.safe_substitute(values)
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_origins_list_cors(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

settings = Settings()

if __name__ == "__main__":
    print(settings.SERVICE_NAME)
    print(settings.ENVIRONMENT)
    print(settings.DEBUG)
    print(settings.APP_PORT)
    print(settings.DATABASE_URL)
    print(settings.ALEMBIC_URL)
    print(settings.API_VERSION)
    print(settings.allowed_origins_list)
    print(settings.allowed_origins_list_cors)
