"""Chat API Router Module."""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.dependencies import get_chat_service
from app.utils.logger import logger

router = APIRouter(tags=["Chat"])

@router.post("/chat", response_model=ChatResponse, summary="Send message to AI Workforce Intelligence Assistant")
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    x_employee_id: Optional[str] = Header(None, alias="X-Employee-Id"),
    x_employee_number: Optional[str] = Header(None, alias="X-Employee-Number")
):
    """Processes user queries regarding workforce intelligence, skills, and recommendations.
    
    Args:
        request (ChatRequest): Request body containing user message.
        chat_service (ChatService): Injected ChatService instance.
        x_employee_id (str, optional): Authenticated employee ID.
        x_employee_number (str, optional): Authenticated employee number.
        
    Returns:
        ChatResponse: AI generated response content.
    """
    try:
        response_text = await chat_service.generate_response(
            message=request.message,
            authenticated_employee_id=x_employee_id,
            authenticated_employee_number=x_employee_number
        )
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error processing chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response from AI Workforce Intelligence Assistant: {str(e)}"
        )
