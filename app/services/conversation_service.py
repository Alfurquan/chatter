from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db import get_db
from app.repositories.conversation_repository import ConversationRepository
from app.models.user import User, UserResponse
from app.services.user_service import UserService
from app.models.conversation import Conversation, ConversationType, CreateConversationRequest, ConversationResponse

class ConversationService:
    def __init__(self, user_service: UserService, db: Session = Depends(get_db)):
        self.repo = ConversationRepository(db)
        self.user_service = user_service
        
    def create_conversation(self, request: CreateConversationRequest, creator: User) -> Conversation:
        return self.repo.create(request, str(creator.id))

    def get_user_conversations(self, username: str) -> List[Conversation]:
        user = self.user_service.get_user(username)
        if not user:
            return []
        return self.repo.get_user_conversations(str(user.id))
        
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        return self.repo.get_by_id(conversation_id)

    def get_conversation_response(self, conversation_id: str) -> ConversationResponse:
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return None
            
        # Get creator user
        creator = self.user_service.get_user_by_id(str(conversation.creator_id))
        creator_response = UserResponse(
            id=str(creator.id),
            name=creator.name,
            username=creator.username,
            status=creator.status
        )
        
        # Get all members
        member_responses = []
        for member in conversation.members:
            member_responses.append(UserResponse(
                id=str(member.id),
                name=member.name,
                username=member.username,
                status=member.status
            ))
        
        return ConversationResponse(
            id=str(conversation.id),
            name=conversation.name,
            creator=creator_response,
            created_at=conversation.created_at,
            members=member_responses,
            type=conversation.type
        )
        
    def check_if_user_has_access_to_conversation(self, user_id: str, conversation_id: str) -> bool:
        return self.repo.check_user_access(user_id, conversation_id)
