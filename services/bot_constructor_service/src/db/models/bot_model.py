from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from src.db.database import Base


class Bot(Base):
    """
    Model for storing bot information.
    """
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=True, default="draft")
    version = Column(String(50), nullable=True, default="1.0.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    logic = Column(JSON, nullable=True)  # Using JSON type to store bot logic
    token = Column(Text, nullable=False) # Telegram bot token
    library = Column(String(50), nullable=False) # library (telegram_api, aiogram, telebot)
    
    def __repr__(self):
        return f"<Bot(id={self.id}, name='{self.name}')>"