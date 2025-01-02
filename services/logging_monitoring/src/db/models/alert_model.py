from sqlalchemy import Column, Integer, String, DateTime, func, Float
from sqlalchemy.orm import relationship
from .base import Base


class Alert(Base):
    """
    SQLAlchemy model for storing alert rules in the database.
    """

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    metric = Column(String(255), nullable=False, index=True)
    threshold = Column(Float, nullable=False)
    operator = Column(String(10), nullable=False)
    notification_channel = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    slack_webhook = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Alert(id={self.id}, metric='{self.metric}')>"