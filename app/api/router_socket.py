"""
WebSocket router for real-time chat communication in ChatFastAPI.

This module handles WebSocket connections for real-time messaging:
- Connection management for multiple chat rooms
- Message broadcasting to all room participants
- User connection/disconnection handling
- Structured message format using Pydantic schemas

The ConnectionManager class maintains active WebSocket connections organized
by room_id and user_id, enabling efficient message broadcasting and cleanup.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.params import Query

from app.api.schemas import ChatMessage

router: APIRouter = APIRouter(prefix="/ws/chat")


class ConnectionManager:
    """
    Manages WebSocket connections for real-time chat functionality.
    
    This class handles the lifecycle of WebSocket connections:
    - Connection establishment and storage
    - Message broadcasting to room participants
    - Connection cleanup on disconnect
    - Room management (auto-cleanup of empty rooms)
    
    The connection storage structure:
    active_connections[room_id][user_id] = WebSocket
    This allows efficient lookup and broadcasting by room.
    """
    
    def __init__(self) -> None:
        """
        Initialize the connection manager.
        
        Creates an empty dictionary to store active WebSocket connections.
        The structure is: {room_id: {user_id: WebSocket}}
        """
        # Active connection storage as dict {room_id: {user_id: WebSocket}}
        self.active_connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int) -> None:
        """
        Establish a WebSocket connection for a user in a specific room.
        
        This method:
        1. Accepts the WebSocket connection
        2. Creates room entry if it doesn't exist
        3. Stores the connection for future message broadcasting
        
        Args:
            websocket: The WebSocket connection to establish
            room_id: Unique identifier for the chat room
            user_id: Unique identifier for the user
        """
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket

    async def disconnect(self, room_id: int, user_id: int) -> None:
        """
        Remove a user's WebSocket connection and clean up empty rooms.
        
        This method:
        1. Removes the user's connection from the room
        2. Deletes the room if no users remain
        3. Prevents memory leaks from abandoned rooms
        
        Args:
            room_id: Unique identifier for the chat room
            user_id: Unique identifier for the user to disconnect
        """
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            del self.active_connections[room_id][user_id]
            # Clean up empty rooms to prevent memory leaks
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: str, room_id: int, sender_id: int) -> None:
        """
        Send a message to all users in a specific room.
        
        This method:
        1. Iterates through all connections in the room
        2. Creates a structured ChatMessage for each recipient
        3. Sets the is_self flag based on whether the recipient is the sender
        4. Sends the message as JSON to each WebSocket connection
        
        Args:
            message: The text content to broadcast
            room_id: Unique identifier for the target room
            sender_id: Unique identifier for the message sender
        """
        if room_id in self.active_connections:
            for user_id, connection in self.active_connections[room_id].items():
                # Create structured message with sender identification
                chat_message = ChatMessage(
                    text=message,
                    is_self=user_id == sender_id
                )
                # Send JSON-formatted message to the WebSocket connection
                await connection.send_json(chat_message.model_dump())


# Global connection manager instance for WebSocket handling
manager: ConnectionManager = ConnectionManager()


@router.websocket("/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, user_id: int, username: str = Query()) -> None:
    """
    WebSocket endpoint for real-time chat communication.
    
    This endpoint handles the complete WebSocket lifecycle:
    1. Establishes connection and notifies room of new user
    2. Listens for incoming messages from the client
    3. Broadcasts messages to all room participants
    4. Handles disconnection and cleanup
    
    The WebSocket connection remains open until the client disconnects,
    enabling real-time bidirectional communication.
    
    Args:
        websocket: The WebSocket connection
        room_id: Unique identifier for the chat room
        user_id: Unique identifier for the user
        username: Display name for the user (from query parameter)
    """
    # Establish the connection and notify room participants
    await manager.connect(websocket, room_id, user_id)
    await manager.broadcast(f"{username} (ID: {user_id}) connected to the chat.", room_id, user_id)

    try:
        # Main message loop - continues until client disconnects
        while True:
            # Receive text message from the client
            data = await websocket.receive_text()
            # Broadcast the message to all room participants
            await manager.broadcast(f"{username} (ID: {user_id}): {data}", room_id, user_id)
    except WebSocketDisconnect:
        # Handle client disconnection gracefully
        await manager.disconnect(room_id, user_id)
        await manager.broadcast(f"{username} (ID: {user_id}) disconnected from chat.", room_id, user_id)
