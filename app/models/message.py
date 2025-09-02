from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field

from app.models.user import User, UserResponse
from app.models.conversation import Conversation, ConversationResponse

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"

class MessageDeliveryStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    
@dataclass
class Message:
    id: str
    sender_id: str
    content: str
    type: MessageType = MessageType.TEXT
    status: MessageDeliveryStatus = MessageDeliveryStatus.PENDING
    conversation_id: str
    timestamp: float

    def to_dict(self):
       return {
           "id": self.id,
           "sender_id": self.sender_id,
           "content": self.content,
           "type": self.type,
           "status": self.status,
           "conversation_id": self.conversation_id,
           "timestamp": self.timestamp,
       }

class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=3, max_length=200, description="Message content")
    type: MessageType = MessageType.TEXT
    conversation_id: str
    
class MessageResponse(BaseModel):
    id: str
    sender: UserResponse
    content: str
    type: MessageType
    status: MessageDeliveryStatus
    conversation: ConversationResponse
    timestamp: float
