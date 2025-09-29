import logging
from typing import Dict, Any, List, Optional
from src.models.trading import TradeResponse, TradeDirection, TradeStatus
from src.integrations.chart_data import ChartDataService, ChartData
from src.integrations.iq_option.real_api import IQOptionRealAPI
from src.config.trading_config import config_parser
from datetime import datetime

logger = logging.getLogger(__name__)


class IQOptionService:
    def __init__(self, use_real_api: bool = True):
        self.connected = False
        self.session = None
        self.chart_service = ChartDataService()
        self.config = config_parser.get_iq_option_config()
        self.use_real_api = use_real_api
        
        if use_real_api:
            self.real_api = IQOptionRealAPI()
            # Connect real API to chart service
            self.chart_service.iq_api = self.real_api
        else:
            self.real_api = None
            logger.info("Using mock IQ Option service")

    async def connect(self):
        """
        Connect to IQ Option API
        """
        logger.info("Connecting to IQ Option API...")
        
        if self.use_real_api and self.real_api:
            try:
                success = await self.real_api.connect()
                if success:
                    self.connected = True
                    logger.info("Connected to real IQ Option API")
                else:
                    logger.error("Failed to connect to real IQ Option API")
                    raise Exception("Failed to connect to IQ Option API")
            except Exception as e:
                logger.error(f"Error connecting to real IQ Option API: {e}")
                logger.info("Falling back to mock mode")
                self.use_real_api = False
                self.real_api = None
                self.connected = True
        else:
            # Mock connection
            self.connected = True
            logger.info("Connected to IQ Option API (mock mode)")

    async def disconnect(self):
        """
        Disconnect from IQ Option API
        """
        logger.info("Disconnecting from IQ Option API...")
        
        if self.use_real_api and self.real_api:
            await self.real_api.disconnect()
        
        self.connected = False
        logger.info("Disconnected from IQ Option API")

    async def execute_trade(
        self, 
        asset: str, 
        direction: TradeDirection, 
        amount: float, 
        duration: int
    ) -> Dict[str, Any]:
        """
        Execute a trade on IQ Option
        """
        if not self.connected:
            raise Exception("Not connected to IQ Option API")
        
        logger.info(f"Executing trade: {direction} {asset} for {amount}$, duration: {duration}s")
        
        if self.use_real_api and self.real_api:
            # Execute real trade
            try:
                result = await self.real_api.execute_binary_trade(
                    asset=asset,
                    direction=direction,
                    amount=amount,
                    duration=duration
                )
                
                if result.get("success"):
                    logger.info(f"Real trade executed successfully: {result}")
                else:
                    logger.error(f"Real trade execution failed: {result}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error executing real trade: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "asset": asset,
                    "direction": direction.value,
                    "amount": amount,
                    "duration": duration
                }
        else:
            # Mock trade execution
            return {
                "success": True,
                "trade_id": f"mock_trade_id_{int(datetime.utcnow().timestamp())}",
                "asset": asset,
                "direction": direction.value,
                "amount": amount,
                "duration": duration,
                "profit": amount * 0.8,  # Mock profit calculation
                "message": "Mock trade executed successfully"
            }

    async def get_recent_trades(self) -> List[TradeResponse]:
        """
        Get recent trades from IQ Option
        """
        if not self.connected:
            raise Exception("Not connected to IQ Option API")
        
        # In a real implementation, this would fetch actual trade history
        # For now, we'll return mock data
        from datetime import datetime
        from src.models.trading import TradeStatus
        
        return [
            TradeResponse(
                trade_id="mock_trade_1",
                asset="EURUSD",
                direction=TradeDirection.CALL,
                amount=10.0,
                entry_price=1.2345,
                status=TradeStatus.CLOSED,
                profit=8.0,
                created_at=datetime.utcnow(),
                closed_at=datetime.utcnow()
            )
        ]

    async def get_balance(self) -> float:
        """Get current account balance."""
        if not self.connected:
            return 0.0
            
        if self.use_real_api and self.real_api:
            try:
                return await self.real_api.get_balance()
            except Exception as e:
                logger.error(f"Error getting real balance: {e}")
                return 0.0
        else:
            # Mock balance
            return 10000.0

    async def get_profile(self) -> Dict[str, Any]:
        """Get account profile information."""
        if not self.connected:
            return {}
            
        if self.use_real_api and self.real_api:
            try:
                return await self.real_api.get_profile()
            except Exception as e:
                logger.error(f"Error getting real profile: {e}")
                return {"error": str(e)}
        else:
            # Mock profile
            return {
                "balance": 10000.0,
                "currency": "USD",
                "account_type": "PRACTICE",
                "name": "Demo User",
                "email": "demo@example.com"
            }

    async def is_market_open(self, asset: str) -> bool:
        """Check if market is open for trading."""
        if not self.connected:
            return False
            
        if self.use_real_api and self.real_api:
            try:
                return await self.real_api.is_market_open(asset)
            except Exception as e:
                logger.error(f"Error checking market status: {e}")
                return False
        else:
            # Mock - assume always open
            return True

    async def get_real_time_quote(self, asset: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for an asset."""
        if not self.connected:
            return None
            
        if self.use_real_api and self.real_api:
            try:
                return await self.real_api.get_real_time_quote(asset)
            except Exception as e:
                logger.error(f"Error getting real-time quote: {e}")
                return None
        else:
            # Mock quote
            import random
            base_price = 1.2000 if asset == "EURUSD" else 1.0000
            price = base_price + random.uniform(-0.01, 0.01)
            return {
                "asset": asset,
                "price": round(price, 5),
                "timestamp": datetime.utcnow(),
                "bid": round(price - 0.0001, 5),
                "ask": round(price + 0.0001, 5)
            }

    async def get_chart_data(
        self, 
        asset: str, 
        timeframe: str, 
        count: int = 100
    ) -> Optional[ChartData]:
        """
        Get chart data for specified asset and timeframe.
        
        Args:
            asset: Asset symbol (e.g., 'EURUSD')
            timeframe: Timeframe string (e.g., 'M1', 'M5', 'M15')
            count: Number of candles to fetch
            
        Returns:
            ChartData object or None if fetch fails
        """
        if not self.connected:
            await self.connect()
        
        return await self.chart_service.get_chart_data(asset, timeframe, count)
    
    async def get_multiple_chart_data(
        self, 
        assets: List[str], 
        timeframes: List[str], 
        count: int = 100
    ) -> Dict[str, Dict[str, ChartData]]:
        """
        Get chart data for multiple assets and timeframes.
        
        Args:
            assets: List of asset symbols
            timeframes: List of timeframe strings
            count: Number of candles per request
            
        Returns:
            Nested dict: {asset: {timeframe: ChartData}}
        """
        if not self.connected:
            await self.connect()
        
        return await self.chart_service.get_multiple_assets_data(assets, timeframes, count)
    
    def get_supported_assets(self) -> List[str]:
        """Get list of supported assets."""
        if self.use_real_api and self.real_api:
            return self.real_api.get_supported_assets()
        else:
            return self.chart_service.supported_assets
    
    def clear_chart_cache(self):
        """Clear chart data cache."""
        self.chart_service.clear_cache()
    
    def get_chart_cache_stats(self) -> Dict[str, Any]:
        """Get chart data cache statistics."""
        return self.chart_service.get_cache_stats()

    def is_using_real_api(self) -> bool:
        """Check if using real API or mock mode."""
        return self.use_real_api and self.real_api is not None

    async def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status."""
        return {
            "connected": self.connected,
            "using_real_api": self.is_using_real_api(),
            "demo_mode": self.config.demo_mode,
            "api_timeout": self.config.api_timeout,
            "account_balance": await self.get_balance() if self.connected else 0.0,
            "account_type": "REAL" if not self.config.demo_mode else "PRACTICE"
        }