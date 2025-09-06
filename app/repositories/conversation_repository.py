from typing import List, Optional
from sqlalchemy.orm import Session
import time

from app.db.models.conversation import Conversation, conversation_members
from app.db.models.user import User
from app.models.conversation import CreateConversationRequest, ConversationType

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, request: CreateConversationRequest, creator_id: str) -> Conversation:
        """Create a new conversation"""
        # Determine conversation type based on number of members
        conversation_type = ConversationType.GROUP if len(request.member_ids) > 1 else ConversationType.ONE_ON_ONE
        
        # Create conversation
        db_conversation = Conversation(
            name=request.name,
            creator_id=creator_id,
            created_at=time.time(),
            type=conversation_type
        )
        
        self.db.add(db_conversation)
        self.db.flush()  # Flush to get the ID
        
        # Add creator and members to the conversation
        member_ids = set(request.member_ids)
        member_ids.add(creator_id)  # Ensure creator is also a member
        
        for member_id in member_ids:
            # Get the user object
            user = self.db.query(User).filter(User.id == member_id).first()
            if user:
                db_conversation.members.append(user)
        
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation
    
    def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        # This query gets conversations where the user is a member
        return (self.db.query(Conversation)
                .join(conversation_members)
                .filter(conversation_members.c.user_id == user_id)
                .all())
    
    def check_user_access(self, user_id: str, conversation_id: str) -> bool:
        """Check if a user has access to a conversation"""
        count = (self.db.query(conversation_members)
                .filter(conversation_members.c.conversation_id == conversation_id, 
                        conversation_members.c.user_id == user_id)
                .count())
        return count > 0
