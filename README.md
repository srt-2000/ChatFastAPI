# 💬 ChatFastAPI

> **Educational Project** - A learning project demonstrating WebSocket chat implementation and comprehensive unit testing

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-34%20passing-green.svg)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A real-time chat application built with FastAPI and WebSocket technology. This project serves as an educational example of modern Python web development, demonstrating WebSocket implementation, form validation, and comprehensive unit testing practices.

## ✨ Features

- **Real-time messaging** with WebSocket connections
- **Multiple chat rooms** - users can join different rooms
- **Form validation** with clear error messages using Pydantic
- **Clean, modern UI** with Tailwind CSS
- **Full test coverage** - 34 unit tests covering all functionality
- **Educational focus** - demonstrates WebSocket testing patterns

## 🚀 Quick Start

### Requirements

- Python 3.12 or higher
- Poetry (package manager)

### Installation

```bash
# Step 1: Clone the repository
git clone <your-repo-url>
cd ChatFastAPI

# Step 2: Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Step 3: Install dependencies
poetry install --no-root

# Step 4: Run the server
poetry run uvicorn app.main:app --reload
```

### Usage

1. Open your browser and go to `http://localhost:8000`
2. Enter your name and choose a room ID
3. Click "Enter chat" to join the room
4. Start chatting in real-time!

## 📁 Project Structure

```
ChatFastAPI/
├── app/
│   ├── api/
│   │   ├── router_page.py     # HTTP endpoints (forms, pages)
│   │   ├── router_socket.py   # WebSocket endpoints (chat)
│   │   └── schemas.py         # Pydantic validation models
│   ├── main.py                # FastAPI application
│   ├── static/
│   │   └── index.js          # Client-side JavaScript
│   └── templates/
│       ├── home.html         # Entry form page
│       └── index.html        # Chat interface
├── tests/
│   ├── conftest.py           # Test fixtures and setup
│   ├── test_router_page.py   # HTTP endpoint tests (18 tests)
│   └── test_router_socket.py # WebSocket tests (16 tests)
├── pyproject.toml            # Project dependencies
└── pytest.ini                # Test configuration
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page with chat entry form |
| POST | `/join_chat` | Submit form and join chat room |
| WebSocket | `/ws/chat/{room_id}/{user_id}` | Real-time messaging connection |

## 🔄 How It Works

1. **User enters form** - Name and room ID are validated using Pydantic schemas
2. **Form validation** - Server validates input and shows errors if needed
3. **WebSocket connection** - Client connects to chat room via WebSocket
4. **Real-time messaging** - Messages are broadcast to all room participants
5. **Connection management** - Server handles user joins/leaves automatically

## 🧪 Testing

This project includes comprehensive unit tests demonstrating WebSocket testing patterns:

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_router_page.py
poetry run pytest tests/test_router_socket.py
```

### Test Coverage

- **18 HTTP endpoint tests** - Form validation, error handling, template rendering
- **16 WebSocket tests** - Connection management, message broadcasting, user handling
- **Total: 34 tests** - All passing with full coverage

### WebSocket Testing Examples

The project demonstrates how to test WebSocket functionality:

```python
# Test WebSocket connection
async def test_websocket_connection(test_client: TestClient):
    with test_client.websocket_connect("/ws/chat/1/100?username=testuser") as websocket:
        data = websocket.receive_json()
        assert "connected" in data["text"]

# Test message broadcasting
async def test_broadcast_message(connection_manager: ConnectionManager):
    await connection_manager.broadcast("Hello", room_id=1, sender_id=100)
    # Verify message was sent to all room participants
```

## 🛠 Tech Stack

- **Backend:** FastAPI, Uvicorn
- **WebSocket:** Native WebSocket support for real-time communication
- **Validation:** Pydantic schemas with comprehensive error handling
- **Frontend:** Jinja2 templates, Vanilla JavaScript
- **Styling:** Tailwind CSS (CDN)
- **Testing:** Pytest, pytest-asyncio, httpx
- **Type Safety:** Python 3.12+ with modern type hints

## 🏗 Development

```bash
# Install development dependencies
poetry install

# Run tests with coverage
poetry run pytest --cov=app

# Run specific test categories
poetry run pytest tests/test_router_page.py -v
poetry run pytest tests/test_router_socket.py -v
```

## 📚 Educational Value

This project demonstrates:

- **WebSocket implementation** - Real-time bidirectional communication
- **Connection management** - Handling multiple users and rooms
- **Form validation** - Pydantic schemas with error messages
- **Unit testing patterns** - Testing async WebSocket functionality
- **Modern Python practices** - Type hints, async/await, dependency injection
- **FastAPI best practices** - Router organization, template rendering

## 📄 License

MIT License - feel free to use this project for learning and educational purposes.

## 👨‍💻 Author

- **Name:** srt-2000
- **Email:** srt2000888@gmail.ru

---

**Happy Learning!** 🚀 This project is designed to help you understand WebSocket implementation and modern Python testing practices.
