from sqlalchemy import Column, String, Enum as SqlEnum
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base
from app.models.user import UserStatus

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    status = Column(SqlEnum(UserStatus), nullable=False, default=UserStatus.ONLINE)
    
    # Relationships
    created_conversations = relationship("Conversation", back_populates="creator", foreign_keys="[Conversation.creator_id]")
    conversations = relationship("Conversation", secondary="conversation_members", back_populates="members")
    messages = relationship("Message", back_populates="sender")