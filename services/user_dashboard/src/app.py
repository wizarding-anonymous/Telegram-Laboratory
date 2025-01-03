from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.api.routers import user_router, bot_router, analytics_router, notification_router, integration_router, health_router
from src.integrations.auth_service import AuthService
from src.api.middleware import AuthMiddleware, ErrorHandlerMiddleware
from loguru import logger
import uvicorn


app = FastAPI(
    title="User Dashboard Service",
    description="This service provides a user dashboard for managing bots and user information.",
    version="1.0.0",
)

# CORS configuration - allows requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, consider restricting this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handler middleware
app.add_middleware(ErrorHandlerMiddleware)

# Include routers
app.include_router(user_router.router, dependencies=[Depends(AuthMiddleware())])
app.include_router(bot_router.router, dependencies=[Depends(AuthMiddleware())])
app.include_router(analytics_router.router, dependencies=[Depends(AuthMiddleware())])
app.include_router(notification_router.router, dependencies=[Depends(AuthMiddleware())])
app.include_router(integration_router.router, dependencies=[Depends(AuthMiddleware())])
app.include_router(health_router.router)



@app.on_event("startup")
async def startup_event():
    """
    Startup event to initialize components and log service info.
    """
    logger.info(f"Starting {settings.SERVICE_NAME} service")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Listening on port: {settings.APP_PORT}")
    logger.info(f"Auth service url: {settings.AUTH_SERVICE_URL}")
    logger.info(f"Logging and Monitoring service url: {settings.LOGGING_MONITORING_URL}")
    logger.info(f"Redis url: {settings.REDIS_URL}")
    logger.info(f"API Gateway url: {settings.API_GATEWAY_URL}")



if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )