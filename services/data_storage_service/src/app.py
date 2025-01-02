from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.api.routers import bot_router, health_router, metadata_router, schema_router
from src.core.utils import check_migrations_status
from src.config import settings
from src.integrations.logging_client import LoggingClient
from src.api.middleware import ErrorHandlerMiddleware
import uvicorn
from src.db.database import engine


app = FastAPI(title="Data Storage Service", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add error handling middleware
app.add_middleware(ErrorHandlerMiddleware)


# Include routers
app.include_router(bot_router)
app.include_router(health_router)
app.include_router(metadata_router)
app.include_router(schema_router)



# Initialize logging
logging_client = LoggingClient(service_name="DataStorageService")


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    Performs a database migrations check and register service in Service Discovery.
    """
    if await check_migrations_status():
         logging_client.logger.info("Database migrations status is ok")
    else:
        logging_client.logger.error("Database migrations status check failed")

    from src.integrations.service_discovery import ServiceDiscoveryClient
    service_discovery_client = ServiceDiscoveryClient()
    try:
        await service_discovery_client.register_service(address="localhost", port=8001)
    except Exception as e:
        logging_client.logger.error(f"Error registering service in Service Discovery: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    Unregister service from service discovery.
    """
    logging_client.logger.info("Shutting down Data Storage Service")

    from src.integrations.service_discovery import ServiceDiscoveryClient
    service_discovery_client = ServiceDiscoveryClient()
    try:
         await service_discovery_client.unregister_service()
    except Exception as e:
        logging_client.logger.error(f"Error unregistering service from Service Discovery: {e}")

    from src.db.database import close_engine
    await close_engine()


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )