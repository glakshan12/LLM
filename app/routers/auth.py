from fastapi import Depends, HTTPException, APIRouter, status
from app.services import auth_services
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import redis_service
from app.models import users
import json
import app.schemas
from app.schemas.user import UserResponse
from app.schemas.user import UserRegister, UserLogin, TokenResponses

router=APIRouter(prefix="/auth",tags=["auth"])
@router.post("/register",response_model=UserResponse,status_code=201)
async def register(user_data:UserRegister,db:AsyncSession=Depends(get_db)):
    user=await auth_services.register_user(user_data=user_data,db=db)
    return user

@router.post("/login",response_model=TokenResponses)
async def login(credentials:UserLogin, db:AsyncSession=Depends(get_db)):
    user=await auth_services.login_user(db,credentials.email,credentials.password)
    token=auth_services.create_access_token(data={"sub":user.email})
    return{"access_token":token,"token_type":"bearer"}

@router.get("/me",response_model=UserResponse)
async def get_me(current_user:app.schemas.user.UserResponse=Depends(auth_services.get_current_user)):
    #from redis_service import get_cache
    #cache the user id until logs in even if page refreshed so not needed from db
    cache_key=f"user:{current_user.id}"
    cached_user=await redis_service.get_cache(cache_key)#get the cache key for user id
    if cached_user:#if cache not found then contniue to database
        print(f"[cache hit] User {current_user.id} from Redis")
        return json.loads(cached_user)#take the file from convert into python object and return it
    print(f"[cache miss] user {current_user.id} from database")
    user_data={#this is for prepare the data for cache if caching is not found for user id
        "id":str(current_user.id),
        "username":current_user.username,
        "email":current_user.email,
        "is_active":current_user.is_active,
        "created_at":current_user.created_at.isoformat()
    }
    await redis_service.set_cache(cache_key,json.dumps(user_data),ttl=3600)
    return current_user

@router.delete("/me")
async def delete_user(current_user:users=Depends(auth_services.get_current_user),db:AsyncSession=Depends(get_db)):
    await auth_services.delete_account(db,current_user.id)
    return {"detail":"account deleted succesfully"}

