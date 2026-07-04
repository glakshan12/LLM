from pydantic import BaseModel, EmailStr, HttpUrl, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
class UserRegister(BaseModel):
    username:str
    email:EmailStr
    password:str=Field(max_length=71)
class UserLogin(BaseModel):
    email:EmailStr
    password:str
class UserResponse(BaseModel):
    id:UUID
    username:str
    email:EmailStr
    is_active:bool
    created_at:datetime
    class Config():
         from_attributes = True#for converting orm into pydantic
class TokenResponses(BaseModel):
    access_token:str
    token_type:str="bearer"