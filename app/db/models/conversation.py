from sqlalchemy import Column, String, Float, Enum as SqlEnum, ForeignKey, Table
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base
from app.models.conversation import ConversationType

# Association table for many-to-many relationship between conversations and users (members)
conversation_members = Table(
    "conversation_members",
    Base.metadata,
    Column("conversation_id", String, ForeignKey("conversations.id"), primary_key=True),
    Column("user_id", String, ForeignKey("users.id"), primary_key=True)
)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(Float, nullable=False)
    type = Column(SqlEnum(ConversationType), nullable=False, default=ConversationType.GROUP)

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_conversations")
    members = relationship("User", secondary=conversation_members, back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
