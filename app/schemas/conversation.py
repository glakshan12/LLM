from pydantic import BaseModel
from datetime import datetime
#this file is specailly for conversation
from uuid import UUID
class ConversationCreate(BaseModel):
    title:str
class ConversationResponse(BaseModel):#this is for to look up when the conversation is created
    id:UUID
    user_id:UUID
    title:str
    created_at:datetime
    updated_at:datetime

class ConversationRename(BaseModel):
    title:str
    
    class Config:
        from_attributes=True #pydantic translated the sql data into JSON for validation