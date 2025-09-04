from fastapi import APIRouter, WebSocket, Query, WebSocketDisconnect
import logging
import json

from app.security.jwt_handler import decode_access_token
from app.models.message import MessageCreateRequest

router = APIRouter()
logger = logging.getLogger("main.websocket.routes")

async def get_user_id_from_token(token: str) -> str:
    payload = decode_access_token(token)
    logger.info(f"WebSocket connection attempt with token payload: {payload}")
    
    if not payload or "sub" not in payload:
        return None
    
    return payload["sub"]

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str, token: str = Query(None)):
    user_id = await get_user_id_from_token(token)
    message_service = websocket.app.state.message_service
    manager = websocket.app.state.connection_manager
    conversation_service = websocket.app.state.conversation_service

    if not user_id:
        return

    logger.info(f"User {user_id} connected to conversation {conversation_id}")
    await manager.connect(conversation_id, user_id, websocket)
    try:
        while True:
            data_json = json.loads(await websocket.receive_text())
            data_json["conversation_id"] = conversation_id
            message_request = MessageCreateRequest(**data_json)
            message = message_service.create_message(message_request, user_id)
            
            if not conversation_service.check_if_user_has_access_to_conversation(user_id, conversation_id):
                logger.info(f"User {user_id} attempted to send message to unauthorized conversation {conversation_id}")
                await websocket.send_json({"error": "Unauthorized access to conversation"})
                continue

            logger.info(f"User {user_id} sent a message in conversation {conversation_id}: {message.content}")
            message_response = message_service.create_message_response(message, websocket.app.state.user_service, conversation_service)
            await manager.broadcast(conversation_id, message_response.dict())

    except Exception as e:
        logger.error(f"Error occurred for user {user_id} in conversation {conversation_id}: {str(e)}")
        await websocket.send_json({"error": str(e)})
    
    except WebSocketDisconnect:
        logger.error(f"User {user_id} disconnected from conversation {conversation_id}")
        manager.disconnect(conversation_id, user_id)