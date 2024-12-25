# services\api_gateway\src\app.py
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid

from src.core.config import settings
from src.core.logger import setup_logging, get_logger
from src.core.redis import setup_redis, close_redis
from src.core.metrics import setup_metrics
from src.core.tracing import setup_tracing
from src.api.middleware.error_handler import setup_error_handler
from src.api.middleware.rate_limiter import setup_rate_limiter
from src.core.load_balancer import get_load_balancer
from src.core.cache_manager import get_cache_manager
from src.db.database import get_database
from src.api.routes import setup_routes

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    Инициализация и освобождение ресурсов.
    """
    # Инициализация компонентов
    try:
        # Настройка логирования
        setup_logging()
        logger.info("Starting API Gateway...")

        # Подключение к базе данных
        database = get_database()
        await database.init()
        logger.info("Database connection established")

        # Подключение к Redis
        await setup_redis()
        logger.info("Redis connection established")

        # Инициализация кэш-менеджера
        cache_manager = get_cache_manager()
        logger.info("Cache manager initialized")

        # Инициализация балансировщика нагрузки
        load_balancer = get_load_balancer()
        await load_balancer.startup()
        logger.info("Load balancer initialized")

        # Настройка метрик
        if settings.METRICS_ENABLED:
            setup_metrics(app)
            logger.info("Metrics collection enabled")

        # Настройка трейсинга
        if settings.TRACING_ENABLED:
            setup_tracing(app)
            logger.info("Distributed tracing enabled")

        # Регистрация микросервисов
        for service_name, config in settings.SERVICES.items():
            await load_balancer.register_service(
                service_name,
                str(config["host"]),
                int(config["port"]),
                health_check_url=config.get("health_check_url")
            )
            logger.info(f"Registered service: {service_name}")

        yield

        # Освобождение ресурсов при остановке
        logger.info("Shutting down API Gateway...")
        
        await load_balancer.shutdown()
        await database.dispose()
        await close_redis()
        
        logger.info("API Gateway shutdown complete")

    except Exception as e:
        logger.error(f"Error during application lifecycle: {e}")
        raise

def create_app() -> FastAPI:
    """
    Создание и настройка приложения FastAPI.

    Returns:
        FastAPI: Настроенное приложение
    """
    # Создание приложения
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=settings.OPENAPI_URL,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        lifespan=lifespan
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Настройка обработчика ошибок
    setup_error_handler(app)

    # Настройка rate limiter
    if settings.RATE_LIMIT_ENABLED:
        setup_rate_limiter(app)

    # Добавление middleware для request_id
    @app.middleware("http")
    async def add_request_id(request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # Настройка маршрутов
    setup_routes(app)

    @app.get("/health")
    async def health_check():
        """Эндпоинт для проверки здоровья API Gateway."""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }

    @app.get("/status")
    async def gateway_status():
        """Эндпоинт для получения статуса компонентов API Gateway."""
        load_balancer = get_load_balancer()
        cache_manager = get_cache_manager()

        services_status = await load_balancer.get_service_stats()
        cache_stats = await cache_manager.get_cache_stats()

        return {
            "status": "operational",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "services": services_status,
            "cache": cache_stats,
            "rate_limit": {
                "enabled": settings.RATE_LIMIT_ENABLED,
                "limit_per_minute": settings.RATE_LIMIT_PER_MINUTE
            }
        }

    return app


# Создание экземпляра приложения
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    # Запуск приложения с uvicorn
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower()
    )