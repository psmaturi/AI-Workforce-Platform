"""Pydantic Schemas for Chat Endpoint."""

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Pydantic model representing incoming chat request payload."""
    
    message: str = Field(
        ...,
        description="User message query regarding workforce intelligence, skills, or career guidance.",
        examples=["I want to become an AI Engineer."]
    )

class ChatResponse(BaseModel):
    """Pydantic model representing outgoing chat response payload."""
    
    response: str = Field(
        ...,
        description="Generated response content from the AI Workforce Intelligence Assistant."
    )
