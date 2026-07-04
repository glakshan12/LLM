from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class MessageCreate(BaseModel):
    conversation_id:UUID
    message:str

class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str  # "user" or "assistant"
    content: str  # The message text
    token_count: int  # Number of tokens
    created_at: datetime

    class config:
        from_attribute=True

class ConversationWithMessage(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []  # List of all messages in this conversation
 
    class Config:
        from_attributes = True