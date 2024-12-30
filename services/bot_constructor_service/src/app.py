from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import (
    bot_router,
    block_router,
    health_router,
    message_router,
    keyboard_router,
    callback_router,
    chat_router,
    webhook_router,
    flow_router,
    variable_router,
    db_router,
    api_request_router,
    bot_settings_router,
    connection_router,
    middleware,
)
from src.config import settings
from src.db.database import init_db, close_engine, check_db_connection, get_session
from src.integrations.logging_client import LoggingClient
from src.integrations.redis_client import redis_client
from src.integrations import get_telegram_client
from src.core.utils.exceptions import TelegramAPIException


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

app = FastAPI(
    title="Bot Constructor Service",
    description="Microservice for creating and managing Telegram bots.",
    version=settings.API_VERSION,
)


# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

# Add exception handling middleware
app.add_middleware(middleware.ErrorHandlerMiddleware)



# Routers
app.include_router(bot_router, prefix="/bots", tags=["Bots"])
app.include_router(block_router, prefix="/bots", tags=["Blocks"])
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(message_router, prefix="/bots", tags=["Messages"])
app.include_router(keyboard_router, prefix="/bots", tags=["Keyboards"])
app.include_router(callback_router, prefix="/bots", tags=["Callbacks"])
app.include_router(chat_router, prefix="/bots", tags=["Chats"])
app.include_router(webhook_router, prefix="/bots", tags=["Webhooks"])
app.include_router(flow_router, prefix="/bots", tags=["Flows"])
app.include_router(variable_router, prefix="/bots", tags=["Variables"])
app.include_router(db_router, prefix="/bots", tags=["Database"])
app.include_router(api_request_router, prefix="/bots", tags=["Api Requests"])
app.include_router(bot_settings_router, prefix="/bots", tags=["Bot Settings"])
app.include_router(connection_router, prefix="/bots", tags=["Connections"])


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
    await redis_client.connect()
    logging_client.info("Redis client connected")
    
    # Initialize telegram client
    telegram_client = get_telegram_client(settings.TELEGRAM_BOT_LIBRARY)
    try:
        await telegram_client.check_connection(bot_token=settings.TELEGRAM_BOT_TOKEN)
        logging_client.info("Telegram token is valid")
    except Exception as e:
         logging_client.error(f"Telegram token is invalid, exception: {e}")
         raise TelegramAPIException(detail=f"Telegram token is invalid: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    logging_client.info("Shutting down the application")
    await close_engine()
    logging_client.info("Database connection closed")
    await redis_client.close()
    logging_client.info("Redis connection closed")


@app.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    """Health check endpoint."""
    db_connected = await check_db_connection(session)
    redis_connected = await redis_client.exists("health_check")

    if db_connected and redis_connected:
      return {"status": "ok", "details": "Service is healthy"}
    else:
       raise HTTPException(status_code=500, detail=f"Service is not healthy db_connection: {db_connected} redis_connection: {redis_connected}")