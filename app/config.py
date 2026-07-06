from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DATABASE_URL:str
    REDIS_URL:str="redis://localhost:6379"
    SECRET_KEY:str
    NVIDIA_API:str
    NVIDIA_MODEL:str="meta/llama-3.1-8b-instruct"
    DEBUG:bool=False
    ALGORITHM:str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int=60
    
    RATE_LIMIT_REQUESTS: int = 20  # max requests per user
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    APP_NAME: str = "AI Chat API"
   

    class Config:
        env_file=".env.local"
settings=Settings()    