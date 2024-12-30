from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from src.db.database import Base


class Block(Base):
    """
    Model for storing block information.
    """
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(255), nullable=False, index=True)
    content = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_message_id = Column(Integer, nullable=True)
    bot_message_id = Column(Integer, nullable=True)
    connections = relationship(
        "Connection",
        primaryjoin="Block.id==Connection.source_block_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
        backref="source_block"
    )


    def __repr__(self):
        return f"<Block(id={self.id}, type='{self.type}')>"
    
class Connection(Base):
    """
    Model for storing connections between blocks.
    """
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    source_block_id = Column(Integer, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False, index=True)
    target_block_id = Column(Integer, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False, index=True)

    def __repr__(self):
         return f"<Connection(source_block_id={self.source_block_id}, target_block_id='{self.target_block_id}')>"