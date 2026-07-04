from fastapi import Depends, HTTPException, APIRouter, status,Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import auth_services, llm, conversation_service,redis_service
from app.models.users import User
from app.schemas.message_schemas import MessageCreate, MessageResponse
from uuid import UUID
import json
import httpx

router=APIRouter(prefix="/chat",tags=["chat"])
#non stream
@router.post("/", response_model=MessageResponse, status_code=201)
async def send_message(
    chat_request: MessageCreate,
    current_user: User = Depends(auth_services.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if await redis_service.is_rate_limited(user_id=current_user.id,limit=20,window=3600):
        remaining=await redis_service.get_rate_limit_remaining(current_user.id)
        #why check rate limit first becasue gemini api calls are expensive, so instead of waste api call on blocked users, check the rate limit first
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded, try again later, request remaining {remaining}"
        ) 
    #for verify the conversation exists  
    conversation = await conversation_service.get_conversation_by_id(
        db=db,
        user_id=current_user.id,
        conversation_id=chat_request.conversation_id
    )
    # If conversation not found, raise 404
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or you don't have access"
        )
    # Step 2: Save user's message to database
    user_message = await llm.save_message(
        db=db,
        conversation_id=chat_request.conversation_id,
        role="user",
        content=chat_request.message,
        token_count=0
    )
    # Step 2b: Count tokens in user's message and update
    user_token_count = await llm.count_tokens(chat_request.message)
    user_message.token_count = user_token_count
    await db.commit()
    # Step 3: Call API (non-streaming)
    try:
        ai_response = await llm.call_api_non_streaming(
            db=db,
            conversation_id=chat_request.conversation_id,
            user_message=chat_request.message
        )
    except Exception as e:
        print(f" API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI temporarily busy now"
        )
    
    return ai_response

#stream 
@router.get("/stream")
async def stream_message(
    conversation_id: UUID = Query(..., description="Which conversation to send message in"),
    message: str = Query(..., description="User's message"),
    current_user: User = Depends(auth_services.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if await redis_service.is_rate_limited(user_id=current_user.id,limit=20,window=3600):
        remaining=await redis_service.get_rate_limit_remaining(current_user.id)
        #why check rate limit first becasue gemini api calls are expensive, so instead of waste api call on blocked users, check the rate limit first
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded, try again later, request remaining {remaining}"
        )
    conversation = await conversation_service.get_conversation_by_id(
        db=db,
        user_id=current_user.id,
        conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or you don't have access"
        )
    
    # Step 2: Save user's message to database
    # Why? Keep conversation history
    user_message = await llm.save_message(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=message,
        token_count=0  # Will update below
    )
    user_token_count = await llm.count_tokens(message)
    user_message.token_count = user_token_count
    await db.commit()
    async def generate():
        complete_response = ""
        try:
            #  Get streaming response from api
            # This returns an async generator that yields chunks
            stream_generator = llm.call_api_streaming(
                db=db,
                conversation_id=conversation_id,
                user_message=message
            )
            async for chunk in stream_generator:
                complete_response += chunk
                
                # Format as SSE event and yield to client
                # Client receives: data: {"content":"Hi","status":"streaming"}\n\n
                event_data = {
                    "content": chunk,
                    "status": "streaming"
                }
                yield f"data: {json.dumps(event_data)}\n\n"
            response_token_count = await llm.count_tokens(complete_response)
            assistant_message = await llm.save_message(
                db=db,
                conversation_id=conversation_id,
                role="assistant",
                content=complete_response,
                token_count=response_token_count
            )
            completion_event = {
                "status": "complete",
                "message_id": str(assistant_message.id)
            }
            yield f"data: {json.dumps(completion_event)}\n\n"
            
        except Exception as e:
            # If error occurs during streaming, send error event
            # Client receives: data: {"status":"error","detail":"..."}\n\n
            print(f"Error during streaming: {e}")
            error_event = {
                "status": "error",
                "detail": "AI service temporarily unavailable"
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",  # Don't cache streaming responses
            "Connection": "keep-alive",  # Keep connection open
            "X-Accel-Buffering": "no"  # Tell reverse proxies not to buffer
        }
    )
