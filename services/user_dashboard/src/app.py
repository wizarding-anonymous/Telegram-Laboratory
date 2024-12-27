# user_dashboard/src/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.routers.bot_router import router as bot_router
from app.api.routers.user_router import router as user_router
from app.api.middleware.auth_middleware import AuthMiddleware
from app.api.middleware.validation_middleware import ValidationMiddleware
from app.db.database import init_db

# Создание экземпляра приложения FastAPI
app = FastAPI(
    title="User Dashboard Service",
    description="API для управления пользователями, ботами и интеграциями",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS (при необходимости)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Замените "*" на список разрешенных доменов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка Trusted Hosts (для безопасности)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Замените "*" на список доверенных хостов
)

# Пользовательские middleware
app.add_middleware(AuthMiddleware)
app.add_middleware(ValidationMiddleware)

# Подключение маршрутов
app.include_router(user_router, prefix="/user", tags=["User Management"])
app.include_router(bot_router, prefix="/bots", tags=["Bot Management"])

# Событие запуска
@app.on_event("startup")
async def on_startup():
    """
    Выполняется при старте приложения.
    """
    await init_db()  # Инициализация базы данных

# Событие завершения работы
@app.on_event("shutdown")
async def on_shutdown():
    """
    Выполняется при завершении работы приложения.
    """
    # Здесь можно закрыть дополнительные ресурсы, например, подключения
    pass

# Маршрут проверки состояния сервиса
@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Возвращает статус сервиса.
    """
    return {"status": "ok"}
