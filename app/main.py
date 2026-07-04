from fastapi import FastAPI
from app.config import Settings

app=FastAPI(
    title="AI Chat API",
    description="Production grade backend platform with gemini ai",
    version="1.0.0"
)

#registe the router files here

from app.routers import auth,conversation_router,chat,health

#auth/endpoints
app.include_router(auth.router)
#conversation/endpoints
app.include_router(conversation_router.router)
#chat/endpoints
app.include_router(chat.router)
app.include_router(health.router)

#---------------------------------------#

#root endpoint

@app.get("/")
async def root():
    return{
        "message":"Welcome to ai chat api",
        "docs":"/docs",#swagger UI
        "redoc":"/redoc" #alternative api docs
    }

@app.on_event("startup")
async def startup_event():
    print("🚀 API Starting...")
    print("✅ Auth endpoints ready: POST /auth/register, POST /auth/login, GET /auth/me")
    print("✅ Conversation endpoints ready: POST/GET/PUT/DELETE /conversations")
    print("✅ Chat endpoints ready: POST /chat, GET /chat/stream")
    print("✅ Health check ready: GET /health")

@app.on_event("shutdown")
async def shutdown_event():
    print("APP Shutting down")