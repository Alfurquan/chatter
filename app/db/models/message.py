from sqlalchemy import Column, Float, Enum as SqlEnum, ForeignKey, Text, String
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base
from app.models.message import MessageType, MessageDeliveryStatus

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(Float, nullable=False)
    type = Column(SqlEnum(MessageType), nullable=False, default=MessageType.TEXT)
    status = Column(SqlEnum(MessageDeliveryStatus), nullable=False, default=MessageDeliveryStatus.PENDING)

    # Relationships
    sender = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
