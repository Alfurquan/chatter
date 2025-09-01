from typing import Dict, List
import uuid
import time

from app.models.user import User
from app.services.user_service import UserService
from app.models.conversation import Conversation, ConversationType, CreateConversationRequest
from app.exception.user_exceptions import UserNotFoundException

class ConversationService:
    def __init__(self, user_service: UserService):
        self.conversations: Dict[str, Conversation] = {}
        self.user_service = user_service
        
    def create_conversation(self, request: CreateConversationRequest, creator_username: str) -> Conversation:
        conversation_id = str(uuid.uuid4())
        creator = self.user_service.get_user(creator_username)
        if not creator:
            raise UserNotFoundException("Creator not found")

        members: List[User] = []
        for member_ids in request.member_ids:
            user = self.user_service.users.get(member_ids)
            if not user:
               raise UserNotFoundException(f"User not found for id: {member_ids}")
            members.append(user)

        conversation = Conversation(
            id=conversation_id,
            name=request.name,
            members=members,
            created_at=time.time(),
            creator=creator,
            type=ConversationType.GROUP if len(members) > 1 else ConversationType.ONE_ON_ONE,
        )
        
        self.conversations[conversation_id] = conversation
        return conversation

    def get_user_conversations(self, username: str) -> List[Conversation]:
        return [
            conv for conv in self.conversations.values() 
                if conv.creator.username == username or 
                username in [member.username for member in conv.members]
            ]
