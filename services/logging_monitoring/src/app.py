from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from src.api.routers import log_router, health_router, alert_router
from src.config import settings
from src.integrations.logging_client import logger, configure_logger
from src.api.middleware import ErrorHandlerMiddleware, AuthMiddleware
from src.db.database import close_engine

app = FastAPI(title="Logging and Monitoring Service", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add exception handling middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(AuthMiddleware)


# Include routers
app.include_router(log_router)
app.include_router(health_router)
app.include_router(alert_router)

# Initialize logging
configure_logger(service_name="LoggingMonitoring")


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    """
    logger.info("Starting up Logging and Monitoring Service")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    Closes database engine
    """
    logger.info("Shutting down Logging and Monitoring Service")
    await close_engine()


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="debug" if settings.DEBUG else "info",
    )