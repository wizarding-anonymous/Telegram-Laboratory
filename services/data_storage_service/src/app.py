from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.api.routers import (
    bot_router,
    health_router,
    metadata_router,
    schema_router,
)
from src.config import settings
from src.integrations.logging_client import configure_logger, logger
from src.api.middleware import ErrorHandlerMiddleware, AuthMiddleware
import uvicorn


app = FastAPI(title="Data Storage Service", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize logging
configure_logger(service_name="DataStorageService")


# Add error handling middleware
app.add_middleware(ErrorHandlerMiddleware)


# Add authentication middleware
app.add_middleware(AuthMiddleware)



# Include routers
app.include_router(bot_router)
app.include_router(health_router)
app.include_router(metadata_router)
app.include_router(schema_router)




@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    """
    logger.info("Starting up Data Storage Service")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    Closes database engine
    """
    logger.info("Shutting down Data Storage Service")
    from src.db.database import close_engine

    await close_engine()


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True if settings.MODE == "development" else False, # Disable reload in production
        log_level= "debug" if settings.MODE == "development" else "info",
    )