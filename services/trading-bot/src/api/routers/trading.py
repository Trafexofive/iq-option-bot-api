from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.models.trading import TradeRequest, TradeResponse, MarketData, LLMResponse
from src.core.trading.service import TradingService
from src.core.market.service import MarketService
from src.core.llm.service import LLMService

router = APIRouter()

# Initialize services
trading_service = TradingService()
market_service = MarketService()
llm_service = LLMService()


@router.post("/trade", response_model=TradeResponse)
async def execute_trade(trade_request: TradeRequest):
    """
    Execute a trade based on LLM decision
    """
    try:
        # Get market data for the requested asset
        market_data = await market_service.get_market_data(trade_request.asset)
        
        # Get LLM decision
        llm_decision = await llm_service.get_trading_decision(
            asset=trade_request.asset,
            market_data=market_data,
            risk_level=trade_request.risk_level
        )
        
        # Execute the trade
        trade_result = await trading_service.execute_trade(
            trade_request=trade_request,
            llm_decision=llm_decision
        )
        
        return trade_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades():
    """
    Get all recent trades
    """
    try:
        trades = await trading_service.get_recent_trades()
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/{asset}", response_model=MarketData)
async def get_market_data(asset: str):
    """
    Get current market data for an asset
    """
    try:
        market_data = await market_service.get_market_data(asset)
        return market_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=LLMResponse)
async def analyze_market(asset: str):
    """
    Get LLM analysis for an asset
    """
    try:
        market_data = await market_service.get_market_data(asset)
        analysis = await llm_service.get_trading_decision(asset, market_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))