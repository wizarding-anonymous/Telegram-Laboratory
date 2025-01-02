from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.middleware.auth import AuthMiddleware
from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.routers.bot_router import router as bot_router
from src.api.routers.health_router import router as health_router
from src.api.routers.metadata_router import router as metadata_router
from src.api.schemas.response_schema import HealthCheckResponse
from src.config import settings
from src.core.database_manager import DatabaseManager
from src.core.utils.exceptions import DatabaseException
from src.db.database import close_engine, init_db, AsyncSessionLocal
from src.db.repositories.schema_repository import SchemaRepository
from src.integrations.service_discovery.client import ServiceDiscoveryClient

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.API_VERSION,
    description="Microservice for storing and managing metadata and bot information.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.add_middleware(
    AuthMiddleware,
    secret_key=settings.SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bot_router, prefix="/api/v1")
app.include_router(metadata_router, prefix="/api/v1")
app.include_router(health_router)


@app.on_event("startup")
async def on_startup():
    logger.info(f"Starting {settings.SERVICE_NAME}...")
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")

        # Initialize DatabaseManager and check connection
        db_manager = DatabaseManager()
        async with AsyncSessionLocal() as session:
            if not await db_manager.check_db_connection():
                logger.error("Failed to establish database connection")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to establish database connection"
                )
            logger.info("Meta database connection established successfully")
            schema_repository = SchemaRepository(session=session)
            await db_manager.apply_migrations_for_all_bots(schema_repository=schema_repository)
            logger.info("Migrations applied for all bots successfully")

        # Register service with Service Discovery
        service_discovery_client = ServiceDiscoveryClient()
        service_id = await service_discovery_client.register_service()
        app.state.service_id = service_id
        logger.info(f"Service registered with service id: {service_id}")
        app.state.service_discovery_client = service_discovery_client

        logger.info(f"{settings.SERVICE_NAME} started successfully")


    except HTTPException as e:
        logger.error(f"Service startup failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during service startup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Service startup failed: {str(e)}"
        )


@app.on_event("shutdown")
async def on_shutdown():
    logger.info(f"Shutting down {settings.SERVICE_NAME}...")
    try:
        if hasattr(app.state, 'service_discovery_client'):
          await app.state.service_discovery_client.unregister_service(app.state.service_id)
          await app.state.service_discovery_client.close()
          logger.info("Service unregistered from Service Discovery")

        db_manager = DatabaseManager()
        await db_manager.close_engine()
        logger.info("Database connections closed successfully")
        logger.info(f"{settings.SERVICE_NAME} shut down successfully")
    except Exception as e:
        logger.error(f"Error during service shutdown: {str(e)}")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "details": exc.errors()},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred. Please try again later."},
    )

@app.get(
    "/",
    response_model=HealthCheckResponse,
    tags=["Root"],
    summary="Service root endpoint",
    description="Returns basic service information and status",
)
async def read_root():
    try:
        return HealthCheckResponse(
            status="healthy",
            details={
                "service": {
                    "status": "healthy",
                    "message": f"Welcome to {settings.SERVICE_NAME}!"
                }
            },
            version=settings.API_VERSION,
            migrations="up-to-date"
        )
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS_COUNT,
        log_level=settings.LOG_LEVEL.lower(),
    )