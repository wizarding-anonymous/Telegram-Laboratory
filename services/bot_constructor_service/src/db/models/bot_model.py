# services\bot_constructor_service\src\db\models\bot_model.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src.db.database import Base


class Bot(Base):
    """
    Database model for bots.
    """
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True, comment="ID of the user owning the bot")
    name = Column(String(255), nullable=False, comment="Name of the bot")
    description = Column(Text, nullable=True, comment="Description of the bot")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Timestamp of creation")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="Timestamp of the last update")

    # Relationships
    blocks = relationship("Block", back_populates="bot", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bot(id={self.id}, name={self.name}, user_id={self.user_id})>"
