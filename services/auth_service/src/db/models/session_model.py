# services\auth_service\src\db\models\session_model.py
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from .base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    refresh_token = Column(Text, unique=True, nullable=False)  # Изменено с String(255) на Text
    expires_at = Column(DateTime(timezone=True), nullable=False)