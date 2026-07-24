# this file is for handling the security and authentication logic
#this is like helper tools that router can use
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from sqlalchemy import select
from app.database import get_db
from app import models
from fastapi import Depends, HTTPException, status
from app.models.users import User
from app.schemas.user import UserRegister, UserLogin, TokenResponses
from fastapi.security import HTTPBearer
from app.schemas import user
from uuid import UUID
password_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")#for verify the old password
oauth=OAuth2PasswordBearer(tokenUrl="/auth/login")#take the token from header and send to function

#verify register user
def hash_password(plain_password:str)->str:
    return password_hashing.hash(plain_password) # method #mock hash

def verify_password(plain_password:str,hash_password:str)->bool:
    return password_hashing.verify(plain_password,hash_password)

def create_access_token(data:dict)->str:
    to_encode=data.copy()#to modify not original data
    expire=datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token:str)->str:
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        email:str=payload.get("sub")#who is this token about with expiration time
        if email is None:
            raise ValueError("No token for this email")
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
        token:str=Depends(oauth),
        db:AsyncSession=Depends(get_db)
)->models:
    email=decode_token(token)
    result = await db.execute(select(User).where(User.email==email))
    user=result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


async def register_user(user_data:UserRegister,db:AsyncSession):#depends written in router file

    if user_data.username is None:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    if user_data.password is None:
        raise HTTPException(status_code=400,detail="Password cannot be empty")
    
    #email check
    result = await db.execute(select(User).where(User.email==user_data.email))#check in db
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already registerd")
    
    #username check
    result = await db.execute(select(User).where(User.username==user_data.username))
    existing_username = result.scalar_one_or_none()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="username already existed")
    
    new_user=User(
        email=user_data.email,#->models
        username=user_data.username,
        password=hash_password(user_data.password)#hashpassword function is called here for password hashing
    )
    
    db.add(new_user)
    await db.flush()
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def login_user(db:AsyncSession, email:str,password:str)->user:
    result=await db.execute(select(User).where(User.email==email))
    user=result.scalar_one_or_none()
    if not user or not verify_password(password,user.password):#call verify password for verify password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=403,detail="Account is deactivated")
    return user


async def delete_account(db:AsyncSession, user_id:UUID):
    result=await db.execute(select(User).where(User.id==user_id))
    user=result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            404,"no user"
        )
    await db.delete(user)
    await db.commit()