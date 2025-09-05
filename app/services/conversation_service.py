from typing import Dict, List
import uuid
import time

from app.models.user import User, UserResponse
from app.services.user_service import UserService
from app.models.conversation import Conversation, ConversationType, CreateConversationRequest, ConversationResponse

class ConversationService:
    def __init__(self, user_service: UserService):
        self.conversations: Dict[str, Conversation] = {}
        self.user_service = user_service
        
    def create_conversation(self, request: CreateConversationRequest, creator: User) -> Conversation:
        conversation_id = str(uuid.uuid4())
            
        conversation = Conversation(
            id=conversation_id,
            name=request.name,
            member_ids=request.member_ids + [creator.id],
            created_at=time.time(),
            creator_id=creator.id,
            type=ConversationType.GROUP if len(request.member_ids) > 1 else ConversationType.ONE_ON_ONE,
        )
        
        self.conversations[conversation_id] = conversation
        return conversation

    def get_user_conversations(self, username: str) -> List[Conversation]:
        user = self.user_service.get_user(username)
        return [
            conv for conv in self.conversations.values() 
                if conv.creator_id == user.id or 
                user.id in [member_id for member_id in conv.member_ids]
            ]
        
    def get_conversation_by_id(self, conversation_id: str) -> Conversation | None:
        return self.conversations.get(conversation_id)

    def get_conversation_response(self, conversation_id: str) -> ConversationResponse:
        conversation = self.get_conversation_by_id(conversation_id)
        creator_dict = self.user_service.get_user_by_id(conversation.creator_id).to_dict()
        
        members_list = [self.user_service.get_user_by_id(member_id).to_dict() for member_id in conversation.member_ids]
        
        return ConversationResponse(
            id=conversation.id,
            name=conversation.name,
            creator=UserResponse(**creator_dict),
            created_at=conversation.created_at,
            members=[UserResponse(**member_dict) for member_dict in members_list],
            type=conversation.type
        )
        
    def check_if_user_has_access_to_conversation(self, user_id: str, conversation_id: str) -> bool:
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return False
        return conversation.creator_id == user_id or user_id in conversation.member_ids
