"""
ChatFastAPI - Real-time chat application with WebSocket support.

This is the main FastAPI application that provides:
- Web interface for chat room entry
- Real-time messaging via WebSocket connections
- Static file serving for frontend assets
- Form validation using Pydantic schemas

The application consists of two main routers:
- Page router: Handles HTTP endpoints for web interface
- Socket router: Manages WebSocket connections for real-time chat

Architecture:
- FastAPI for HTTP/WebSocket handling
- Jinja2 templates for server-side rendering
- Pydantic for data validation
- WebSocket for real-time communication
"""

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.api.router_page import router as router_page
from app.api.router_socket import router as router_socket

# Create the main FastAPI application instance
app = FastAPI(
    title="ChatFastAPI",
    description="Real-time chat application with WebSocket support",
    version="1.0.0"
)

# Mount static files directory for serving frontend assets
# This serves CSS, JavaScript, and other static resources
app.mount("/static", StaticFiles(directory="app/static"), "static")

# Include routers for different functionality
# Socket router handles WebSocket connections (prefix: /ws/chat)
app.include_router(router_socket)
# Page router handles HTTP endpoints for web interface
app.include_router(router_page)