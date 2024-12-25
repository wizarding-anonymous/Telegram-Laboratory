# services\bot_constructor_service\src\db\models\block_model.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src.db.database import Base


class Block(Base):
    """
    Database model for blocks.
    """
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True, comment="ID of the bot this block belongs to")
    type = Column(String(255), nullable=False, comment="Type of the block (e.g., 'message', 'action')")
    content = Column(JSON, nullable=False, comment="Content of the block")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Timestamp of creation")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="Timestamp of the last update")

    # Relationships
    bot = relationship("Bot", back_populates="blocks")
    connections = relationship("Connection", back_populates="source_block", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Block(id={self.id}, bot_id={self.bot_id}, type={self.type})>"
