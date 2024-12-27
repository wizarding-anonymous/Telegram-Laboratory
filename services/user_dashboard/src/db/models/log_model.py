# user_dashboard/src/models/log_model.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from user_dashboard.src.db.database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), nullable=False)
    message = Column(String(255), nullable=False)
    service = Column(String(50), nullable=False, default="UserDashboard")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
