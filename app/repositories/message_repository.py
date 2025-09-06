from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import time

from app.db.models.message import Message
from app.models.message import MessageCreateRequest, MessageDeliveryStatus, MessageType

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, request: MessageCreateRequest, sender_id: str) -> Message:
        """Create a new message"""
        db_message = Message(
            sender_id=sender_id,
            conversation_id=request.conversation_id,
            content=request.content,
            timestamp=time.time(),
            type=request.type or MessageType.TEXT,
            status=MessageDeliveryStatus.PENDING
        )
        
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
    
    def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get a message by ID"""
        return self.db.query(Message).filter(Message.id == message_id).first()
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50, before_timestamp: Optional[float] = None) -> List[Message]:
        """Get messages for a conversation with optional pagination"""
        query = self.db.query(Message).filter(Message.conversation_id == conversation_id)
        
        if before_timestamp:
            query = query.filter(Message.timestamp < before_timestamp)
        
        return query.order_by(desc(Message.timestamp)).limit(limit).all()
    
    def update_status(self, message_ids: List[str], status: MessageDeliveryStatus) -> int:
        """Update status for multiple messages"""
        result = self.db.query(Message).filter(Message.id.in_(message_ids)).update(
            {Message.status: status}, 
            synchronize_session=False
        )
        self.db.commit()
        return result
    
    def update_status_by_criteria(self, conversation_id: str, before_timestamp: Optional[float], sender_id: Optional[str], status: MessageDeliveryStatus) -> int:
        """Update status for messages matching criteria"""
        query = self.db.query(Message).filter(Message.conversation_id == conversation_id)
        
        if before_timestamp:
            query = query.filter(Message.timestamp < before_timestamp)
            
        if sender_id:
            query = query.filter(Message.sender_id == sender_id)
            
        result = query.update({Message.status: status}, synchronize_session=False)
        self.db.commit()
        return result
