"""
Page router for ChatFastAPI application.

This module handles HTTP endpoints for the web interface, including:
- Home page with chat room entry form
- Form processing with Pydantic validation
- Error handling and user feedback

The router uses Jinja2 templates for server-side rendering and provides
a seamless user experience with proper form validation and error messages.
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
import random

from app.api.schemas import JoinChatForm

# Configure Jinja2 templates for server-side rendering
templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request) -> HTMLResponse:
    """
    Home page endpoint displaying the chat room entry form.
    
    This endpoint serves the main landing page where users can:
    - Enter their username
    - Specify a room ID to join
    - Submit the form to enter the chat
    
    Args:
        request: FastAPI Request object for template context
        
    Returns:
        HTMLResponse: Rendered home.html template with form
    """
    return templates.TemplateResponse(request, "home.html")


@router.post("/join_chat", response_class=HTMLResponse)
async def join_chat(request: Request) -> HTMLResponse:
    """
    Process chat room entry form with Pydantic validation.
    
    This endpoint handles form submission for joining chat rooms:
    1. Extracts form data from the request
    2. Validates input using JoinChatForm schema
    3. Generates a random user ID for the session
    4. Redirects to chat interface on success
    5. Returns form with errors on validation failure
    
    The validation ensures:
    - Username is not empty and within length limits
    - Room ID is a positive integer
    - All input is properly sanitized
    
    Args:
        request: FastAPI Request object containing form data
        
    Returns:
        HTMLResponse: Either chat interface (index.html) or form with errors (home.html)
    """
    # Extract form data from the HTTP request
    form_data_raw = await request.form()
    
    try:
        # Validate form data using Pydantic schema
        # This ensures data integrity and provides clear error messages
        form_data = JoinChatForm(
            username=form_data_raw.get("username", ""),
            room_id=int(form_data_raw.get("room_id", 0))
        )
        
        # Generate a random user ID for this chat session
        # Range 100-100000 provides sufficient uniqueness for demo purposes
        user_id = random.randint(100, 100000)
        
        # Render the chat interface with validated data
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "room_id": form_data.room_id,
                "username": form_data.username,
                "user_id": user_id
            }
        )
    except ValidationError as e:
        # Handle validation errors by returning the form with error messages
        # This provides immediate feedback to users about input issues
        error_messages = [error['msg'] for error in e.errors()]
        
        return templates.TemplateResponse(
            request,
            "home.html",
            {
                "error_messages": error_messages,
                "username": form_data_raw.get("username", ""),
                "room_id": form_data_raw.get("room_id", "")
            }
        )