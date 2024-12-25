# services/auth_service/src/app.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE
)
from loguru import logger
import time
import traceback
from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.api.middleware.auth_middleware import AuthMiddleware, check_permissions
from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.routers import router as api_router
from src.db.database import init_db, close_db, apply_migrations_async, get_session
from src.integrations.logging_client import LoggingClient
from src.api.controllers.auth_controller import AuthController

app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.API_VERSION,
    description="Auth Service for user management, roles, and permissions",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = f"{int(start_time * 1000)}"
    local_logger = logger.bind(request_id=request_id)

    try:
        local_logger.info(f"Incoming {request.method} {request.url.path}")

        auth_header = request.headers.get("Authorization")
        if auth_header:
            local_logger.debug(f"Authorization header present: {auth_header[:20]}...")
        else:
            local_logger.debug("No Authorization header")

        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        local_logger.info(
            f"Completed {request.method} {request.url.path} "
            f"[{response.status_code}] in {process_time:.2f}ms"
        )
        return response
    except Exception as e:
        local_logger.error(f"Request failed: {str(e)}")
        raise

app.add_middleware(
    AuthMiddleware,
    secret_key=settings.SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
    public_paths=[
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/metrics",
        "/auth/register",
        "/auth/login",
        "/auth/refresh",
        "/auth/password-reset",
        "/auth/verify-email"
    ],
)

app.add_middleware(ErrorHandlerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Total-Count",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    expose_headers=["X-Total-Count", "Authorization"],
    max_age=3600,
)

app.include_router(api_router)

async def ensure_default_roles():
    try:
        logger.info("Ensuring default roles exist...")
        async for session in get_session():
            auth_controller = AuthController(session)
            await auth_controller.ensure_default_roles()
        logger.info("Default roles verified successfully")
    except Exception as e:
        logger.error(f"Failed to ensure default roles: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def create_error_response(
    status_code: int,
    detail: str,
    path: str,
    errors: Any = None
) -> Dict[str, Any]:
    response = {
        "status_code": status_code,
        "detail": detail,
        "path": path,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    if errors:
        response["errors"] = errors
    return response

@app.on_event("startup")
async def on_startup():
    try:
        logger.info(f"Starting {settings.SERVICE_NAME}...")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Debug mode: {settings.DEBUG}")

        await init_db()
        logger.info("Database initialized")

        await apply_migrations_async()
        logger.info("Migrations applied")

        await ensure_default_roles()
        logger.info("Default roles established")

        logger.info(f"{settings.SERVICE_NAME} started successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.on_event("shutdown")
async def on_shutdown():
    try:
        logger.info(f"Shutting down {settings.SERVICE_NAME}...")
        await close_db()
        logger.info("Shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.get("/health")
async def health_check():
    try:
        await init_db()
        return {
            "status": "healthy",
            "service": settings.SERVICE_NAME,
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is unhealthy"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    headers = {}
    if exc.status_code == 401:
        headers["WWW-Authenticate"] = "Bearer"
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS_COUNT,
        log_level=settings.LOG_LEVEL.lower()
    )
