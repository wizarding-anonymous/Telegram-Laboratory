# services/auth_service/src/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, model_validator
from typing import List, Optional, Dict, Set
import json
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"


class Permission(str, Enum):
    READ_USERS = "read:users"
    CREATE_USERS = "create:users"
    UPDATE_USERS = "update:users"
    DELETE_USERS = "delete:users"

    READ_ROLES = "read:roles"
    CREATE_ROLES = "create:roles"
    UPDATE_ROLES = "update:roles"
    DELETE_ROLES = "delete:roles"

    READ_BOTS = "read:bots"
    CREATE_BOTS = "create:bots"
    UPDATE_BOTS = "update:bots"
    DELETE_BOTS = "delete:bots"

    READ_SESSIONS = "read:sessions"
    DELETE_SESSIONS = "delete:sessions"

    MANAGE_SYSTEM = "manage:system"
    VIEW_METRICS = "view:metrics"


class Settings(BaseSettings):
    SERVICE_NAME: str = Field("AuthService", env="SERVICE_NAME")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(True, env="DEBUG")
    APP_PORT: int = Field(8002, env="APP_PORT")
    APP_HOST: str = Field("0.0.0.0", env="APP_HOST")
    API_VERSION: str = Field("v1", env="API_VERSION")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE_PATH: str = Field("./logs/auth_service.log", env="LOG_FILE_PATH")
    WORKERS_COUNT: int = Field(1, env="WORKERS_COUNT")

    DATABASE_USER: str = Field("bot_user", env="DATABASE_USER")
    DATABASE_PASSWORD: str = Field("bot_password", env="DATABASE_PASSWORD")
    DATABASE_HOST: str = Field("localhost", env="DATABASE_HOST")
    DATABASE_PORT: int = Field(5432, env="DATABASE_PORT")
    DATABASE_NAME: str = Field("auth_service_db", env="DATABASE_NAME")

    DATABASE_URL: PostgresDsn = Field(
        "postgresql+asyncpg://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}",
        env="DATABASE_URL"
    )

    ALEMBIC_URL: PostgresDsn = Field(
        "postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}",
        env="ALEMBIC_URL"
    )
    ALEMBIC_SCRIPT_LOCATION: str = Field("src/db/migrations", env="ALEMBIC_SCRIPT_LOCATION")

    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: str = Field("", env="REDIS_PASSWORD")
    REDIS_DB: int = Field(0, env="REDIS_DB")

    SECRET_KEY: str = Field("your_secret_for_jwt_here", env="SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(2880, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    RESET_TOKEN_EXPIRE_HOURS: int = Field(48, env="RESET_TOKEN_EXPIRE_HOURS")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(60, env="REFRESH_TOKEN_EXPIRE_DAYS")

    JWT_TOKEN_PREFIX: str = Field("Bearer", env="JWT_TOKEN_PREFIX")
    JWT_REFRESH_SECRET_KEY: Optional[str] = Field(None, env="JWT_REFRESH_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    MIN_PASSWORD_LENGTH: int = Field(8, env="MIN_PASSWORD_LENGTH")
    PASSWORD_HASH_ROUNDS: int = Field(12, env="PASSWORD_HASH_ROUNDS")

    RATE_LIMIT_ENABLED: bool = Field(True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(60, env="RATE_LIMIT_PERIOD")

    SESSION_CLEANUP_INTERVAL: int = Field(3600, env="SESSION_CLEANUP_INTERVAL")
    MAX_SESSIONS_PER_USER: int = Field(5, env="MAX_SESSIONS_PER_USER")

    ALLOWED_ORIGINS: Optional[List[str]] = Field(
        ["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )

    DEFAULT_ROLES: Dict[str, List[str]] = {
        UserRole.ADMIN: [perm.value for perm in Permission],
        UserRole.MANAGER: [
            Permission.READ_USERS.value,
            Permission.READ_ROLES.value,
            Permission.READ_BOTS.value,
            Permission.CREATE_BOTS.value,
            Permission.UPDATE_BOTS.value,
            Permission.DELETE_BOTS.value,
            Permission.READ_SESSIONS.value,
            Permission.DELETE_SESSIONS.value,
            Permission.VIEW_METRICS.value
        ],
        UserRole.USER: [
            Permission.READ_BOTS.value,
            Permission.CREATE_BOTS.value,
            Permission.UPDATE_BOTS.value,
            Permission.DELETE_BOTS.value,
            Permission.READ_SESSIONS.value,
            Permission.DELETE_SESSIONS.value
        ]
    }

    REQUIRED_PERMISSIONS: Dict[str, Set[str]] = {
        "roles:read": {Permission.READ_ROLES.value},
        "roles:create": {Permission.CREATE_ROLES.value},
        "roles:update": {Permission.UPDATE_ROLES.value},
        "roles:delete": {Permission.DELETE_ROLES.value},
        "users:read": {Permission.READ_USERS.value},
        "users:create": {Permission.CREATE_USERS.value},
        "users:update": {Permission.UPDATE_USERS.value},
        "users:delete": {Permission.DELETE_USERS.value}
    }

    PUBLIC_PATHS: List[str] = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/metrics",
        "/auth/register",
        "/auth/login",
        "/auth/refresh",
        "/auth/password-reset",
        "/auth/verify-email",
        "/roles",
        "/roles/{role_id}"
    ]

    @model_validator(mode="before")
    def parse_allowed_origins(cls, values):
        origins = values.get("ALLOWED_ORIGINS")
        if isinstance(origins, str):
            try:
                parsed = json.loads(origins)
                if isinstance(parsed, list):
                    values["ALLOWED_ORIGINS"] = parsed
                else:
                    values["ALLOWED_ORIGINS"] = [origin.strip() for origin in origins.split(",")]
            except json.JSONDecodeError:
                values["ALLOWED_ORIGINS"] = [origin.strip() for origin in origins.split(",")]
        return values

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def get_role_permissions(self, role_name: str) -> List[str]:
        return self.DEFAULT_ROLES.get(role_name, [])

    def is_valid_role(self, role_name: str) -> bool:
        return role_name in self.DEFAULT_ROLES

    def has_required_permissions(self, user_permissions: List[str], endpoint: str) -> bool:
        required = self.REQUIRED_PERMISSIONS.get(endpoint, set())
        return all(perm in user_permissions for perm in required)

    def get_refresh_secret_key(self) -> str:
        return self.JWT_REFRESH_SECRET_KEY or self.SECRET_KEY


settings = Settings()
