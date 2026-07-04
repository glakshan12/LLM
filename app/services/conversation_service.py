from sqlalchemy import select,desc #it is for order the results new-old
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from uuid import UUID

#for every function to written in fastapi there is three rule(anatomy of database function)
#who,where,what
#sql commands
#db execution
#instead of scalar or more if we use .first it returns none in silent user doesnt know about it.
async def create_conversation(db:AsyncSession, user_id:int,title:str):
    new_conv=Conversation(user_id=user_id,title=title)
    db.add(new_conv)#new conversation create in db
    await db.commit()
    await db.refresh(new_conv)
    return new_conv

#get all the conversation of user in order using desc
async def get_conversation(db:AsyncSession,user_id:int):
    result = await db.execute(
    select(Conversation).where(Conversation.user_id == user_id).order_by(desc(Conversation.created_at))
)
    return result.scalars().all()

#get the single conversation by its id
async def get_conversation_by_id(db: AsyncSession, user_id: UUID, conversation_id: UUID):
    """Get conversation by ID (verify user owns it)"""
    
    result = await db.execute(
        select(Conversation).where(
            (Conversation.user_id == user_id) & (Conversation.id == conversation_id)
        )
    )
    return result.scalar_one_or_none()

#rename conversation
async def rename_conversation(db:AsyncSession,user_id:int,conversation_id:int,new_title:str):
    #fetch the conversation
    conv=await get_conversation_by_id(db,user_id,conversation_id)
    if not conv:
        return None
    conv.title=new_title
    await db.commit()
    await db.refresh(conv)
    return conv

#delete conversation
async def delete_conversation(db:AsyncSession, user_id:int, conversation_id:int):
    conv=await get_conversation_by_id(db,user_id, conversation_id)
    if not conv:
        return False#tell the router it is failed
    await db.delete(conv)
    await db.commit()
    return True#tell the router it is worked