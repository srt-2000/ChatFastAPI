"""
Shared test fixtures for ChatFastAPI unit tests.

This module provides reusable fixtures for testing WebSocket functionality,
ConnectionManager, and related components. All fixtures include proper type
annotations and comprehensive documentation.

Fixtures are designed to be:
- Stateless and isolated between tests
- Properly typed for Python 3.12+ compatibility
- Well-documented with clear usage examples
- Reusable across different test modules
"""

import pytest
from unittest.mock import AsyncMock
from collections.abc import Callable
from fastapi.testclient import TestClient

from app.api.router_socket import ConnectionManager
from app.main import app


@pytest.fixture
def connection_manager() -> ConnectionManager:
    """
    Create a fresh ConnectionManager instance for each test.
    
    This fixture provides a clean ConnectionManager instance with no existing
    connections, ensuring test isolation. Each test gets a fresh instance to
    prevent state leakage between tests.
    
    Returns:
        ConnectionManager: A new instance with empty active_connections dict
        
    Example:
        ```python
        async def test_connect(connection_manager: ConnectionManager):
            # Use the fresh instance for testing
            await connection_manager.connect(mock_websocket, room_id=1, user_id=100)
        ```
    """
    return ConnectionManager()


@pytest.fixture
def mock_websocket() -> AsyncMock:
    """
    Create a mock WebSocket object with async methods.
    
    This fixture provides a properly configured AsyncMock that simulates
    WebSocket behavior for testing. The mock includes all necessary async
    methods like accept() and send_json().
    
    Returns:
        AsyncMock: A mock WebSocket with async methods configured
        
    Example:
        ```python
        async def test_websocket_accept(mock_websocket: AsyncMock):
            # The mock is ready to simulate WebSocket.accept() calls
            await mock_websocket.accept()
            mock_websocket.accept.assert_called_once()
        ```
    """
    # Create AsyncMock for WebSocket with all necessary async methods
    websocket = AsyncMock()
    
    # Configure async methods that ConnectionManager uses
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.receive_text = AsyncMock()
    
    return websocket


@pytest.fixture
def mock_websocket_factory() -> Callable[[], AsyncMock]:
    """
    Factory fixture to create multiple mock WebSocket objects.
    
    This fixture returns a factory function that creates new AsyncMock
    WebSocket objects. Useful for testing scenarios with multiple users
    or connections in the same room.
    
    Returns:
        Callable[[], AsyncMock]: Factory function that creates new mock WebSockets
        
    Example:
        ```python
        async def test_multiple_users(mock_websocket_factory: Callable[[], AsyncMock]):
            # Create multiple mock WebSockets for different users
            ws1 = mock_websocket_factory()
            ws2 = mock_websocket_factory()
            # Each is independent and properly configured
        ```
    """
    def create_websocket() -> AsyncMock:
        """Create a new mock WebSocket instance."""
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        websocket.send_json = AsyncMock()
        websocket.receive_text = AsyncMock()
        return websocket
    
    return create_websocket


@pytest.fixture
def sample_room_data() -> dict[str, int | str]:
    """
    Provide sample test data for room_id, user_id, and username.
    
    This fixture provides consistent test data across multiple tests,
    ensuring predictable behavior and easy maintenance of test values.
    
    Returns:
        dict[str, int | str]: Dictionary containing sample test data
        
    Example:
        ```python
        async def test_connect_with_data(sample_room_data: dict[str, int | str]):
            room_id = sample_room_data["room_id"]  # 1
            user_id = sample_room_data["user_id"]  # 100
            username = sample_room_data["username"]  # "testuser"
        ```
    """
    return {
        "room_id": 1,
        "user_id": 100,
        "username": "testuser"
    }


@pytest.fixture
def multiple_room_data() -> dict[str, dict[str, int | str]]:
    """
    Provide test data for multiple rooms and users.
    
    This fixture provides structured data for testing scenarios involving
    multiple rooms and users, useful for testing broadcast functionality
    and room isolation.
    
    Returns:
        dict[str, dict[str, int | str]]: Nested dict with room and user data
        
    Example:
        ```python
        async def test_multiple_rooms(multiple_room_data: dict[str, dict[str, int | str]]):
            room1_data = multiple_room_data["room1"]  # {"room_id": 1, "user_id": 100}
            room2_data = multiple_room_data["room2"]  # {"room_id": 2, "user_id": 200}
        ```
    """
    return {
        "room1": {
            "room_id": 1,
            "user_id": 100,
            "username": "user1"
        },
        "room2": {
            "room_id": 2,
            "user_id": 200,
            "username": "user2"
        },
        "room1_user2": {
            "room_id": 1,
            "user_id": 300,
            "username": "user3"
        }
    }


@pytest.fixture
def sample_message_data() -> dict[str, str | int | bool]:
    """
    Provide sample message data for testing broadcast functionality.
    
    This fixture provides test message content and metadata for testing
    message broadcasting, serialization, and ChatMessage schema validation.
    
    Returns:
        dict[str, object]: Dictionary containing sample message data
        
    Example:
        ```python
        async def test_broadcast_message(sample_message_data: dict[str, object]):
            message_text = sample_message_data["text"]  # "Hello World"
            sender_id = sample_message_data["sender_id"]  # 100
        ```
    """
    return {
        "text": "Hello World",
        "sender_id": 100,
        "expected_is_self": True
    }


@pytest.fixture
def test_client() -> TestClient:
    """
    Create FastAPI TestClient for HTTP endpoint testing.
    
    This fixture provides a TestClient instance for testing HTTP endpoints
    without running a real server. It allows testing of GET/POST requests,
    form submissions, and template rendering.
    
    Returns:
        TestClient: FastAPI TestClient instance for HTTP testing
        
    Example:
        ```python
        def test_home_page(test_client: TestClient):
            response = test_client.get("/")
            assert response.status_code == 200
        ```
    """
    return TestClient(app)


@pytest.fixture
def sample_form_data_valid(sample_room_data: dict[str, int | str]) -> dict[str, str | int]:
    """
    Provide valid form data for join_chat endpoint testing.
    
    This fixture creates valid form data by reusing existing sample_room_data,
    ensuring consistency across tests and avoiding data duplication.
    
    Args:
        sample_room_data: Existing fixture with room_id and username
        
    Returns:
        dict[str, str | int]: Valid form data for POST requests
        
    Example:
        ```python
        def test_join_chat_success(test_client: TestClient, sample_form_data_valid: dict[str, str | int]):
            response = test_client.post("/join_chat", data=sample_form_data_valid)
            assert response.status_code == 200
        ```
    """
    return {
        "username": str(sample_room_data["username"]),
        "room_id": int(sample_room_data["room_id"])
    }


@pytest.fixture
def sample_form_data_invalid() -> dict[str, dict[str, str | int]]:
    """
    Provide various invalid form data scenarios for validation testing.
    
    This fixture provides a comprehensive set of invalid form data to test
    all validation edge cases, including empty fields, boundary values,
    and invalid data types.
    
    Returns:
        dict[str, dict[str, str | int]]: Dictionary of invalid form data scenarios
        
    Example:
        ```python
        def test_join_chat_validation_errors(test_client: TestClient, sample_form_data_invalid: dict[str, dict[str, str | int]]):
            invalid_data = sample_form_data_invalid["empty_username"]
            response = test_client.post("/join_chat", data=invalid_data)
            assert response.status_code == 200  # Returns form with errors
        ```
    """
    return {
        "empty_username": {"username": "", "room_id": 1},
        "whitespace_username": {"username": "   ", "room_id": 1},
        "long_username": {"username": "a" * 51, "room_id": 1},
        "zero_room_id": {"username": "testuser", "room_id": 0},
        "negative_room_id": {"username": "testuser", "room_id": -1}
    }
