# user_dashboard/src/app.py

from fastapi import FastAPI
from user_dashboard.src.api.controllers import user_controller, bot_controller

app = FastAPI(
    title="User Dashboard API",
    description="API для управления пользователями и ботами",
    version="1.0.0"
)

# Подключение роутеров
app.include_router(user_controller.router)
app.include_router(bot_controller.router)

@app.get("/health", tags=["Health"], response_model=dict)
async def health_check() -> dict:
    return {"status": "healthy"}
