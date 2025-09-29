"""Manifest system for custom indicators, triggers, and news feeds."""

import yaml
import json
import importlib
import logging
from typing import Dict, Any, List, Optional, Type, Callable
from pathlib import Path
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class ManifestType(str, Enum):
    INDICATOR = "indicator"
    TRIGGER = "trigger" 
    NEWS_FEED = "news_feed"


class ManifestBase(BaseModel):
    """Base class for all manifest configurations."""
    name: str = Field(..., description="Name of the component")
    version: str = Field(..., description="Version of the component")
    description: str = Field(..., description="Description of the component")
    author: Optional[str] = Field(None, description="Author of the component")
    type: ManifestType = Field(..., description="Type of component")
    
    
class IndicatorManifest(ManifestBase):
    """Manifest for custom indicators."""
    type: ManifestType = Field(default=ManifestType.INDICATOR)
    implementation: str = Field(..., description="Python module path or class name")
    parameters: Dict[str, Any] = Field(default={}, description="Default parameters")
    inputs: List[str] = Field(default=["close"], description="Required price inputs")
    outputs: List[str] = Field(..., description="Output values")
    timeframe_support: List[str] = Field(default=["M1", "M5", "M15", "M30", "H1"], description="Supported timeframes")
    
    
class TriggerManifest(ManifestBase):
    """Manifest for custom triggers."""
    type: ManifestType = Field(default=ManifestType.TRIGGER)
    implementation: str = Field(..., description="Python module path or class name")
    parameters: Dict[str, Any] = Field(default={}, description="Default parameters")
    conditions: List[str] = Field(..., description="Trigger conditions")
    actions: List[str] = Field(default=["BUY", "SELL", "HOLD"], description="Possible actions")
    required_indicators: List[str] = Field(default=[], description="Required indicators")
    

class NewsFeedManifest(ManifestBase):
    """Manifest for custom news feeds."""
    type: ManifestType = Field(default=ManifestType.NEWS_FEED)
    implementation: str = Field(..., description="Python module path or class name")
    parameters: Dict[str, Any] = Field(default={}, description="Default parameters")
    source_url: Optional[str] = Field(None, description="News source URL")
    update_interval: str = Field(default="5m", description="Update interval")
    sentiment_analysis: bool = Field(default=True, description="Enable sentiment analysis")
    keywords: List[str] = Field(default=[], description="Keywords to filter news")


class BaseIndicator(ABC):
    """Base class for custom indicators."""
    
    def __init__(self, parameters: Dict[str, Any]):
        self.parameters = parameters
        self.name = self.__class__.__name__
    
    @abstractmethod
    def calculate(self, data: List[float], **kwargs) -> Dict[str, List[float]]:
        """Calculate indicator values."""
        pass
    
    def get_required_lookback(self) -> int:
        """Get minimum number of data points required."""
        return 20  # Default lookback period


class BaseTrigger(ABC):
    """Base class for custom triggers."""
    
    def __init__(self, parameters: Dict[str, Any]):
        self.parameters = parameters
        self.name = self.__class__.__name__
    
    @abstractmethod
    def evaluate(self, market_data: Dict[str, Any], indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate trigger conditions."""
        pass


class BaseNewsFeed(ABC):
    """Base class for custom news feeds."""
    
    def __init__(self, parameters: Dict[str, Any]):
        self.parameters = parameters
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def fetch_news(self) -> List[Dict[str, Any]]:
        """Fetch latest news."""
        pass
    
    @abstractmethod
    def analyze_sentiment(self, news_text: str) -> float:
        """Analyze sentiment of news text. Returns score between -1 and 1."""
        pass


class ManifestLoader:
    """Loader for YAML manifests and dynamic component instantiation."""
    
    def __init__(self):
        self.loaded_manifests: Dict[str, Any] = {}
        self.loaded_components: Dict[str, Any] = {}
    
    def load_manifest_from_file(self, file_path: str) -> Optional[ManifestBase]:
        """Load manifest from YAML file."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"Manifest file not found: {file_path}")
                return None
            
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Determine manifest type and create appropriate object
            manifest_type = data.get('type')
            if manifest_type == ManifestType.INDICATOR:
                manifest = IndicatorManifest(**data)
            elif manifest_type == ManifestType.TRIGGER:
                manifest = TriggerManifest(**data)
            elif manifest_type == ManifestType.NEWS_FEED:
                manifest = NewsFeedManifest(**data)
            else:
                logger.error(f"Unknown manifest type: {manifest_type}")
                return None
            
            self.loaded_manifests[manifest.name] = manifest
            logger.info(f"Loaded manifest: {manifest.name} ({manifest.type})")
            return manifest
            
        except Exception as e:
            logger.error(f"Error loading manifest from {file_path}: {e}")
            return None
    
    def load_component(self, manifest: ManifestBase) -> Optional[Any]:
        """Load and instantiate component from manifest."""
        try:
            # Check if already loaded
            if manifest.name in self.loaded_components:
                return self.loaded_components[manifest.name]
            
            # Import the implementation
            if '.' in manifest.implementation:
                # Module path
                module_path, class_name = manifest.implementation.rsplit('.', 1)
                module = importlib.import_module(module_path)
                component_class = getattr(module, class_name)
            else:
                # Assume it's a class name in current context
                # This is for built-in components
                component_class = self._get_builtin_component(manifest.implementation, manifest.type)
            
            if not component_class:
                logger.error(f"Component class not found: {manifest.implementation}")
                return None
            
            # Instantiate the component
            component = component_class(manifest.parameters)
            self.loaded_components[manifest.name] = component
            
            logger.info(f"Loaded component: {manifest.name}")
            return component
            
        except Exception as e:
            logger.error(f"Error loading component {manifest.name}: {e}")
            return None
    
    def _get_builtin_component(self, name: str, component_type: ManifestType) -> Optional[Type]:
        """Get built-in component classes."""
        builtin_indicators = {
            "RSI": RSIIndicator,
            "MACD": MACDIndicator,
            "BollingerBands": BollingerBandsIndicator,
            "SMA": SMAIndicator,
            "EMA": EMAIndicator,
        }
        
        builtin_triggers = {
            "PriceActionTrigger": PriceActionTrigger,
            "VolumeSpikeTrigger": VolumeSpikeTrigger,
            "MomentumTrigger": MomentumTrigger,
        }
        
        if component_type == ManifestType.INDICATOR:
            return builtin_indicators.get(name)
        elif component_type == ManifestType.TRIGGER:
            return builtin_triggers.get(name)
        
        return None
    
    def load_all_manifests(self, directory: str) -> List[ManifestBase]:
        """Load all manifests from a directory."""
        manifests = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            logger.warning(f"Manifest directory not found: {directory}")
            return manifests
        
        # Find all YAML files
        for yaml_file in directory_path.glob("*.yml"):
            manifest = self.load_manifest_from_file(str(yaml_file))
            if manifest:
                manifests.append(manifest)
        
        for yaml_file in directory_path.glob("*.yaml"):
            manifest = self.load_manifest_from_file(str(yaml_file))
            if manifest:
                manifests.append(manifest)
        
        return manifests


# Built-in Indicator Implementations
class RSIIndicator(BaseIndicator):
    """Relative Strength Index indicator."""
    
    def calculate(self, data: List[float], **kwargs) -> Dict[str, List[float]]:
        period = self.parameters.get('period', 14)
        
        if len(data) < period + 1:
            return {"rsi": []}
        
        # Calculate price changes
        deltas = [data[i] - data[i-1] for i in range(1, len(data))]
        
        # Separate gains and losses
        gains = [max(delta, 0) for delta in deltas]
        losses = [abs(min(delta, 0)) for delta in deltas]
        
        rsi_values = []
        
        # Calculate initial averages
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        for i in range(period, len(gains)):
            # Smoothed averages
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return {"rsi": rsi_values}


class MACDIndicator(BaseIndicator):
    """MACD (Moving Average Convergence Divergence) indicator."""
    
    def calculate(self, data: List[float], **kwargs) -> Dict[str, List[float]]:
        fast_period = self.parameters.get('fast_period', 12)
        slow_period = self.parameters.get('slow_period', 26)
        signal_period = self.parameters.get('signal_period', 9)
        
        if len(data) < slow_period:
            return {"macd": [], "signal": [], "histogram": []}
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(data, fast_period)
        slow_ema = self._calculate_ema(data, slow_period)
        
        # Calculate MACD line
        min_length = min(len(fast_ema), len(slow_ema))
        macd_line = [fast_ema[i] - slow_ema[i] for i in range(min_length)]
        
        # Calculate Signal line (EMA of MACD)
        signal_line = self._calculate_ema(macd_line, signal_period)
        
        # Calculate Histogram
        min_length = min(len(macd_line), len(signal_line))
        histogram = [macd_line[i] - signal_line[i] for i in range(min_length)]
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    def _calculate_ema(self, data: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average."""
        if len(data) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = []
        
        # Start with SMA for first value
        sma = sum(data[:period]) / period
        ema_values.append(sma)
        
        # Calculate EMA for remaining values
        for i in range(period, len(data)):
            ema = (data[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values


class BollingerBandsIndicator(BaseIndicator):
    """Bollinger Bands indicator."""
    
    def calculate(self, data: List[float], **kwargs) -> Dict[str, List[float]]:
        period = self.parameters.get('period', 20)
        std_dev = self.parameters.get('std_dev', 2)
        
        if len(data) < period:
            return {"upper": [], "middle": [], "lower": []}
        
        upper_band = []
        middle_band = []
        lower_band = []
        
        for i in range(period - 1, len(data)):
            # Calculate SMA (middle band)
            sma = sum(data[i-period+1:i+1]) / period
            
            # Calculate standard deviation
            variance = sum((x - sma) ** 2 for x in data[i-period+1:i+1]) / period
            std = variance ** 0.5
            
            upper_band.append(sma + (std_dev * std))
            middle_band.append(sma)
            lower_band.append(sma - (std_dev * std))
        
        return {
            "upper": upper_band,
            "middle": middle_band,
            "lower": lower_band
        }


class SMAIndicator(BaseIndicator):
    """Simple Moving Average indicator."""
    
    def calculate(self, data: List[float], **kwargs) -> Dict[str, List[float]]:
        period = self.parameters.get('period', 20)
        
        if len(data) < period:
            return {"sma": []}
        
        sma_values = []
        for i in range(period - 1, len(data)):
            sma = sum(data[i-period+1:i+1]) / period
            sma_values.append(sma)
        
        return {"sma": sma_values}


class EMAIndicator(BaseIndicator):
    """Exponential Moving Average indicator."""
    
    def calculate(self, data: List[float], **kwargs) -> Dict[str, List[float]]:
        period = self.parameters.get('period', 20)
        
        if len(data) < period:
            return {"ema": []}
        
        multiplier = 2 / (period + 1)
        ema_values = []
        
        # Start with SMA
        sma = sum(data[:period]) / period
        ema_values.append(sma)
        
        # Calculate EMA
        for i in range(period, len(data)):
            ema = (data[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return {"ema": ema_values}


# Built-in Trigger Implementations
class PriceActionTrigger(BaseTrigger):
    """Price action based trigger."""
    
    def evaluate(self, market_data: Dict[str, Any], indicators: Dict[str, Any]) -> Dict[str, Any]:
        # Simple price action logic
        candles = market_data.get('candles', [])
        if len(candles) < 3:
            return {"action": "HOLD", "confidence": 0.0, "reason": "Insufficient data"}
        
        # Get last 3 candles
        recent_candles = candles[-3:]
        
        # Bullish pattern: 3 consecutive higher closes
        if all(recent_candles[i]['close'] > recent_candles[i-1]['close'] for i in range(1, 3)):
            return {
                "action": "BUY",
                "confidence": 0.7,
                "reason": "Bullish price action - consecutive higher closes"
            }
        
        # Bearish pattern: 3 consecutive lower closes
        if all(recent_candles[i]['close'] < recent_candles[i-1]['close'] for i in range(1, 3)):
            return {
                "action": "SELL", 
                "confidence": 0.7,
                "reason": "Bearish price action - consecutive lower closes"
            }
        
        return {"action": "HOLD", "confidence": 0.5, "reason": "No clear price action signal"}


class VolumeSpikeTrigger(BaseTrigger):
    """Volume spike based trigger."""
    
    def evaluate(self, market_data: Dict[str, Any], indicators: Dict[str, Any]) -> Dict[str, Any]:
        candles = market_data.get('candles', [])
        if len(candles) < 20:
            return {"action": "HOLD", "confidence": 0.0, "reason": "Insufficient data"}
        
        # Calculate average volume over last 20 periods
        volumes = [candle['volume'] for candle in candles[-20:]]
        avg_volume = sum(volumes) / len(volumes)
        
        current_volume = candles[-1]['volume']
        current_close = candles[-1]['close'] 
        previous_close = candles[-2]['close']
        
        # Volume spike threshold
        spike_threshold = self.parameters.get('spike_threshold', 2.0)
        
        if current_volume > avg_volume * spike_threshold:
            if current_close > previous_close:
                return {
                    "action": "BUY",
                    "confidence": 0.8,
                    "reason": f"Volume spike with bullish price movement (Volume: {current_volume:.0f} vs Avg: {avg_volume:.0f})"
                }
            else:
                return {
                    "action": "SELL",
                    "confidence": 0.8, 
                    "reason": f"Volume spike with bearish price movement (Volume: {current_volume:.0f} vs Avg: {avg_volume:.0f})"
                }
        
        return {"action": "HOLD", "confidence": 0.3, "reason": "No significant volume spike"}


class MomentumTrigger(BaseTrigger):
    """Momentum based trigger using RSI and MACD."""
    
    def evaluate(self, market_data: Dict[str, Any], indicators: Dict[str, Any]) -> Dict[str, Any]:
        rsi_data = indicators.get('RSI', {})
        macd_data = indicators.get('MACD', {})
        
        if not rsi_data or not macd_data:
            return {"action": "HOLD", "confidence": 0.0, "reason": "Missing indicator data"}
        
        rsi_values = rsi_data.get('rsi', [])
        macd_values = macd_data.get('macd', [])
        signal_values = macd_data.get('signal', [])
        
        if not rsi_values or not macd_values or not signal_values:
            return {"action": "HOLD", "confidence": 0.0, "reason": "Insufficient indicator data"}
        
        current_rsi = rsi_values[-1]
        current_macd = macd_values[-1]
        current_signal = signal_values[-1]
        
        overbought_level = self.parameters.get('rsi_overbought', 70)
        oversold_level = self.parameters.get('rsi_oversold', 30)
        
        # Bullish momentum
        if current_rsi < oversold_level and current_macd > current_signal:
            return {
                "action": "BUY",
                "confidence": 0.8,
                "reason": f"Bullish momentum: RSI oversold ({current_rsi:.1f}) + MACD bullish crossover"
            }
        
        # Bearish momentum  
        if current_rsi > overbought_level and current_macd < current_signal:
            return {
                "action": "SELL",
                "confidence": 0.8,
                "reason": f"Bearish momentum: RSI overbought ({current_rsi:.1f}) + MACD bearish crossover"
            }
        
        return {"action": "HOLD", "confidence": 0.4, "reason": "No clear momentum signal"}


# Global manifest loader instance
manifest_loader = ManifestLoader()