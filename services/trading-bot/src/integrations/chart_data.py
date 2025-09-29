"""Real chart data service for fetching market data from IQ Option API."""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Timeframe(Enum):
    """Supported chart timeframes."""
    M1 = 60      # 1 minute
    M5 = 300     # 5 minutes  
    M15 = 900    # 15 minutes
    M30 = 1800   # 30 minutes
    H1 = 3600    # 1 hour
    H4 = 14400   # 4 hours
    D1 = 86400   # 1 day


@dataclass
class Candle:
    """Individual price candle data."""
    open: float
    high: float
    low: float  
    close: float
    volume: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass 
class ChartData:
    """Chart data for a specific asset and timeframe."""
    asset: str
    timeframe: str
    candles: List[Candle]
    last_update: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset": self.asset,
            "timeframe": self.timeframe,
            "candles": [candle.to_dict() for candle in self.candles],
            "last_update": self.last_update.isoformat(),
            "candle_count": len(self.candles)
        }


class ChartDataService:
    """Service for fetching real chart data from IQ Option."""
    
    def __init__(self, iq_api=None):
        self.iq_api = iq_api
        self.supported_assets = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
            "EURJPY", "EURGBP", "EURCHF", "GBPJPY", "GBPCHF", "AUDJPY", "NZDJPY",
            "BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "ADAUSD", "DOTUSD",
            "GOOGL", "AAPL", "MSFT", "AMZN", "TSLA", "NVDA", "META",
            "GOLD", "SILVER", "OIL", "GAS",
            "SPX500", "NDQ100", "DAX30", "FTSE100", "NIKKEI225"
        ]
        self.cache: Dict[str, ChartData] = {}
        self.cache_duration = timedelta(minutes=1)  # Cache for 1 minute
    
    def _get_cache_key(self, asset: str, timeframe: str) -> str:
        """Generate cache key for asset and timeframe combination."""
        return f"{asset}_{timeframe}"
    
    def _is_cache_valid(self, chart_data: ChartData) -> bool:
        """Check if cached data is still valid."""
        return (datetime.utcnow() - chart_data.last_update) < self.cache_duration
    
    async def get_chart_data(
        self, 
        asset: str, 
        timeframe: str, 
        count: int = 100,
        force_refresh: bool = False
    ) -> Optional[ChartData]:
        """
        Fetch chart data for specified asset and timeframe.
        
        Args:
            asset: Asset symbol (e.g., 'EURUSD')
            timeframe: Timeframe string (e.g., 'M1', 'M5', 'M15')  
            count: Number of candles to fetch
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            ChartData object or None if fetch fails
        """
        cache_key = self._get_cache_key(asset, timeframe)
        
        # Check cache first
        if not force_refresh and cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if self._is_cache_valid(cached_data):
                logger.debug(f"Returning cached data for {asset} {timeframe}")
                return cached_data
        
        # Validate asset
        if asset not in self.supported_assets:
            logger.warning(f"Unsupported asset: {asset}")
            return None
            
        # Validate timeframe
        try:
            tf_enum = Timeframe[timeframe]
        except KeyError:
            logger.error(f"Unsupported timeframe: {timeframe}")
            return None
        
        try:
            if self.iq_api and hasattr(self.iq_api, 'get_candles'):
                # Use real IQ Option API
                candles_data = await self._fetch_real_data(asset, tf_enum, count)
            else:
                # Use mock data for testing
                logger.warning("Using mock data - IQ Option API not available")
                candles_data = await self._fetch_mock_data(asset, timeframe, count)
                
            if not candles_data:
                logger.error(f"No data received for {asset} {timeframe}")
                return None
                
            chart_data = ChartData(
                asset=asset,
                timeframe=timeframe, 
                candles=candles_data,
                last_update=datetime.utcnow()
            )
            
            # Cache the data
            self.cache[cache_key] = chart_data
            logger.info(f"Fetched {len(candles_data)} candles for {asset} {timeframe}")
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error fetching chart data for {asset} {timeframe}: {e}")
            return None
    
    async def _fetch_real_data(self, asset: str, timeframe: Timeframe, count: int) -> List[Candle]:
        """Fetch real data from IQ Option API."""
        try:
            logger.debug(f"Fetching real data for {asset} {timeframe.name}")
            
            # Use the IQ Option API to get candles
            candles = await self.iq_api.get_candles(asset, timeframe.name, count)
            
            if not candles:
                logger.warning(f"No real data received for {asset} {timeframe.name}")
                return []
            
            logger.debug(f"Fetched {len(candles)} real candles for {asset} {timeframe.name}")
            return candles
            
        except Exception as e:
            logger.error(f"Error fetching real data: {e}")
            raise
    
    async def _fetch_mock_data(self, asset: str, timeframe: str, count: int) -> List[Candle]:
        """Generate mock chart data for testing."""
        import random
        
        candles = []
        tf_seconds = Timeframe[timeframe].value
        base_price = self._get_base_price(asset)
        
        # Generate candles going backwards in time
        for i in range(count):
            timestamp = datetime.utcnow() - timedelta(seconds=tf_seconds * (count - i))
            
            # Generate realistic price movement
            volatility = 0.002  # 0.2% volatility
            price_change = random.uniform(-volatility, volatility)
            
            open_price = base_price * (1 + price_change)
            close_price = open_price * (1 + random.uniform(-volatility, volatility))
            
            high_price = max(open_price, close_price) * (1 + random.uniform(0, volatility/2))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, volatility/2))
            
            volume = random.uniform(1000, 10000)
            
            candle = Candle(
                open=round(open_price, 5),
                high=round(high_price, 5),
                low=round(low_price, 5),
                close=round(close_price, 5),
                volume=round(volume, 2),
                timestamp=timestamp
            )
            candles.append(candle)
            base_price = close_price  # Use close as next base
        
        return candles
    
    def _get_base_price(self, asset: str) -> float:
        """Get base price for mock data generation."""
        base_prices = {
            "EURUSD": 1.1000, "GBPUSD": 1.2500, "USDJPY": 110.00,
            "USDCHF": 0.9200, "USDCAD": 1.2800, "AUDUSD": 0.7300,
            "BTCUSD": 45000.0, "ETHUSD": 3000.0, "LTCUSD": 150.0,
            "GOOGL": 2500.0, "AAPL": 150.0, "MSFT": 300.0,
            "GOLD": 1800.0, "SILVER": 24.0, "OIL": 70.0,
            "SPX500": 4200.0, "NDQ100": 14000.0, "DAX30": 15500.0
        }
        return base_prices.get(asset, 1.0000)
    
    async def get_multiple_assets_data(
        self, 
        assets: List[str], 
        timeframes: List[str], 
        count: int = 100
    ) -> Dict[str, Dict[str, ChartData]]:
        """
        Fetch chart data for multiple assets and timeframes.
        
        Args:
            assets: List of asset symbols
            timeframes: List of timeframe strings
            count: Number of candles per request
            
        Returns:
            Nested dict: {asset: {timeframe: ChartData}}
        """
        results = {}
        
        # Create tasks for concurrent fetching
        tasks = []
        asset_tf_pairs = []
        
        for asset in assets:
            results[asset] = {}
            for timeframe in timeframes:
                task = self.get_chart_data(asset, timeframe, count)
                tasks.append(task)
                asset_tf_pairs.append((asset, timeframe))
        
        # Execute all tasks concurrently
        chart_data_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for (asset, timeframe), chart_data in zip(asset_tf_pairs, chart_data_list):
            if isinstance(chart_data, Exception):
                logger.error(f"Error fetching {asset} {timeframe}: {chart_data}")
                results[asset][timeframe] = None
            else:
                results[asset][timeframe] = chart_data
        
        return results
    
    def clear_cache(self):
        """Clear all cached chart data."""
        self.cache.clear()
        logger.info("Chart data cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        valid_entries = 0
        total_entries = len(self.cache)
        
        for chart_data in self.cache.values():
            if self._is_cache_valid(chart_data):
                valid_entries += 1
                
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries,
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60
        }