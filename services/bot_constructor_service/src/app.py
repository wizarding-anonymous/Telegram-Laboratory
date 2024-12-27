from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import (
    bot_router,
    block_router,
    health_router,
    AuthMiddleware,
    ErrorHandlerMiddleware,
)
from src.config import settings
from src.db.database import init_db, close_engine
from src.integrations.logging_client import LoggingClient
from prometheus_fastapi_instrumentator import Instrumentator


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

app = FastAPI(
    title="Bot Constructor Service",
    description="Microservice for creating and managing Telegram bots.",
    version="0.1.0",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handling middleware
app.add_middleware(ErrorHandlerMiddleware)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Routers
app.include_router(bot_router, prefix="/bots", tags=["Bots"])
app.include_router(block_router, prefix="/blocks", tags=["Blocks"])
app.include_router(health_router, prefix="/health", tags=["Health"])

# Prometheus
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics", "/health"],
)
instrumentator.instrument(app)
@app.get("/metrics")
async def metrics():
    return instrumentator.expose(app)


@app.on_event("startup")
async def startup_event():
    logging_client.info("Starting up the application")
    await init_db()
    logging_client.info("Database initialized")

@app.on_event("shutdown")
async def shutdown_event():
    logging_client.info("Shutting down the application")
    await close_engine()
    logging_client.info("Database connection closed")