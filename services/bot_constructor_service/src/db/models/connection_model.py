# services\bot_constructor_service\src\db\models\connection_model.py
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from src.db.database import Base


class Connection(Base):
    """
    Database model for connections between blocks.
    """
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    source_block_id = Column(
        Integer, 
        ForeignKey("blocks.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True, 
        comment="ID of the source block"
    )
    target_block_id = Column(
        Integer, 
        ForeignKey("blocks.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True, 
        comment="ID of the target block"
    )
    type = Column(
        String(255), 
        nullable=False, 
        default="default", 
        comment="Type of the connection (e.g., 'default', 'conditional')"
    )
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        comment="Timestamp of creation"
    )

    # Relationships
    source_block = relationship("Block", foreign_keys=[source_block_id], back_populates="connections")
    target_block = relationship("Block", foreign_keys=[target_block_id])

    def __repr__(self):
        return f"<Connection(id={self.id}, source_block_id={self.source_block_id}, target_block_id={self.target_block_id}, type={self.type})>"
