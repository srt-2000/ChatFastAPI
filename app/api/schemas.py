"""
Pydantic schemas for data validation in ChatFastAPI.

This module contains Pydantic models for form validation and WebSocket message structure.
These schemas ensure data integrity and provide clear error messages for user input validation.

Models:
- JoinChatForm: Validates user input for joining chat rooms
- ChatMessage: Structures WebSocket messages for real-time communication
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict


class JoinChatForm(BaseModel):
    """
    Validation schema for chat room entry form.
    
    This model validates user input when joining a chat room, ensuring:
    - Username is not empty and within length limits (1-50 characters)
    - Room ID is a positive integer
    - All input is properly sanitized (trimmed whitespace)
    
    Attributes:
        username: User's display name for the chat
        room_id: Unique identifier for the chat room (must be > 0)
    """
    
    username: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="User's display name for the chat",
        json_schema_extra={"error_messages": {"min_length": "Username cannot be empty"}}
    )
    room_id: int = Field(
        ..., 
        gt=0, 
        description="Unique identifier for the chat room (must be greater than 0)",
        json_schema_extra={"error_messages": {"gt": "Room ID must be greater than 0"}}
    )
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Sanitize username by removing leading/trailing whitespace.
        
        This validator ensures that usernames don't have accidental spaces
        that could cause display issues in the chat interface.
        
        Args:
            v: Raw username input from the form
            
        Returns:
            Cleaned username with trimmed whitespace
        """
        return v.strip()


class ChatMessage(BaseModel):
    """
    WebSocket message structure for real-time chat communication.
    
    This model defines the structure of messages sent through WebSocket connections,
    ensuring consistent message format across all chat participants.
    
    Attributes:
        text: The actual message content
        is_self: Boolean flag indicating if the message is from the current user
                (used for UI styling - own messages vs others' messages)
    """
    
    text: str = Field(..., description="The actual message content")
    is_self: bool = Field(..., description="Whether the message is from the current user")
    
    # Prevent additional fields from being added to maintain message structure integrity
    model_config = ConfigDict(extra="forbid")
