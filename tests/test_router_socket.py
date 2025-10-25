"""
Unit tests for router_socket.py ConnectionManager functionality.

This module contains comprehensive unit tests for the ConnectionManager class,
covering all methods and edge cases. Tests are organized by functionality:
- Initialization tests
- Connection management tests  
- Disconnection and cleanup tests
- Message broadcasting tests

All tests use proper async/await patterns, type annotations, and follow
the AAA (Arrange, Act, Assert) testing pattern with detailed documentation.
"""

import pytest
from unittest.mock import AsyncMock

from app.api.router_socket import ConnectionManager
from app.api.schemas import ChatMessage


class TestConnectionManagerInitialization:
    """Test cases for ConnectionManager initialization and basic state."""
    
    def test_connection_manager_init(self, connection_manager: ConnectionManager) -> None:
        """
        Test that ConnectionManager initializes with empty connections.
        
        This test verifies that a new ConnectionManager instance starts with
        an empty active_connections dictionary, ensuring clean state for
        connection management.
        
        Args:
            connection_manager: Fresh ConnectionManager instance from fixture
        """
        # Arrange: ConnectionManager is created by fixture
        
        # Act: Check initial state (no action needed - testing initial state)
        
        # Assert: Verify empty initial state
        assert isinstance(connection_manager.active_connections, dict)
        assert len(connection_manager.active_connections) == 0
        assert connection_manager.active_connections == {}


class TestConnectionManagerConnect:
    """Test cases for ConnectionManager.connect() method."""
    
    @pytest.mark.asyncio
    async def test_connect_new_room(
        self,
        connection_manager: ConnectionManager,
        mock_websocket: AsyncMock,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test connecting a user to a new room.
        
        This test verifies that:
        - WebSocket accept() is called
        - New room is created in active_connections
        - User is added to the room
        - Connection is stored correctly
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket: Mocked WebSocket connection
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Extract test data
        room_id = sample_room_data["room_id"]
        user_id = sample_room_data["user_id"]
        
        # Act: Connect user to room
        await connection_manager.connect(mock_websocket, room_id, user_id)
        
        # Assert: Verify connection is established
        assert room_id in connection_manager.active_connections, "Room should be created"
        assert user_id in connection_manager.active_connections[room_id], "User should be in room"
        assert connection_manager.active_connections[room_id][user_id] == mock_websocket, "WebSocket should be stored"
        mock_websocket.accept.assert_called_once(), "WebSocket accept() should be called"
    
    @pytest.mark.asyncio
    async def test_connect_existing_room(
        self,
        connection_manager: ConnectionManager,
        mock_websocket_factory,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test connecting a second user to an existing room.
        
        This test verifies that multiple users can be added to the same room
        without affecting existing connections.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket_factory: Factory for creating mock WebSockets
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Setup first user and room
        room_id = sample_room_data["room_id"]
        user_id_1 = sample_room_data["user_id"]
        user_id_2 = 200  # Second user
        websocket_1 = mock_websocket_factory()
        websocket_2 = mock_websocket_factory()
        
        # Act: Connect first user, then second user to same room
        await connection_manager.connect(websocket_1, room_id, user_id_1)
        await connection_manager.connect(websocket_2, room_id, user_id_2)
        
        # Assert: Verify both users are in the same room
        assert room_id in connection_manager.active_connections, "Room should exist"
        assert len(connection_manager.active_connections[room_id]) == 2, "Room should have 2 users"
        assert user_id_1 in connection_manager.active_connections[room_id], "First user should be in room"
        assert user_id_2 in connection_manager.active_connections[room_id], "Second user should be in room"
        assert connection_manager.active_connections[room_id][user_id_1] == websocket_1, "First WebSocket should be stored"
        assert connection_manager.active_connections[room_id][user_id_2] == websocket_2, "Second WebSocket should be stored"
    
    @pytest.mark.asyncio
    async def test_connect_websocket_accept_called(
        self,
        connection_manager: ConnectionManager,
        mock_websocket: AsyncMock,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test that WebSocket accept() is called during connection.
        
        This test specifically verifies that the WebSocket accept() method
        is called exactly once during the connection process.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket: Mocked WebSocket connection
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Extract test data
        room_id = sample_room_data["room_id"]
        user_id = sample_room_data["user_id"]
        
        # Act: Connect user to room
        await connection_manager.connect(mock_websocket, room_id, user_id)
        
        # Assert: Verify accept() was called
        mock_websocket.accept.assert_called_once(), "WebSocket accept() should be called exactly once"
        assert mock_websocket.accept.call_count == 1, "Accept should be called only once"


class TestConnectionManagerDisconnect:
    """Test cases for ConnectionManager.disconnect() method."""
    
    @pytest.mark.asyncio
    async def test_disconnect_single_user(
        self,
        connection_manager: ConnectionManager,
        mock_websocket: AsyncMock,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test disconnecting a single user from a room.
        
        This test verifies that a user can be disconnected from a room
        and the connection is properly removed.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket: Mocked WebSocket connection
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Connect user first
        room_id = sample_room_data["room_id"]
        user_id = sample_room_data["user_id"]
        await connection_manager.connect(mock_websocket, room_id, user_id)
        
        # Act: Disconnect user
        await connection_manager.disconnect(room_id, user_id)
        
        # Assert: Verify user is removed
        assert room_id not in connection_manager.active_connections, "Room should be removed when empty"
    
    @pytest.mark.asyncio
    async def test_disconnect_empty_room_cleanup(
        self,
        connection_manager: ConnectionManager,
        mock_websocket: AsyncMock,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test that empty rooms are automatically cleaned up.
        
        This test verifies that when the last user disconnects from a room,
        the room itself is removed from active_connections to prevent
        memory leaks.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket: Mocked WebSocket connection
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Connect user to room
        room_id = sample_room_data["room_id"]
        user_id = sample_room_data["user_id"]
        await connection_manager.connect(mock_websocket, room_id, user_id)
        
        # Act: Disconnect the only user
        await connection_manager.disconnect(room_id, user_id)
        
        # Assert: Verify room is completely removed
        assert room_id not in connection_manager.active_connections, "Empty room should be removed"
        assert len(connection_manager.active_connections) == 0, "No rooms should remain"
    
    @pytest.mark.asyncio
    async def test_disconnect_keep_room_with_users(
        self,
        connection_manager: ConnectionManager,
        mock_websocket_factory,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test that room remains when other users are still connected.
        
        This test verifies that disconnecting one user from a room with
        multiple users doesn't remove the entire room.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket_factory: Factory for creating mock WebSockets
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Connect two users to same room
        room_id = sample_room_data["room_id"]
        user_id_1 = sample_room_data["user_id"]
        user_id_2 = 200
        websocket_1 = mock_websocket_factory()
        websocket_2 = mock_websocket_factory()
        
        await connection_manager.connect(websocket_1, room_id, user_id_1)
        await connection_manager.connect(websocket_2, room_id, user_id_2)
        
        # Act: Disconnect first user
        await connection_manager.disconnect(room_id, user_id_1)
        
        # Assert: Verify room still exists with remaining user
        assert room_id in connection_manager.active_connections, "Room should still exist"
        assert user_id_2 in connection_manager.active_connections[room_id], "Second user should still be in room"
        assert user_id_1 not in connection_manager.active_connections[room_id], "First user should be removed"
        assert len(connection_manager.active_connections[room_id]) == 1, "Room should have 1 remaining user"
    
    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_user(
        self,
        connection_manager: ConnectionManager,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test disconnecting a user that doesn't exist (should not raise error).
        
        This test verifies that disconnecting a non-existent user doesn't
        cause an error and doesn't affect existing connections.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: No connections exist
        room_id = sample_room_data["room_id"]
        user_id = sample_room_data["user_id"]
        
        # Act & Assert: Disconnect non-existent user should not raise error
        await connection_manager.disconnect(room_id, user_id)  # Should not raise exception
        
        # Verify no connections exist (unchanged)
        assert len(connection_manager.active_connections) == 0, "No connections should exist"
    
    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_room(
        self,
        connection_manager: ConnectionManager,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test disconnecting from a room that doesn't exist (should not raise error).
        
        This test verifies that disconnecting from a non-existent room doesn't
        cause an error and doesn't affect the connection manager state.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: No rooms exist
        non_existent_room = 999
        user_id = sample_room_data["user_id"]
        
        # Act & Assert: Disconnect from non-existent room should not raise error
        await connection_manager.disconnect(non_existent_room, user_id)  # Should not raise exception
        
        # Verify no connections exist (unchanged)
        assert len(connection_manager.active_connections) == 0, "No connections should exist"


class TestConnectionManagerBroadcast:
    """Test cases for ConnectionManager.broadcast() method."""
    
    @pytest.mark.asyncio
    async def test_broadcast_single_user(
        self,
        connection_manager: ConnectionManager,
        mock_websocket: AsyncMock,
        sample_room_data: dict[str, int | str],
        sample_message_data: dict[str, str | int | bool]
    ) -> None:
        """
        Test broadcasting a message to a single user in a room.
        
        This test verifies that:
        - Message is sent to the user
        - ChatMessage is properly structured
        - is_self flag is set correctly for the sender
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket: Mocked WebSocket connection
            sample_room_data: Test data with room_id and user_id
            sample_message_data: Test message data
        """
        # Arrange: Connect user and prepare message
        room_id = sample_room_data["room_id"]
        user_id = sample_room_data["user_id"]
        message_text = sample_message_data["text"]
        sender_id = sample_message_data["sender_id"]
        
        await connection_manager.connect(mock_websocket, room_id, user_id)
        
        # Act: Broadcast message
        await connection_manager.broadcast(message_text, room_id, sender_id)
        
        # Assert: Verify message was sent
        mock_websocket.send_json.assert_called_once(), "Message should be sent to user"
        
        # Verify the message structure
        call_args = mock_websocket.send_json.call_args[0][0]  # Get the first argument
        assert call_args["text"] == message_text, "Message text should match"
        assert call_args["is_self"] == (user_id == sender_id), "is_self should be True for sender"
    
    @pytest.mark.asyncio
    async def test_broadcast_multiple_users(
        self,
        connection_manager: ConnectionManager,
        mock_websocket_factory,
        sample_room_data: dict[str, int | str],
        sample_message_data: dict[str, str | int | bool]
    ) -> None:
        """
        Test broadcasting a message to multiple users in the same room.
        
        This test verifies that:
        - Message is sent to all users in the room
        - Each user receives the message
        - is_self flag is set correctly for each recipient
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket_factory: Factory for creating mock WebSockets
            sample_room_data: Test data with room_id and user_id
            sample_message_data: Test message data
        """
        # Arrange: Connect multiple users to same room
        room_id = sample_room_data["room_id"]
        user_id_1 = sample_room_data["user_id"]
        user_id_2 = 200
        user_id_3 = 300
        sender_id = user_id_1  # First user is the sender
        
        websocket_1 = mock_websocket_factory()
        websocket_2 = mock_websocket_factory()
        websocket_3 = mock_websocket_factory()
        
        await connection_manager.connect(websocket_1, room_id, user_id_1)
        await connection_manager.connect(websocket_2, room_id, user_id_2)
        await connection_manager.connect(websocket_3, room_id, user_id_3)
        
        message_text = sample_message_data["text"]
        
        # Act: Broadcast message
        await connection_manager.broadcast(message_text, room_id, sender_id)
        
        # Assert: Verify all users received the message
        websocket_1.send_json.assert_called_once(), "Sender should receive message"
        websocket_2.send_json.assert_called_once(), "User 2 should receive message"
        websocket_3.send_json.assert_called_once(), "User 3 should receive message"
        
        # Verify is_self flag for each user
        call_1 = websocket_1.send_json.call_args[0][0]
        call_2 = websocket_2.send_json.call_args[0][0]
        call_3 = websocket_3.send_json.call_args[0][0]
        
        assert call_1["is_self"] == True, "Sender should have is_self=True"
        assert call_2["is_self"] == False, "Other users should have is_self=False"
        assert call_3["is_self"] == False, "Other users should have is_self=False"
    
    @pytest.mark.asyncio
    async def test_broadcast_is_self_true_for_sender(
        self,
        connection_manager: ConnectionManager,
        mock_websocket: AsyncMock,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test that is_self flag is True for the message sender.
        
        This test specifically verifies that when a user sends a message,
        they receive it with is_self=True for proper UI styling.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket: Mocked WebSocket connection
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Connect user
        room_id = sample_room_data["room_id"]
        user_id = sample_room_data["user_id"]
        await connection_manager.connect(mock_websocket, room_id, user_id)
        
        # Act: Broadcast message from the same user
        await connection_manager.broadcast("Test message", room_id, user_id)
        
        # Assert: Verify is_self is True for sender
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["is_self"] == True, "Sender should have is_self=True"
        assert call_args["text"] == "Test message", "Message text should be preserved"
    
    @pytest.mark.asyncio
    async def test_broadcast_is_self_false_for_others(
        self,
        connection_manager: ConnectionManager,
        mock_websocket_factory,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test that is_self flag is False for other users.
        
        This test verifies that when a user sends a message, other users
        in the room receive it with is_self=False for proper UI styling.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket_factory: Factory for creating mock WebSockets
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Connect two users
        room_id = sample_room_data["room_id"]
        sender_id = sample_room_data["user_id"]
        receiver_id = 200
        
        sender_websocket = mock_websocket_factory()
        receiver_websocket = mock_websocket_factory()
        
        await connection_manager.connect(sender_websocket, room_id, sender_id)
        await connection_manager.connect(receiver_websocket, room_id, receiver_id)
        
        # Act: Broadcast message from sender
        await connection_manager.broadcast("Test message", room_id, sender_id)
        
        # Assert: Verify is_self is False for receiver
        receiver_call = receiver_websocket.send_json.call_args[0][0]
        assert receiver_call["is_self"] == False, "Receiver should have is_self=False"
        assert receiver_call["text"] == "Test message", "Message text should be preserved"
    
    @pytest.mark.asyncio
    async def test_broadcast_empty_room_no_error(
        self,
        connection_manager: ConnectionManager,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test broadcasting to an empty room doesn't cause errors.
        
        This test verifies that broadcasting to a room with no users
        doesn't raise an exception and handles the edge case gracefully.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: No users in room
        room_id = sample_room_data["room_id"]
        sender_id = sample_room_data["user_id"]
        message_text = "Test message"
        
        # Act & Assert: Broadcast to empty room should not raise error
        await connection_manager.broadcast(message_text, room_id, sender_id)  # Should not raise exception
        
        # Verify no connections exist (unchanged)
        assert len(connection_manager.active_connections) == 0, "No connections should exist"
    
    @pytest.mark.asyncio
    async def test_broadcast_message_structure(
        self,
        connection_manager: ConnectionManager,
        mock_websocket: AsyncMock,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test that broadcast creates properly structured ChatMessage.
        
        This test verifies that the broadcast method creates a valid
        ChatMessage object with correct field types and values.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket: Mocked WebSocket connection
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Connect user
        room_id = sample_room_data["room_id"]
        user_id = sample_room_data["user_id"]
        await connection_manager.connect(mock_websocket, room_id, user_id)
        
        # Act: Broadcast message
        message_text = "Test message structure"
        await connection_manager.broadcast(message_text, room_id, user_id)
        
        # Assert: Verify message structure
        call_args = mock_websocket.send_json.call_args[0][0]
        
        # Check that the message has required fields
        assert "text" in call_args, "Message should have 'text' field"
        assert "is_self" in call_args, "Message should have 'is_self' field"
        
        # Check field types and values
        assert isinstance(call_args["text"], str), "Text should be string"
        assert isinstance(call_args["is_self"], bool), "is_self should be boolean"
        assert call_args["text"] == message_text, "Text should match input"
        assert call_args["is_self"] == True, "is_self should be True for sender"
    
    @pytest.mark.asyncio
    async def test_broadcast_json_serialization(
        self,
        connection_manager: ConnectionManager,
        mock_websocket: AsyncMock,
        sample_room_data: dict[str, int | str]
    ) -> None:
        """
        Test that broadcast properly serializes ChatMessage to JSON.
        
        This test verifies that the broadcast method uses model_dump()
        to serialize the ChatMessage and calls send_json() with the
        serialized data.
        
        Args:
            connection_manager: Fresh ConnectionManager instance
            mock_websocket: Mocked WebSocket connection
            sample_room_data: Test data with room_id and user_id
        """
        # Arrange: Connect user
        room_id = sample_room_data["room_id"]
        user_id = sample_room_data["user_id"]
        await connection_manager.connect(mock_websocket, room_id, user_id)
        
        # Act: Broadcast message
        message_text = "JSON serialization test"
        await connection_manager.broadcast(message_text, room_id, user_id)
        
        # Assert: Verify send_json was called with serialized data
        mock_websocket.send_json.assert_called_once(), "send_json should be called"
        
        # Verify the call was made with a dictionary (serialized ChatMessage)
        call_args = mock_websocket.send_json.call_args[0][0]
        assert isinstance(call_args, dict), "send_json should receive a dictionary"
        
        # Verify the dictionary contains the expected ChatMessage fields
        expected_message = ChatMessage(text=message_text, is_self=True)
        expected_dict = expected_message.model_dump()
        
        assert call_args == expected_dict, "Serialized message should match expected ChatMessage"
