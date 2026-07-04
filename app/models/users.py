import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, UUID,func
from sqlalchemy.orm import relationship
import app.database

class User(app.database.Base):
    __tablename__= "users"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,default=uuid.uuid4)
    username=Column(String, index=True, nullable=False)
    email=Column(String, unique=True, index=True, nullable=False)
    password=Column(String, nullable=False)
    is_active=Column(Boolean, default=True)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    conversations=relationship("Conversation", back_populates="user",cascade="all,delete-orphan")




