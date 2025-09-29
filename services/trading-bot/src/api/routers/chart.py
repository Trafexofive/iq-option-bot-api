"""Chart data and configuration API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/chart", tags=["chart"])

# Import services locally to avoid circular imports
def get_iq_service():
    from src.integrations.iq_option.service import IQOptionService
    return IQOptionService()

def get_config_parser():
    from src.config.trading_config import config_parser
    return config_parser

def get_trading_agent():
    from src.core.trading_agent import TradingAgent
    return TradingAgent()

# Global agent instance
trading_agent_instance = None


@router.get("/data/{asset}/{timeframe}")
async def get_chart_data(
    asset: str,
    timeframe: str,
    count: int = Query(default=100, ge=1, le=1000, description="Number of candles to fetch")
) -> Dict[str, Any]:
    """Get chart data for a specific asset and timeframe."""
    try:
        iq_service = get_iq_service()
        chart_data = await iq_service.get_chart_data(asset, timeframe, count)
        
        if not chart_data:
            raise HTTPException(status_code=404, detail=f"No data available for {asset} {timeframe}")
        
        return chart_data.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")


@router.get("/data/multiple")
async def get_multiple_chart_data(
    assets: List[str] = Query(..., description="List of asset symbols"),
    timeframes: List[str] = Query(..., description="List of timeframes"),
    count: int = Query(default=100, ge=1, le=1000, description="Number of candles per request")
) -> Dict[str, Any]:
    """Get chart data for multiple assets and timeframes."""
    try:
        iq_service = get_iq_service()
        chart_data = await iq_service.get_multiple_chart_data(assets, timeframes, count)
        
        # Convert to serializable format
        result = {}
        for asset, timeframes_data in chart_data.items():
            result[asset] = {}
            for tf, data in timeframes_data.items():
                result[asset][tf] = data.to_dict() if data else None
        
        return {
            "data": result,
            "timestamp": datetime.utcnow().isoformat(),
            "assets_count": len(assets),
            "timeframes_count": len(timeframes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching multiple chart data: {str(e)}")


@router.get("/supported-assets")
async def get_supported_assets() -> Dict[str, List[str]]:
    """Get list of supported trading assets."""
    try:
        iq_service = get_iq_service()
        assets = iq_service.get_supported_assets()
        return {
            "assets": assets,
            "count": len(assets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting supported assets: {str(e)}")


@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """Get chart data cache statistics."""
    try:
        iq_service = get_iq_service()
        stats = iq_service.get_chart_cache_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")


@router.post("/cache/clear")
async def clear_cache() -> Dict[str, str]:
    """Clear chart data cache."""
    try:
        iq_service = get_iq_service()
        iq_service.clear_chart_cache()
        return {
            "message": "Chart data cache cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@router.get("/config")
async def get_trading_config() -> Dict[str, Any]:
    """Get current trading configuration."""
    try:
        config_parser = get_config_parser()
        config = config_parser.load_config()
        return config.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading config: {str(e)}")


@router.get("/config/trading")
async def get_trading_config_section() -> Dict[str, Any]:
    """Get trading configuration section."""
    try:
        config_parser = get_config_parser()
        trading_config = config_parser.get_trading_config()
        return trading_config.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading trading config: {str(e)}")


@router.post("/agent/start")
async def start_trading_agent() -> Dict[str, Any]:
    """Start the trading agent."""
    global trading_agent_instance
    
    try:
        if trading_agent_instance and trading_agent_instance.running:
            return {
                "message": "Trading agent is already running",
                "status": trading_agent_instance.get_status()
            }
        
        trading_agent_instance = get_trading_agent()
        # Start agent in background task
        import asyncio
        asyncio.create_task(trading_agent_instance.start())
        
        # Give it a moment to initialize
        await asyncio.sleep(1)
        
        return {
            "message": "Trading agent started successfully",
            "status": trading_agent_instance.get_status()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting trading agent: {str(e)}")


@router.post("/agent/stop")
async def stop_trading_agent() -> Dict[str, Any]:
    """Stop the trading agent."""
    global trading_agent_instance
    
    try:
        if not trading_agent_instance:
            return {"message": "Trading agent is not running"}
        
        await trading_agent_instance.stop()
        
        return {
            "message": "Trading agent stopped successfully",
            "final_status": trading_agent_instance.get_status()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping trading agent: {str(e)}")


@router.get("/iq-option/status")
async def get_iq_option_status() -> Dict[str, Any]:
    """Get IQ Option connection and account status."""
    try:
        iq_service = get_iq_service()
        status = await iq_service.get_connection_status()
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting IQ Option status: {str(e)}")


@router.get("/iq-option/profile")
async def get_iq_option_profile() -> Dict[str, Any]:
    """Get IQ Option account profile."""
    try:
        iq_service = get_iq_service()
        profile = await iq_service.get_profile()
        return {
            "profile": profile,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting IQ Option profile: {str(e)}")


@router.get("/iq-option/balance")
async def get_iq_option_balance() -> Dict[str, Any]:
    """Get current IQ Option account balance."""
    try:
        iq_service = get_iq_service()
        balance = await iq_service.get_balance()
        return {
            "balance": balance,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting IQ Option balance: {str(e)}")


@router.get("/market/{asset}/status")
async def get_market_status(asset: str) -> Dict[str, Any]:
    """Check if market is open for trading."""
    try:
        iq_service = get_iq_service()
        is_open = await iq_service.is_market_open(asset)
        return {
            "asset": asset,
            "market_open": is_open,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking market status: {str(e)}")


@router.get("/market/{asset}/quote")
async def get_real_time_quote(asset: str) -> Dict[str, Any]:
    """Get real-time quote for an asset."""
    try:
        iq_service = get_iq_service()
        quote = await iq_service.get_real_time_quote(asset)
        
        if not quote:
            raise HTTPException(status_code=404, detail=f"No quote available for {asset}")
        
        return {
            "quote": quote,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting real-time quote: {str(e)}")


@router.post("/trade/execute")
async def execute_trade(
    asset: str,
    direction: str,
    amount: float,
    duration: int = 60
) -> Dict[str, Any]:
    """Execute a binary options trade."""
    try:
        from src.models.trading import TradeDirection
        
        # Validate direction
        try:
            trade_direction = TradeDirection(direction.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid direction: {direction}. Use 'call' or 'put'")
        
        # Validate amount
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        if amount > 10000:  # Safety limit
            raise HTTPException(status_code=400, detail="Amount too large (max: $10,000)")
        
        # Validate duration
        if duration not in [60, 120, 300, 600, 900, 1800, 3600]:
            raise HTTPException(status_code=400, detail="Invalid duration. Use: 60, 120, 300, 600, 900, 1800, or 3600 seconds")
        
        iq_service = get_iq_service()
        
        # Check if connected
        if not iq_service.connected:
            raise HTTPException(status_code=503, detail="Not connected to IQ Option API")
        
        # Check if market is open
        market_open = await iq_service.is_market_open(asset)
        if not market_open:
            raise HTTPException(status_code=400, detail=f"Market is closed for {asset}")
        
        # Execute trade
        result = await iq_service.execute_trade(asset, trade_direction, amount, duration)
        
        return {
            "trade_result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing trade: {str(e)}")


@router.get("/trade/history")
async def get_trade_history() -> Dict[str, Any]:
    """Get recent trading history."""
    try:
        iq_service = get_iq_service()
        trades = await iq_service.get_recent_trades()
        
        return {
            "trades": [trade.dict() for trade in trades],
            "count": len(trades),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trade history: {str(e)}")


@router.post("/iq-option/connect")
async def connect_to_iq_option() -> Dict[str, Any]:
    """Manually connect to IQ Option API."""
    try:
        iq_service = get_iq_service()
        await iq_service.connect()
        
        status = await iq_service.get_connection_status()
        return {
            "message": "Connected to IQ Option API",
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to IQ Option: {str(e)}")


@router.get("/agent/status")
async def get_agent_status() -> Dict[str, Any]:
    """Get trading agent status."""
    global trading_agent_instance
    
    try:
        if not trading_agent_instance:
            return {
                "running": False,
                "message": "Trading agent not initialized"
            }
        
        return trading_agent_instance.get_status()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")


@router.post("/iq-option/disconnect")
async def disconnect_from_iq_option() -> Dict[str, Any]:
    """Manually disconnect from IQ Option API."""
    try:
        iq_service = get_iq_service()
        await iq_service.disconnect()
        
        return {
            "message": "Disconnected from IQ Option API",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting from IQ Option: {str(e)}")