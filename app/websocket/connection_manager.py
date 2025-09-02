from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    """
    A class to manage WebSocket connections for different conversations.
    """
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        
    async def connect(self, conversation_id: str, user_id: str, websocket: WebSocket):
        """
        Add a new WebSocket connection to the manager.
        @param conversation_id: The ID of the conversation.
        @param user_id: The ID of the user.
        @param websocket: The WebSocket connection to add.
        
        """
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = {}
        self.active_connections[conversation_id][user_id] = websocket

    def disconnect(self, conversation_id: str, user_id: str):
        """
        Remove a WebSocket connection from the manager.
        @param conversation_id: The ID of the conversation.
        @param user_id: The ID of the user.
        """
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].pop(user_id, None)

    async def broadcast(self, conversation_id: str, message: str):
        """
        Send a message to all WebSocket connections in a conversation.
        @param conversation_id: The ID of the conversation.
        @param message: The message to send.
        """
        if conversation_id in self.active_connections:
            for user_id, websocket in self.active_connections[conversation_id].items():
                await websocket.send_text(message)
