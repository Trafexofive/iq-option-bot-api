"""Real IQ Option API integration using iqoptionapi library."""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal
import concurrent.futures
from threading import Thread

# Conditional import for IQ Option API
try:
    from iqoptionapi.stable_api import IQ_Option
    IQ_OPTION_API_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import
        from iqoptionapi import IQOption as IQ_Option
        IQ_OPTION_API_AVAILABLE = True
    except ImportError:
        IQ_Option = None
        IQ_OPTION_API_AVAILABLE = False

from src.models.trading import TradeResponse, TradeDirection, TradeStatus
from src.integrations.chart_data import ChartData, Candle, Timeframe
from src.config.trading_config import config_parser
from config.settings import settings

logger = logging.getLogger(__name__)


class IQOptionRealAPI:
    """Real IQ Option API integration with async wrapper."""
    
    def __init__(self):
        self.api: Optional[IQ_Option] = None
        self.connected = False
        self.account_balance = 0.0
        self.account_type = "PRACTICE"  # PRACTICE or REAL
        self.supported_assets = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        # Asset mapping for IQ Option API
        self.asset_mapping = {
            # Forex
            "EURUSD": "EURUSD-OTC", "GBPUSD": "GBPUSD-OTC", "USDJPY": "USDJPY-OTC",
            "USDCHF": "USDCHF-OTC", "USDCAD": "USDCAD-OTC", "AUDUSD": "AUDUSD-OTC",
            "NZDUSD": "NZDUSD-OTC", "EURJPY": "EURJPY-OTC", "EURGBP": "EURGBP-OTC",
            # Crypto
            "BTCUSD": "BTCUSD", "ETHUSD": "ETHUSD", "LTCUSD": "LTCUSD",
            "XRPUSD": "XRPUSD", "ADAUSD": "ADAUSD",
            # Add more as needed
        }
        
        # Timeframe mapping
        self.timeframe_mapping = {
            "M1": 60, "M5": 300, "M15": 900, "M30": 1800,
            "H1": 3600, "H4": 14400, "D1": 86400
        }
    
    async def connect(self) -> bool:
        """Connect to IQ Option API."""
        if not IQ_OPTION_API_AVAILABLE:
            logger.error("IQ Option API library not available. Install with: pip install iqoptionapi==4.3.0")
            return False
            
        try:
            logger.info("Connecting to IQ Option API...")
            
            # Run connection in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self.executor, self._connect_sync
            )
            
            if success:
                self.connected = True
                await self._initialize_account_info()
                logger.info(f"Connected to IQ Option API - Account: {self.account_type}, Balance: {self.account_balance}")
                return True
            else:
                logger.error("Failed to connect to IQ Option API")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to IQ Option API: {e}")
            return False
    
    def _connect_sync(self) -> bool:
        """Synchronous connection method."""
        if not IQ_OPTION_API_AVAILABLE:
            return False
            
        try:
            self.api = IQ_Option(
                settings.iq_option_email,
                settings.iq_option_password
            )
            
            check, reason = self.api.connect()
            
            if not check:
                logger.error(f"IQ Option connection failed: {reason}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Sync connection error: {e}")
            return False
    
    async def _initialize_account_info(self):
        """Initialize account information."""
        try:
            loop = asyncio.get_event_loop()
            
            # Get account type and balance
            balance = await loop.run_in_executor(
                self.executor, self.api.get_balance
            )
            self.account_balance = float(balance)
            
            # Check if we're in practice mode
            config = config_parser.get_iq_option_config()
            if config.demo_mode:
                await loop.run_in_executor(
                    self.executor, self.api.change_balance, "PRACTICE"
                )
                self.account_type = "PRACTICE"
            else:
                await loop.run_in_executor(
                    self.executor, self.api.change_balance, "REAL"
                )
                self.account_type = "REAL"
            
            # Get updated balance after account type change
            balance = await loop.run_in_executor(
                self.executor, self.api.get_balance
            )
            self.account_balance = float(balance)
            
            # Get available assets
            await self._load_available_assets()
            
        except Exception as e:
            logger.error(f"Error initializing account info: {e}")
    
    async def _load_available_assets(self):
        """Load available trading assets."""
        try:
            loop = asyncio.get_event_loop()
            
            # Get all available assets
            all_assets = await loop.run_in_executor(
                self.executor, self.api.get_all_open_time
            )
            
            self.supported_assets = {}
            for asset_type in ["binary", "turbo"]:
                if asset_type in all_assets:
                    for asset_name, asset_info in all_assets[asset_type].items():
                        if asset_info.get("open", False):
                            self.supported_assets[asset_name] = asset_info
            
            logger.info(f"Loaded {len(self.supported_assets)} available assets")
            
        except Exception as e:
            logger.error(f"Error loading available assets: {e}")
    
    async def disconnect(self):
        """Disconnect from IQ Option API."""
        try:
            if self.api and self.connected:
                logger.info("Disconnecting from IQ Option API...")
                
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor, self.api.close_connect
                )
                
                self.connected = False
                logger.info("Disconnected from IQ Option API")
                
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
        finally:
            self.executor.shutdown(wait=True)
    
    async def get_candles(
        self, 
        asset: str, 
        timeframe: str, 
        count: int = 100
    ) -> List[Candle]:
        """Get historical candle data."""
        try:
            if not self.connected:
                raise Exception("Not connected to IQ Option API")
            
            # Map asset name
            iq_asset = self.asset_mapping.get(asset, asset)
            
            # Map timeframe
            if timeframe not in self.timeframe_mapping:
                raise ValueError(f"Unsupported timeframe: {timeframe}")
            
            timeframe_seconds = self.timeframe_mapping[timeframe]
            
            # Calculate end time (current time)
            end_time = int(time.time())
            
            logger.debug(f"Fetching candles for {iq_asset}, timeframe: {timeframe_seconds}s, count: {count}")
            
            # Get candles from API
            loop = asyncio.get_event_loop()
            candles_data = await loop.run_in_executor(
                self.executor,
                self.api.get_candles,
                iq_asset,
                timeframe_seconds,
                count,
                end_time
            )
            
            if not candles_data:
                logger.warning(f"No candle data received for {asset}")
                return []
            
            # Convert to our Candle format
            candles = []
            for candle_data in candles_data:
                candle = Candle(
                    open=float(candle_data['open']),
                    high=float(candle_data['max']),
                    low=float(candle_data['min']),
                    close=float(candle_data['close']),
                    volume=float(candle_data.get('volume', 0)),
                    timestamp=datetime.fromtimestamp(candle_data['from'])
                )
                candles.append(candle)
            
            # Sort by timestamp
            candles.sort(key=lambda x: x.timestamp)
            
            logger.debug(f"Successfully fetched {len(candles)} candles for {asset}")
            return candles
            
        except Exception as e:
            logger.error(f"Error fetching candles for {asset}: {e}")
            return []
    
    async def execute_binary_trade(
        self,
        asset: str,
        direction: TradeDirection,
        amount: float,
        duration: int = 60
    ) -> Dict[str, Any]:
        """Execute a binary options trade."""
        try:
            if not self.connected:
                raise Exception("Not connected to IQ Option API")
            
            # Map asset name
            iq_asset = self.asset_mapping.get(asset, asset)
            
            # Check if asset is available
            if iq_asset not in self.supported_assets:
                raise ValueError(f"Asset {asset} is not available for trading")
            
            # Convert direction
            iq_direction = "call" if direction == TradeDirection.CALL else "put"
            
            logger.info(f"Executing {iq_direction} trade: {iq_asset}, ${amount}, {duration}s")
            
            # Execute trade
            loop = asyncio.get_event_loop()
            buy_result = await loop.run_in_executor(
                self.executor,
                self.api.buy,
                amount,
                iq_asset,
                iq_direction,
                duration
            )
            
            if buy_result[0]:
                trade_id = str(buy_result[1])
                logger.info(f"Trade executed successfully: ID {trade_id}")
                
                return {
                    "success": True,
                    "trade_id": trade_id,
                    "asset": asset,
                    "direction": direction.value,
                    "amount": amount,
                    "duration": duration,
                    "message": "Trade executed successfully"
                }
            else:
                error_msg = f"Trade execution failed: {buy_result[1] if len(buy_result) > 1 else 'Unknown error'}"
                logger.error(error_msg)
                
                return {
                    "success": False,
                    "error": error_msg,
                    "asset": asset,
                    "direction": direction.value,
                    "amount": amount,
                    "duration": duration
                }
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return {
                "success": False,
                "error": str(e),
                "asset": asset,
                "direction": direction.value,
                "amount": amount,
                "duration": duration
            }
    
    async def get_trade_result(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed trade."""
        try:
            if not self.connected:
                raise Exception("Not connected to IQ Option API")
            
            loop = asyncio.get_event_loop()
            
            # Wait for trade to complete and get result
            # This is a simplified version - in production you might want to poll periodically
            await asyncio.sleep(2)  # Give some time for trade to process
            
            # Get recent trades to find our trade
            trades = await loop.run_in_executor(
                self.executor, self.api.get_positions, "binary"
            )
            
            if trades:
                for trade in trades:
                    if str(trade.get('id')) == trade_id:
                        return {
                            "trade_id": trade_id,
                            "profit": float(trade.get('win', 0)),
                            "win": trade.get('win', 0) > 0,
                            "status": "completed",
                            "close_time": trade.get('close_time'),
                            "result": trade.get('result', 'unknown')
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting trade result for {trade_id}: {e}")
            return None
    
    async def get_balance(self) -> float:
        """Get current account balance."""
        try:
            if not self.connected:
                return 0.0
            
            loop = asyncio.get_event_loop()
            balance = await loop.run_in_executor(
                self.executor, self.api.get_balance
            )
            
            self.account_balance = float(balance)
            return self.account_balance
            
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get account profile information."""
        try:
            if not self.connected:
                return {}
            
            loop = asyncio.get_event_loop()
            profile = await loop.run_in_executor(
                self.executor, self.api.get_profile
            )
            
            return {
                "balance": await self.get_balance(),
                "currency": profile.get("currency", "USD"),
                "name": profile.get("name", ""),
                "email": profile.get("email", ""),
                "account_type": self.account_type,
                "country": profile.get("country_id", ""),
                "total_assets": len(self.supported_assets)
            }
            
        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return {}
    
    def get_supported_assets(self) -> List[str]:
        """Get list of supported asset names."""
        # Return both original names and IQ Option names
        assets = list(self.asset_mapping.keys())
        assets.extend(self.supported_assets.keys())
        return list(set(assets))
    
    async def is_market_open(self, asset: str) -> bool:
        """Check if market is open for the given asset."""
        try:
            iq_asset = self.asset_mapping.get(asset, asset)
            
            if iq_asset in self.supported_assets:
                asset_info = self.supported_assets[iq_asset]
                return asset_info.get("open", False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking market status for {asset}: {e}")
            return False
    
    async def get_real_time_quote(self, asset: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for an asset."""
        try:
            if not self.connected:
                return None
            
            iq_asset = self.asset_mapping.get(asset, asset)
            
            loop = asyncio.get_event_loop()
            
            # Start getting real-time data
            self.api.start_candles_stream(iq_asset, 60, 1)
            await asyncio.sleep(1)  # Wait for data
            
            candles = self.api.get_realtime_candles(iq_asset, 60)
            
            if candles:
                latest_candle = list(candles.values())[-1]
                return {
                    "asset": asset,
                    "price": latest_candle['close'],
                    "timestamp": datetime.fromtimestamp(latest_candle['to']),
                    "open": latest_candle['open'],
                    "high": latest_candle['max'],
                    "low": latest_candle['min'],
                    "volume": latest_candle.get('volume', 0)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting real-time quote for {asset}: {e}")
            return None