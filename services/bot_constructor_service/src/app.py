# services\bot_constructor_service\src\app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger
from src.config import settings
from src.db.database import init_db, close_engine
from src.api.routers import bot_router, block_router, health_router

# Create FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.API_VERSION,
    description="Microservice for building and managing Telegram bots",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),  # Read allowed origins from .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bot_router)
app.include_router(block_router)
app.include_router(health_router)

# Events
@app.on_event("startup")
async def on_startup():
    """Startup event handler."""
    logger.info("Starting application...")
    await init_db()
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def on_shutdown():
    """Shutdown event handler."""
    logger.info("Shutting down application...")
    await close_engine()
    logger.info("Application shut down successfully")


# Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
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


# Root and health endpoints
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint for the Bot Constructor service.
    """
    return {
        "message": "Welcome to the Bot Constructor service!",
        "version": settings.API_VERSION,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "details": "Service is running"}


# Main entry point for running the application
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting application on port {settings.APP_PORT}")
    uvicorn.run("src.app:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)
