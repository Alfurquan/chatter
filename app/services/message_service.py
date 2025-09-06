from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db import get_db
from app.repositories.message_repository import MessageRepository
from app.models.message import Message, MessageCreateRequest, MessageDeliveryStatus, MessageResponse
from app.services.user_service import UserService
from app.services.conversation_service import ConversationService

class MessageService:
    def __init__(self, db: Session = Depends(get_db)):
        self.repo = MessageRepository(db)

    def add_message(self, message: Message):
        """
        Adds a message to conversation
        
        Args:
            message: Message to add.
        """
        # This method is not needed anymore as the repository handles persistence
        pass
    
    def get_messages(self, conversation_id: str, limit: int = 50, before_timestamp: float = None) -> List[Message]:
        """
        Get messages for a specific conversation.
        Args:
            conversation_id: The ID of the conversation
            limit: The maximum number of messages to return
            before_timestamp: Only return messages sent before this timestamp

        Returns
            List of messages
        """
        return self.repo.get_conversation_messages(conversation_id, limit, before_timestamp)

    def check_if_message_exists(self, conversation_id: str, message_id: str) -> bool:
        """
        Check if a message exists in a conversation.

        Args:
            conversation_id: The ID of the conversation
            message_id: The ID of the message to check

        Returns:
            True if the message exists, False otherwise
        """
        message = self.repo.get_by_id(message_id)
        return message is not None and str(message.conversation_id) == conversation_id
    
    def update_messages_status(
        self, 
        conversation_id: str, 
        message_ids: List[str],  
        before_timestamp: float,
        sender_id: str,
        status: MessageDeliveryStatus
    ) -> int:
        """
        Update status for multiple messages based on provided criteria.

        Args:
            conversation_id: The conversation to update messages in
            message_ids: Optional list of specific message IDs to update
            before_timestamp: Update all messages before this timestamp
            sender_id: Only update messages from this sender
            status: The new status to apply

        Returns:
            Number of messages that were updated
        """
        if message_ids:
            return self.repo.update_status(message_ids, status)
        else:
            return self.repo.update_status_by_criteria(conversation_id, before_timestamp, sender_id, status)
        
    def create_message(self, request: MessageCreateRequest, sender_id: str) -> Message:
        """
        Create a new message from the request.

        Args:
            request: The request containing the message data.
            sender_id: The ID of the user sending the message.

        Returns
            The created message
        """
        return self.repo.create(request, sender_id)

    def create_message_response(self, message: Message, user_service: UserService, conversation_service: ConversationService) -> MessageResponse:
        """
        Create a full MessageResponse object for a message.

        Args:
            message: The message object
            user_service: Service to look up user details
            conversation_service: Service to look up conversation details

        Returns:
            A MessageResponse object with all related data
        """
        return MessageResponse(
            id=str(message.id),
            sender=user_service.get_user_response(str(message.sender_id)),
            content=message.content,
            type=message.type,
            status=message.status,
            conversation=conversation_service.get_conversation_response(str(message.conversation_id)),
            timestamp=message.timestamp
        )