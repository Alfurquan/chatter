from app.models.message import MessageResponse
from app.services.message_service import MessageService
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import JSONResponse
import logging
from typing import List
import time

from app.error.error import APIException, ErrorCode
from ..models.conversation import CreateConversationRequest, ConversationResponse
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
        logger.info(f"Conversation creation request",
                    extra={
                        "username": current_user.username, 
                        "request_id": request.state.request_id
                    })

        conversation_service = request.app.state.conversation_service
        user_service = request.app.state.user_service
        
        if not user_service.get_user_by_id(current_user.id):
            raise APIException(
                code=ErrorCode.USER_NOT_FOUND,
                status_code=404,
                message="User not found", 
                details={"username": current_user.username}
            )
        
        conversation = conversation_service.create_conversation(
            conversation_request, current_user
        )
        
        return JSONResponse(
            status_code=201, 
            content=conversation_service.get_conversation_response(conversation.id).dict()
        )
    
    except Exception as e:
        logger.error(f"Error creating conversation: {e}",
                     extra={
                         "username": current_user.username, 
                         "request_id": request.state.request_id
                     })
        raise APIException(
            code=ErrorCode.CONVERSATION_CREATION_FAILED,
            status_code=500,
            message="Failed to create conversation",
            details={"error": str(e)}
        )
    
@router.get("/v1/conversations", response_model=List[ConversationResponse])
async def get_conversations(request: Request, current_user = Depends(get_current_user)):
    try:
        logger.info(f"Conversation fetch request",
                    extra={
                        "username": current_user.username, 
                        "request_id": request.state.request_id
                    })

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
        logger.error(f"Error fetching conversations: {e}",
                     extra={
                         "username": current_user.username,
                         "request_id": request.state.request_id
                     })
        raise APIException(
            code=ErrorCode.CONVERSATION_FETCH_FAILED,
            status_code=500,
            message="Failed to fetch conversations",
            details={"error": str(e)}
        )

@router.get("/v1/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    request: Request,
    conversation_id: str,
    limit: int = Query(50),
    before: float = Query(None),
    user = Depends(get_current_user)
):
    try:
        logger.info(f"Message fetch request for conversation {conversation_id}",
                    extra={
                        "username": user.username, 
                        "request_id": request.state.request_id,
                        "conversation_id": conversation_id,
                        "limit": limit,
                        "before": before
                    })
        
        message_service: MessageService = request.app.state.message_service
        messages = message_service.get_messages(conversation_id=conversation_id, limit=limit, before_timestamp=before)
        conversation_service = request.app.state.conversation_service

        if not conversation_service.check_if_user_has_access_to_conversation(user.id, conversation_id):
            logger.info(f"User {user.name} attempted to view messages in unauthorized conversation {conversation_id}")
            raise APIException(
                code=ErrorCode.UNAUTHORIZED_ACCESS,
                status_code=403,
                message="You do not have access to this conversation",
                details={"conversation_id": conversation_id}
            )

        responses: List[MessageResponse] = []
        for msg in messages:
            msg_response = message_service.create_message_response(
                msg, request.app.state.user_service, request.app.state.conversation_service
            )
            responses.append(msg_response)

        return responses

    except Exception as e:
        logger.error(f"Error fetching conversation messages: {e}", 
                     extra={
                         "username": user.username,
                         "conversation_id": conversation_id,
                         "request_id": request.state.request_id
                     })
        raise APIException(
            code=ErrorCode.MESSAGE_FETCH_FAILED,
            status_code=500,
            message="Failed to fetch messages",
            details={"error": str(e)}
        )