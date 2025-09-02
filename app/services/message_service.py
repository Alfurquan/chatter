from typing import Dict, List
from threading import Lock
from app.models.message import Message, MessageType, MessageDeliveryStatus


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
