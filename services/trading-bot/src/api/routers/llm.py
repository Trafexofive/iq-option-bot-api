from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.core.llm.service import LLMService

router = APIRouter()
llm_service = LLMService()


@router.post("/analyze")
async def analyze_market_data(payload: Dict[str, Any]):
    """
    Analyze market data using LLM
    Expected payload: 
    {
        "asset": "EURUSD",
        "market_data": {...},
        "risk_level": 0.5
    }
    """
    try:
        result = await llm_service.get_trading_decision(
            asset=payload.get("asset"),
            market_data=payload.get("market_data"),
            risk_level=payload.get("risk_level", 0.5)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_llm_providers():
    """
    Get available LLM providers
    """
    try:
        providers = await llm_service.get_available_providers()
        return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))