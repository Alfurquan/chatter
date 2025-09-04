from app.models.message import MessageResponse
from app.services.message_service import MessageService
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import logging
from typing import List
import time

from ..models.conversation import CreateConversationRequest, ConversationResponse
from ..exception.user_exceptions import UserNotFoundException
from app.middleware.auth import get_current_user

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
        
        return JSONResponse(
            status_code=201, 
            content=conversation_service.get_conversation_response(conversation.id).dict()
        )

    except UserNotFoundException as e:
        logger.warning(f"User not found: {e}")
        return JSONResponse(status_code=404, content={"detail": str(e)})
    
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    
@router.get("/v1/conversations", response_model=List[ConversationResponse])
async def get_conversations(request: Request, current_user = Depends(get_current_user)):
    try:
        conversation_service = request.app.state.conversation_service
        conversations = conversation_service.get_user_conversations(current_user.username)
        
        conversation_reponses = [
            conversation_service.get_conversation_response(conv.id).dict() for conv in conversations
        ]
        
        return JSONResponse(
            status_code=200,
            content=conversation_reponses
        )

    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@router.get("/v1/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    request: Request,
    conversation_id: str,
    user_id = Depends(get_current_user)
):
    try:
        message_service: MessageService = request.app.state.message_service
        messages = message_service.get_messages(conversation_id, before_timestamp=time.time())
        conversation_service = request.app.state.conversation_service
        
        if not conversation_service.check_if_user_has_access_to_conversation(user_id, conversation_id):
            logger.info(f"User {user_id} attempted to send message to unauthorized conversation {conversation_id}")
            return JSONResponse(status_code=403, content={"detail": "Unauthorized access to conversation"})

        responses: List[MessageResponse] = []
        for msg in messages:
            msg_response = message_service.create_message_response(
                msg, request.app.state.user_service, request.app.state.conversation_service
            )
            responses.append(msg_response)

        return responses

    except Exception as e:
        logger.error(f"Error fetching conversation messages: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})