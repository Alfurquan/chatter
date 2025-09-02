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
    creator_id: str
    member_ids: List[str]
    created_at: float
    type: ConversationType

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "creator_id": self.creator_id,
            "member_ids": self.member_ids,
            "created_at": self.created_at,
            "type": self.type,
        }

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