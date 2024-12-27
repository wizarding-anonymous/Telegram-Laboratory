# user_dashboard/src/integrations/logging_client.py

from sqlalchemy.ext.asyncio import AsyncSession
from user_dashboard.src.models.log_model import Log
from datetime import datetime

async def log_event(db: AsyncSession, level: str, message: str, service: str = "UserDashboard") -> None:
    log_entry = Log(
        level=level,
        message=message,
        service=service,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    await db.commit()
