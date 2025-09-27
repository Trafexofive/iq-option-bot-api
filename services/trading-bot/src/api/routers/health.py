from fastapi import APIRouter
from typing import Dict

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "llm-trading-bot-api"}


@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """
    Readiness check endpoint
    """
    # Here we would check if all dependencies are ready
    # For now, we'll just return that the service is ready
    return {"status": "ready", "service": "llm-trading-bot-api"}