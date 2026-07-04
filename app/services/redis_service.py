import redis
import json
from app.config import Settings
from typing import Optional, Any
redis_client=redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
#decode responses is automatically convert the binary data into python strings

#caching operations
async def get_cache(key:str)->Optional[Any]:
    try:
        value=redis_client.get(key)
        if value:
            return value
        return None
    except Exception as e:
        print(f"Error getting cache for {key}:{e}")
        return None
async def set_cache(key:str,value:str,ttl:int=3600)->bool:
    try:
        # Set value in Redis with expiration
        redis_client.set(key, value, ex=ttl)
        return True
    except Exception as e:
        # If Redis error, log and return False
        print(f"Error setting cache for {key}: {e}")
        return False
#if any information changes  means then redis delete the cache memory and update it with new data
async def delete_cache(key: str) -> bool:
    try:
        # Delete key from Redis
        redis_client.delete(key)
        return True
    except Exception as e:
        # If Redis error, log and return False
        print(f"Error deleting cache for {key}: {e}")
        return False
    
#------------------------------------------------------------#

#rate limit

async def is_rate_limited(user_id: int,limit:int=20,window:int=3600) -> bool:
    try:
        # Create rate limit key
        key = f"rate_limit:user:{user_id}"
        # Increment counter
        count = redis_client.incr(key)
        # If this is the first request in the window, set expiration
        if count == 1:
            redis_client.expire(key, window)
        # Check if limit exceeded
        if count > limit:
            return True  # Rate limited (blocked)
        return False  # Not limited (allowed)
    except Exception as e:
        # If Redis error, log and allow request (fail open)
        print(f"Error checking rate limit for user {user_id}: {e}")
        return False  # Allow request if Redis is down
async def get_rate_limit_remaining(user_id: int, limit: int = 20) -> int:
    try:
        # Create rate limit key
        key = f"rate_limit:user:{user_id}"
        # Get current count
        count = redis_client.get(key)
        # If no count, all requests remaining
        if not count:
            return limit
        # Calculate remaining
        remaining = limit - int(count)
        # Return 0 if exceeded
        return max(0, remaining)
    except Exception as e:
        # If Redis error, return full limit
        print(f"Error getting rate limit remaining for user {user_id}: {e}")
        return limit
async def reset_rate_limit(user_id: int) -> bool:
    try:
        key = f"rate_limit:user:{user_id}"
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Error resetting rate limit for user {user_id}: {e}")
        return False
async def check_redis_connection() -> bool:
    try:
        result = redis_client.ping()
        return result is True
    except Exception as e:
        print(f"Redis connection error: {e}")
        return False