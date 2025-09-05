from typing import Dict, List
from threading import Lock
import time
import uuid

from app.models.message import Message, MessageCreateRequest, MessageDeliveryStatus, MessageResponse
from app.models.user import UserResponse
from app.services.user_service import UserService
from app.services.conversation_service import ConversationService

class MessageService:
    def __init__(self):
        self.messages: Dict[str, List[Message]] = {}
        self.lock = Lock()

    def add_message(self, message: Message):
        """
        Adds a message to conversation
        
        Args:
            message: Message to add.
        """
        with self.lock:
            if message.conversation_id not in self.messages:
                self.messages[message.conversation_id] = []
            self.messages[message.conversation_id].append(message)
    
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
        with self.lock:
            messages = self.messages.get(conversation_id, [])

            if not messages or before_timestamp is None:
                return sorted(messages, key=lambda msg: msg.timestamp, reverse=True)[:limit]

            sorted_messages = sorted(messages, key=lambda msg: msg.timestamp, reverse=True)

            filtered_messages = []
            for msg in sorted_messages:
                if msg.timestamp < before_timestamp:
                    filtered_messages.append(msg)
                    if len(filtered_messages) >= limit:
                        break

            return filtered_messages

    def check_if_message_exists(self, conversation_id: str, message_id: str) -> bool:
        """
        Check if a message exists in a conversation.

        Args:
            conversation_id: The ID of the conversation
            message_id: The ID of the message to check

        Returns:
            True if the message exists, False otherwise
        """
        
        with self.lock:
            messages = self.messages.get(conversation_id, [])
            for message in messages:
                if message.id == message_id:
                    return True
            return False
        
    
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
        with self.lock:
            messages = self.messages.get(conversation_id, [])
            updated_count = 0

            for message in messages:
                if message_ids is not None and message.id not in message_ids:
                    continue

                if before_timestamp is not None and message.timestamp >= before_timestamp:
                    continue

                if sender_id is not None and message.sender_id != sender_id:
                    continue
                
                if message.status != status:
                    message.status = status
                    updated_count += 1

            return updated_count
        
    def create_message(self, request: MessageCreateRequest, sender_id: str) -> Message:
        """
        Create a new message from the request.

        Args:
            request: The request containing the message data.
            sender_id: The ID of the user sending the message.

        Returns
            The created message
        """
        message = Message(
            id=str(uuid.uuid4()),
            content=request.content,
            sender_id=sender_id,
            conversation_id=request.conversation_id,
            timestamp=time.time(),
            status=MessageDeliveryStatus.PENDING
        )
        self.add_message(message)
        return message

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
            id=message.id,
            sender=user_service.get_user_response(message.sender_id),
            content=message.content,
            type=message.type,
            status=message.status,
            conversation=conversation_service.get_conversation_response(message.conversation_id),
            timestamp=message.timestamp
        )