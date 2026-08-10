"""Health Check and Root API Router."""

from fastapi import APIRouter

router = APIRouter(tags=["Health & Info"])

@router.get("/", summary="Root Endpoint")
async def root():
    """Root endpoint returning platform welcome message.
    
    Returns:
        dict: Welcome message payload.
    """
    return {"message": "AI Workforce Intelligence Platform API"}

@router.get("/health", summary="Health Check Endpoint")
async def health_check():
    """Health check endpoint indicating service operational status.
    
    Returns:
        dict: Health status payload.
    """
    return {"status": "healthy"}
