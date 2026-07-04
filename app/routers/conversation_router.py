from fastapi import APIRouter, Depends, status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import users,conversation
from app.services import auth_services, conversation_service
from app.schemas import conversation,user
from app.models import users
from app.schemas import conversation
from uuid import UUID
router=APIRouter(prefix="/conversations",tags=["Conversations"])
@router.post("/",response_model=conversation.ConversationResponse,status_code=201)
async def create_conversation(conv_data:conversation.ConversationCreate,current_user:users.User=Depends(auth_services.get_current_user),db:AsyncSession=Depends(get_db)):
    new_conversation=await conversation_service.create_conversation(db=db,user_id=current_user.id,title=conv_data.title)
    return new_conversation

@router.get("/",response_model=list[conversation.ConversationResponse])
async def get_all_conversation(current_user:users.User=Depends(auth_services.get_current_user),db:AsyncSession=Depends(get_db)):
    conversations=await conversation_service.get_conversation(db=db,user_id=current_user.id)
    return conversations

@router.get("/{conversation_id}", response_model=conversation.ConversationResponse)
async def get_conversation_byid(conversation_id:UUID, current_user:users.User=Depends(auth_services.get_current_user),db:AsyncSession=Depends(get_db)):
    conversation=await conversation_service.get_conversation_by_id(db=db,conversation_id=conversation_id,user_id=current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Conversation not found")
    return conversation

@router.put("/{conversation_id}",response_model=conversation.ConversationResponse)
async def rename(conversation_id:UUID,conversation_data:conversation.ConversationRename,
                 current_user:users.User=Depends(auth_services.get_current_user),db:AsyncSession=Depends(get_db)):
    updated_conversation = await conversation_service.rename_conversation(
        db=db,
        user_id=current_user.id,
        conversation_id=conversation_id,
        new_title=conversation_data.title
    )
    if not updated_conversation:
        raise HTTPException(...)
    return updated_conversation

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: users.User = Depends(auth_services.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    deleted = await conversation_service.delete_conversation(
        db=db,
        user_id=current_user.id,
        conversation_id=conversation_id
    )
    if not deleted:
        raise HTTPException(...)
    return None