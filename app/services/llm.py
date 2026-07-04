import asyncio
import httpx
import traceback
from app.config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import message as message_model
from uuid import UUID
from typing import AsyncGenerator
from .conversation_service import get_conversation
import json


#get the previous messages from this conversation.
async def get_conversation_history(
    db: AsyncSession, 
    conversation_id: UUID, 
    limit: int = 10 #limit(10 previous messages) get as list in oldest to newest
) -> list:
    stmt = (
        select(message_model.Message)
        .where(message_model.Message.conversation_id == conversation_id)
        .order_by(message_model.Message.created_at)
        .limit(limit)
    )
     #Execute the query
    result = await db.execute(stmt)
    
    #Get all results as list
    messages = result.scalars().all()
    
    return messages
#-----------------------------------------------#

#Token count of gemini

async def count_tokens(text: str) -> int:
    try:
        token_count = len(text) // 4
        return max(1, token_count)
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return len(text) // 4
#--------------------------------------------------#    

#save message to database

async def save_message(
    db: AsyncSession,#args
    conversation_id: UUID,
    role: str,
    content: str,
    token_count: int = 0
) -> message_model.Message:
    new_message = message_model.Message(#create the new message object from sqlalchemy with parameters
        conversation_id=conversation_id,
        role=role,
        content=content,
        token_count=token_count
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)#refresh to get auto generated id
    return new_message
#--------------------------------------------------------#

#message as full conversation
async def call_api_non_streaming(
    db: AsyncSession,
    conversation_id: UUID,
    user_message: str,
) -> message_model.Message:
    try:
        print(f"starting the non-streaing call")
    #step 1 : call the function 1
    #get conv history, format to nvidia api, save response to database, and return save message to object
        history = await get_conversation_history(db, conversation_id,limit=10)

        messages = []#build the message in nvidia format
   
        for msg in history:#this will loop throught the each message in history and convert into format
            role="assistant" if msg.role=="assistant" else "user"
            messages.append({#this will get the previous message from conversation
            "role": role,
            "content": msg.content #for text in gemini text is required, for images images
            })#gemini requires parts list
    
    #current messages
        messages.append({#this will store the current user message
            "role": "user",
            "content": user_message
    })
        print(f" Messages sent: {len(messages)}total")
        print(f"first message:{messages[0] if messages else 'empty'}")  
    
    #call nvidia api
    
        async with httpx.AsyncClient() as client:
            print("client sending request")
            response=await client.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",#nvidia server address
                 headers={
                     "Authorization":f"Bearer {settings.NVIDIA_API}",
                     "Content-Type":"application/json"
                 },
                 json={
                     "model": settings.NVIDIA_MODEL,
                     "messages":messages,
                     "max_tokens":1024,
                     "temperature":0.7
                 },
                 timeout=30.0
            )
            print(f"Got response, status {response.status_code}")
            if response.status_code!=200:
                print(f"error is {response.status_code}")
                print(f"error response:{response.text}")
                raise Exception (f"api returned {response.status_code}:{response.text}")
            response_data=response.json()
            print(f"parsed json :{response_data.keys()}")
            ai_response_text=response_data["choices"][0]["message"]["content"]
            print(f"got response:{ai_response_text[:100]}")
        token_count=await count_tokens(ai_response_text)
        print(f"counted tokens:{token_count}")
        # Save message
        ai_message = await save_message(
            db, conversation_id, "assistant", ai_response_text, token_count
        )
        print(f"✅ Saved message: {ai_message.id}")
        
        return ai_message

    except Exception as e:
        print(f"❌ EXCEPTION TYPE: {type(e).__name__}")
        print(f"❌ EXCEPTION MESSAGE: {str(e)}")
        import traceback
        print(f"❌ TRACEBACK:\n{traceback.format_exc()}")
        raise
#----------------------------------------------------------------#

#this will return the response as chunk(stream, one by one)
async def call_api_streaming(
    db: AsyncSession,
    conversation_id: UUID,
    user_message: str
)-> AsyncGenerator[str, None]:
    
    #get previous message
    history = await get_conversation_history(db, conversation_id,limit=10)

    #build message list
    messages = []

    for msg in history:
        role="assistant" if msg.role=="assistant" else "user"
        messages.append({
            "role": role,
            "content":msg.content
        })
    messages.append({"role": "user", "content":user_message})#current message
    print(f"streaming request :{len(messages)}")

    complete_response=""#add chunk messages here
    try:
        async with httpx.AsyncClient() as client:#this is for talk with nvidia server, create http request 
            response=await client.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.NVIDIA_API}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.NVIDIA_MODEL,
                    "messages": messages,
                    "max_tokens": 1024,
                    "temperature": 0.7,
                    "stream": True  # ← ENABLE STREAMING
                },
                timeout=30.0
            )
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data_str=line[6:].strip()
                    if data_str==["Done"]:
                        break
                    try:
                        data=json.loads(data_str)
                        chunk = data["choices"][0]["delta"].get("content", "")
                        
                        if chunk:
                            complete_response += chunk
                            yield chunk  # Send to client immediately 
                    except json.JSONDecodeError:
                        continue
            print(f" Streaming complete: {len(complete_response)} chars") 
    except Exception as e:
        # If error occurs, yield error message
        print(f"Error streaming : {e}")
        yield f"Error: {str(e)}"
        raise
    if complete_response:
        token_count=await count_tokens(complete_response )
        await save_message(
            db,conversation_id,"assistant",complete_response,token_count)