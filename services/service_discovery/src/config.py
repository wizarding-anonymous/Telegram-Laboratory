import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuration settings for the Service Discovery microservice.
    """
    # General settings
    SERVICE_NAME: str = Field("ServiceDiscovery", env="SERVICE_NAME")
    ENVIRONMENT: str = Field(
        "development", env="ENVIRONMENT"
    )  # "development", "production", "testing"
    DEBUG: bool = Field(True, env="DEBUG")

    # Application settings
    APP_PORT: int = Field(8004, env="APP_PORT")

    # Database settings
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # Logging settings
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # JWT settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")

    # Auth Service settings
    AUTH_SERVICE_URL: str = Field(
        "http://localhost:8002", env="AUTH_SERVICE_URL"
    )

    # Redis settings
    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
   
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


if __name__ == "__main__":
    print("Service Name:", settings.SERVICE_NAME)
    print("Environment:", settings.ENVIRONMENT)
    print("Debug Mode:", settings.DEBUG)
    print("App Port:", settings.APP_PORT)
    print("Database URL:", settings.DATABASE_URL)
    print("Log Level:", settings.LOG_LEVEL)
    print("Secret Key:", settings.SECRET_KEY)
    print("Algorithm:", settings.ALGORITHM)
    print("Auth Service URL:", settings.AUTH_SERVICE_URL)
    print("Redis URL:", settings.REDIS_URL)