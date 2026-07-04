import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, UUID,func
from sqlalchemy.orm import relationship
import app.database

class Conversation(app.database.Base):
    __tablename__="conversations"
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id=Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title=Column(String, nullable=False)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    updated_at=Column(DateTime(timezone=True), server_default=func.now(),onupdate=func.now())
    user=relationship("User", back_populates="conversations")
    messages=relationship("Message",back_populates="conversation",cascade="all,delete-orphan")