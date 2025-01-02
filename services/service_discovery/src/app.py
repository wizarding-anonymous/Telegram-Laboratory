from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from src.api.routers import service_router, health_router
from src.config import settings
from src.integrations.logging_client import logger, configure_logger
from src.api.middleware import ErrorHandlerMiddleware, AuthMiddleware
from src.db.database import close_engine

app = FastAPI(title="Service Discovery", version="0.1.0")

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
app.include_router(service_router)
app.include_router(health_router)

# Initialize logging
configure_logger(service_name="ServiceDiscovery")


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    """
    logger.info("Starting up Service Discovery")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    Closes database engine
    """
    logger.info("Shutting down Service Discovery")
    await close_engine()


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
         log_level="debug" if settings.DEBUG else "info",
    )