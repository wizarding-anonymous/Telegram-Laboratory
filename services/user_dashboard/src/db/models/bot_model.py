# user_dashboard/src/models/bot_model.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Bot(Base):
    """
    Модель для таблицы 'bots' в базе данных.
    """
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Связь с моделью User
    user = relationship("User", back_populates="bots")

    # Связь с блоками логики бота
    blocks = relationship("Block", back_populates="bot", cascade="all, delete-orphan")


class Block(Base):
    """
    Модель для таблицы 'blocks' в базе данных.
    """
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)
    type = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связь с моделью Bot
    bot = relationship("Bot", back_populates="blocks")
