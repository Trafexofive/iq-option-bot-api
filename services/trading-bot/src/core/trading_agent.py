"""Main trading agent that orchestrates all components."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, time, timedelta
import json
from pathlib import Path

from src.config.trading_config import config_parser, TradingConfig
from src.integrations.iq_option.service import IQOptionService
from src.integrations.chart_data import ChartData
from src.core.manifests import (
    manifest_loader, ManifestType, BaseIndicator, BaseTrigger, BaseNewsFeed
)
from src.models.trading import TradeDirection, TradeRequest

logger = logging.getLogger(__name__)


class TradingAgent:
    """Main trading agent that manages the entire trading process."""
    
    def __init__(self):
        self.config = config_parser.get_trading_config()
        self.iq_service = IQOptionService()
        self.indicators: Dict[str, BaseIndicator] = {}
        self.triggers: Dict[str, BaseTrigger] = {}
        self.news_feeds: Dict[str, BaseNewsFeed] = {}
        self.running = False
        self.daily_trades = 0
        self.daily_losses = 0
        self.last_trade_date = None
        
        # Initialize components from config
        self._load_components()
    
    def _load_components(self):
        """Load indicators, triggers, and news feeds from configuration."""
        logger.info("Loading trading components...")
        
        # Load context feeds (indicators and custom feeds)
        for feed_name in self.config.context_feeds:
            if feed_name.endswith('.yml') or feed_name.endswith('.yaml'):
                # Custom manifest
                manifest = manifest_loader.load_manifest_from_file(feed_name)
                if manifest:
                    component = manifest_loader.load_component(manifest)
                    if isinstance(component, BaseIndicator):
                        self.indicators[manifest.name] = component
                        logger.info(f"Loaded custom indicator: {manifest.name}")
                    elif isinstance(component, BaseNewsFeed):
                        self.news_feeds[manifest.name] = component
                        logger.info(f"Loaded custom news feed: {manifest.name}")
            else:
                # Built-in indicator
                if feed_name in ["RSI", "MACD", "BollingerBands", "SMA", "EMA"]:
                    # Create manifest for built-in indicator
                    from src.core.manifests import IndicatorManifest
                    manifest = IndicatorManifest(
                        name=feed_name,
                        version="1.0.0",
                        description=f"Built-in {feed_name} indicator",
                        type=ManifestType.INDICATOR,
                        implementation=feed_name,
                        outputs=[feed_name.lower()]
                    )
                    component = manifest_loader.load_component(manifest)
                    if component:
                        self.indicators[feed_name] = component
                        logger.info(f"Loaded built-in indicator: {feed_name}")
        
        # Load triggers
        for trigger_name in self.config.triggers:
            if trigger_name.endswith('.yml') or trigger_name.endswith('.yaml'):
                # Custom manifest
                manifest = manifest_loader.load_manifest_from_file(trigger_name)
                if manifest:
                    component = manifest_loader.load_component(manifest)
                    if isinstance(component, BaseTrigger):
                        self.triggers[manifest.name] = component
                        logger.info(f"Loaded custom trigger: {manifest.name}")
            else:
                # Built-in trigger
                if trigger_name in ["PriceActionTrigger", "VolumeSpikeTrigger", "MomentumTrigger"]:
                    from src.core.manifests import TriggerManifest
                    manifest = TriggerManifest(
                        name=trigger_name,
                        version="1.0.0", 
                        description=f"Built-in {trigger_name} trigger",
                        type=ManifestType.TRIGGER,
                        implementation=trigger_name,
                        conditions=["Built-in trigger condition"],
                        actions=["BUY", "SELL", "HOLD"]
                    )
                    component = manifest_loader.load_component(manifest)
                    if component:
                        self.triggers[trigger_name] = component
                        logger.info(f"Loaded built-in trigger: {trigger_name}")
        
        logger.info(f"Loaded {len(self.indicators)} indicators, {len(self.triggers)} triggers, {len(self.news_feeds)} news feeds")
    
    async def start(self):
        """Start the trading agent."""
        logger.info("Starting trading agent...")
        self.running = True
        
        # Connect to IQ Option
        await self.iq_service.connect()
        
        # Main trading loop
        try:
            await self._trading_loop()
        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the trading agent."""
        logger.info("Stopping trading agent...")
        self.running = False
        await self.iq_service.disconnect()
    
    async def _trading_loop(self):
        """Main trading loop."""
        wake_interval = self._parse_interval(self.config.wake_interval)
        
        while self.running:
            try:
                current_time = datetime.now().time()
                
                # Check if we should trade (trading hours)
                if not self._is_trading_time(current_time):
                    logger.debug("Outside trading hours, sleeping...")
                    await asyncio.sleep(wake_interval)
                    continue
                
                # Reset daily counters if new day
                self._check_new_day()
                
                # Check daily trade limits
                if self.daily_trades >= self.config.max_daily_trades:
                    logger.info(f"Daily trade limit reached ({self.config.max_daily_trades})")
                    await asyncio.sleep(wake_interval)
                    continue
                
                # Check loss limits
                if self.daily_losses >= self.config.stop_after_losses:
                    logger.info(f"Daily loss limit reached ({self.config.stop_after_losses})")
                    await asyncio.sleep(wake_interval)
                    continue
                
                # Analyze market and make trading decision
                await self._analyze_and_trade()
                
                # Sleep until next iteration
                await asyncio.sleep(wake_interval)
                
            except Exception as e:
                logger.error(f"Error in trading loop iteration: {e}")
                await asyncio.sleep(wake_interval)
    
    def _parse_interval(self, interval: str) -> float:
        """Parse interval string to seconds."""
        if interval.endswith('s'):
            return float(interval[:-1])
        elif interval.endswith('m'):
            return float(interval[:-1]) * 60
        elif interval.endswith('h'):
            return float(interval[:-1]) * 3600
        else:
            return 120.0  # Default 2 minutes
    
    def _is_trading_time(self, current_time: time) -> bool:
        """Check if current time is within trading hours."""
        if self.config.trading_hours:
            start_time = time.fromisoformat(self.config.trading_hours.start)
            end_time = time.fromisoformat(self.config.trading_hours.end)
            return start_time <= current_time <= end_time
        
        # If trading sessions are specified instead
        if self.config.trading_sessions:
            # Simple implementation - assume always in session for now
            # In real implementation, would check timezone-aware session times
            return True
        
        # Default: always trade
        return True
    
    def _check_new_day(self):
        """Check if it's a new trading day and reset counters."""
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.daily_losses = 0
            self.last_trade_date = today
            logger.info(f"New trading day: {today}")
    
    async def _analyze_and_trade(self):
        """Analyze market data and execute trades if conditions are met."""
        logger.debug("Analyzing market data...")
        
        # Get chart data for all configured timeframes
        supported_assets = ["EURUSD", "GBPUSD", "USDJPY"]  # Example assets
        chart_data = await self.iq_service.get_multiple_chart_data(
            assets=supported_assets,
            timeframes=self.config.timeframes,
            count=100
        )
        
        # Analyze each asset
        for asset in supported_assets:
            try:
                await self._analyze_asset(asset, chart_data.get(asset, {}))
            except Exception as e:
                logger.error(f"Error analyzing asset {asset}: {e}")
    
    async def _analyze_asset(self, asset: str, asset_chart_data: Dict[str, ChartData]):
        """Analyze a specific asset and make trading decision."""
        if not asset_chart_data:
            logger.warning(f"No chart data for {asset}")
            return
        
        # Calculate indicators for each timeframe
        indicators_data = {}
        market_data = {}
        
        for timeframe, chart_data in asset_chart_data.items():
            if not chart_data or not chart_data.candles:
                continue
                
            # Prepare price data
            closes = [candle.close for candle in chart_data.candles]
            volumes = [candle.volume for candle in chart_data.candles]
            
            market_data[timeframe] = {
                'candles': [candle.to_dict() for candle in chart_data.candles],
                'closes': closes,
                'volumes': volumes
            }
            
            # Calculate indicators
            timeframe_indicators = {}
            for name, indicator in self.indicators.items():
                try:
                    result = indicator.calculate(closes, volumes=volumes)
                    timeframe_indicators[name] = result
                    logger.debug(f"Calculated {name} for {asset} {timeframe}")
                except Exception as e:
                    logger.error(f"Error calculating {name} for {asset} {timeframe}: {e}")
            
            indicators_data[timeframe] = timeframe_indicators
        
        # Evaluate triggers
        signals = []
        for name, trigger in self.triggers.items():
            try:
                # Use primary timeframe (first in config) for trigger evaluation
                primary_tf = self.config.timeframes[0]
                if primary_tf in market_data and primary_tf in indicators_data:
                    signal = trigger.evaluate(
                        market_data[primary_tf], 
                        indicators_data[primary_tf]
                    )
                    signal['trigger_name'] = name
                    signal['asset'] = asset
                    signal['timeframe'] = primary_tf
                    signals.append(signal)
                    logger.debug(f"Trigger {name} signal for {asset}: {signal['action']} (confidence: {signal['confidence']})")
            except Exception as e:
                logger.error(f"Error evaluating trigger {name} for {asset}: {e}")
        
        # Make trading decision based on signals
        await self._make_trading_decision(asset, signals, market_data)
    
    async def _make_trading_decision(
        self, 
        asset: str, 
        signals: List[Dict[str, Any]], 
        market_data: Dict[str, Any]
    ):
        """Make final trading decision based on all signals."""
        if not signals:
            logger.debug(f"No signals for {asset}")
            return
        
        # Simple aggregation: use highest confidence signal
        best_signal = max(signals, key=lambda x: x['confidence'])
        
        min_confidence = 0.6  # Minimum confidence threshold
        if best_signal['confidence'] < min_confidence:
            logger.debug(f"Signal confidence too low for {asset}: {best_signal['confidence']}")
            return
        
        action = best_signal['action']
        if action in ['BUY', 'SELL']:
            await self._execute_trade(asset, action, best_signal)
    
    async def _execute_trade(self, asset: str, action: str, signal: Dict[str, Any]):
        """Execute a trade based on the signal."""
        try:
            # Calculate trade amount
            balance_str = self.config.balance
            balance_value = float(''.join(filter(str.isdigit, balance_str)))
            trade_amount = balance_value * self.config.trade_amount_ratio
            
            # Convert action to TradeDirection
            direction = TradeDirection.CALL if action == 'BUY' else TradeDirection.PUT
            
            # Create trade request
            trade_request = TradeRequest(
                asset=asset,
                direction=direction,
                amount=trade_amount,
                duration=60  # 1 minute trades
            )
            
            logger.info(f"Executing {action} trade for {asset}: ${trade_amount} (confidence: {signal['confidence']:.2f})")
            logger.info(f"Reason: {signal.get('reason', 'No reason provided')}")
            
            # Execute trade
            result = await self.iq_service.execute_trade(
                asset=trade_request.asset,
                direction=trade_request.direction,
                amount=trade_request.amount,
                duration=trade_request.duration
            )
            
            if result.get('success'):
                self.daily_trades += 1
                logger.info(f"Trade executed successfully: {result}")
                
                # In a real implementation, you would track the trade result
                # and update daily_losses if the trade was unsuccessful
            else:
                logger.error(f"Trade execution failed: {result}")
                
        except Exception as e:
            logger.error(f"Error executing trade for {asset}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "running": self.running,
            "daily_trades": self.daily_trades,
            "daily_losses": self.daily_losses,
            "max_daily_trades": self.config.max_daily_trades,
            "stop_after_losses": self.config.stop_after_losses,
            "last_trade_date": self.last_trade_date.isoformat() if self.last_trade_date else None,
            "loaded_indicators": list(self.indicators.keys()),
            "loaded_triggers": list(self.triggers.keys()),
            "loaded_news_feeds": list(self.news_feeds.keys()),
            "supported_assets": self.iq_service.get_supported_assets(),
            "chart_cache_stats": self.iq_service.get_chart_cache_stats()
        }