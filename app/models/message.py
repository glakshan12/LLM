import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, UUID,func
from sqlalchemy.orm import relationship
import app.database

class Message(app.database.Base):
    __tablename__="messages"
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id=Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role=Column(String, nullable=False)
    content=Column(Text, nullable=False)
    token_count=Column(Integer,default=0)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    conversation=relationship("Conversation", back_populates="messages")