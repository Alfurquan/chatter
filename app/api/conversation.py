from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import logging
from ..models.conversation import CreateConversationRequest, ConversationResponse
from ..exception.user_exceptions import UserNotFoundException
from app.middleware.auth import get_current_user
from app.models.user import UserResponse

router = APIRouter()
logger = logging.getLogger("main.api.conversation")

@router.post("/v1/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: Request,
    conversation_request: CreateConversationRequest,
    current_user = Depends(get_current_user)
):
    try:
        conversation_service = request.app.state.conversation_service
        conversation = conversation_service.create_conversation(
            conversation_request, current_user.username
        )
        
        creator_dict = conversation.creator.dict() if hasattr(conversation.creator, 'dict') else vars(conversation.creator)
        
        members_list = []
        for member in conversation.members:
            member_dict = member.dict() if hasattr(member, 'dict') else vars(member)
            members_list.append(UserResponse(**member_dict))
        
        return JSONResponse(
            status_code=201, 
            content=ConversationResponse(
                id=conversation.id,
                name=conversation.name,
                creator=UserResponse(**creator_dict),
                created_at=conversation.created_at,
                members=members_list,
                type=conversation.type
            ).dict())
    
    except UserNotFoundException as e:
        logger.warning(f"User not found: {e}")
        return JSONResponse(status_code=404, content={"detail": str(e)})
    
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
