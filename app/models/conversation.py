from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import List
from enum import Enum

from app.models.user import User, UserResponse

class ConversationType(str, Enum):
    GROUP = "group"
    ONE_ON_ONE = "one_on_one"

@dataclass
class Conversation:
    id: str
    name: str
    creator: User
    members: List[User]
    created_at: float
    type: ConversationType
    
class CreateConversationRequest(BaseModel):
    name: str
    member_ids: List[str] = Field(default_factory=list)

class ConversationResponse(BaseModel):
    id: str
    name: str
    creator: UserResponse
    members: List[UserResponse]
    created_at: float
    type: ConversationType