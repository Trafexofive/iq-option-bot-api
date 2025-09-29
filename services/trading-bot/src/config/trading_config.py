"""Trading configuration models and parser for YAML-based trading settings."""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import time
import yaml
import os
from pathlib import Path


class TradingHours(BaseModel):
    start: str = Field(..., description="Trading start time in HH:MM format")
    end: str = Field(..., description="Trading end time in HH:MM format")
    
    @validator('start', 'end')
    def validate_time_format(cls, v):
        try:
            time.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid time format: {v}. Use HH:MM format.")


class TradingConfig(BaseModel):
    max_daily_trades: int = Field(default=5, ge=1)
    balance: str = Field(default="10$", description="Starting balance with currency symbol")
    wake_interval: str = Field(default="2m", description="Sync interval for chart timeframe")
    stop_after_losses: int = Field(default=1, ge=1)
    trade_amount_ratio: float = Field(default=0.1, ge=0.01, le=1.0)
    win_amount_multiplier: float = Field(default=1.7, ge=1.0)
    trading_hours: Optional[TradingHours] = None
    trading_sessions: Optional[List[str]] = Field(default=None, description="Trading sessions like London, New York, Tokyo")
    timeframes: List[str] = Field(default=["M1", "M5", "M15"], description="Chart timeframes")
    context_feeds: List[str] = Field(default=[], description="Context feeds for LLM")
    triggers: List[str] = Field(default=[], description="Trading triggers")
    
    @validator('balance')
    def validate_balance(cls, v):
        # Extract numeric value and currency
        if not any(c.isdigit() for c in v):
            raise ValueError("Balance must contain a numeric value")
        return v
    
    @validator('wake_interval')
    def validate_wake_interval(cls, v):
        # Basic validation for interval format (e.g., "2m", "30s", "1h")
        if not v[-1] in ['s', 'm', 'h']:
            raise ValueError("Wake interval must end with 's' (seconds), 'm' (minutes), or 'h' (hours)")
        try:
            int(v[:-1])
        except ValueError:
            raise ValueError("Wake interval must start with a number")
        return v


class IQOptionConfig(BaseModel):
    demo_mode: bool = Field(default=True)
    api_timeout: int = Field(default=30, ge=1)
    credentials_file: Optional[str] = None


class LoggingConfig(BaseModel):
    level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL|VERBOSE)$")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class AppConfig(BaseModel):
    name: str = Field(default="IQ Option Bot API")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)


class DatabaseConfig(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=5432, ge=1, le=65535)
    name: str = Field(default="trading_bot")
    user: str = Field(default="user")
    password: str = Field(default="password")


class RedisConfig(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=6379, ge=1, le=65535)
    db: int = Field(default=0, ge=0)


class LLMGatewayConfig(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=8001, ge=1, le=65535)
    timeout: int = Field(default=30, ge=1)


class FullConfig(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    llm_gateway: LLMGatewayConfig = Field(default_factory=LLMGatewayConfig)
    trading: TradingConfig = Field(default_factory=TradingConfig)
    iq_option: IQOptionConfig = Field(default_factory=IQOptionConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


class TradingConfigParser:
    """Parser for trading configuration from YAML files."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self._config: Optional[FullConfig] = None
    
    def _find_config_file(self) -> str:
        """Find the configuration file in common locations."""
        possible_paths = [
            "settings.yml",
            "config.yml",
            "../../../settings.yml",  # From trading-bot service to root
            os.path.expanduser("~/.iq-option-bot/settings.yml"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If no config file found, create a default one
        default_path = "settings.yml"
        self._create_default_config(default_path)
        return default_path
    
    def _create_default_config(self, path: str):
        """Create a default configuration file."""
        default_config = FullConfig()
        with open(path, 'w') as f:
            # Convert to dict and write as YAML
            yaml.dump(default_config.dict(), f, default_flow_style=False, indent=2)
    
    def load_config(self) -> FullConfig:
        """Load configuration from YAML file."""
        if self._config is None:
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                self._config = FullConfig(**data)
            except FileNotFoundError:
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML configuration: {e}")
            except Exception as e:
                raise ValueError(f"Error loading configuration: {e}")
        
        return self._config
    
    def save_config(self, config: FullConfig):
        """Save configuration to YAML file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(config.dict(), f, default_flow_style=False, indent=2)
        self._config = config
    
    def get_trading_config(self) -> TradingConfig:
        """Get the trading configuration section."""
        return self.load_config().trading
    
    def get_iq_option_config(self) -> IQOptionConfig:
        """Get the IQ Option configuration section."""
        return self.load_config().iq_option
    
    def validate_context_feeds(self, trading_config: TradingConfig) -> List[str]:
        """Validate and resolve context feeds (builtin and custom)."""
        builtin_indicators = {"RSI", "MACD", "BollingerBands", "SMA", "EMA", "STOCH"}
        builtin_triggers = {"PriceActionTrigger", "VolumeSpikeTrigger", "MomentumTrigger"}
        
        validated_feeds = []
        
        for feed in trading_config.context_feeds:
            if feed in builtin_indicators:
                validated_feeds.append(feed)
            elif feed.endswith('.yml') or feed.endswith('.yaml'):
                # Custom manifest file
                if os.path.exists(feed):
                    validated_feeds.append(feed)
                else:
                    print(f"Warning: Custom manifest file not found: {feed}")
            else:
                print(f"Warning: Unknown context feed: {feed}")
        
        return validated_feeds
    
    def validate_triggers(self, trading_config: TradingConfig) -> List[str]:
        """Validate and resolve triggers (builtin and custom)."""
        builtin_triggers = {"PriceActionTrigger", "VolumeSpikeTrigger", "MomentumTrigger"}
        
        validated_triggers = []
        
        for trigger in trading_config.triggers:
            if trigger in builtin_triggers:
                validated_triggers.append(trigger)
            elif trigger.endswith('.yml') or trigger.endswith('.yaml'):
                # Custom manifest file
                if os.path.exists(trigger):
                    validated_triggers.append(trigger)
                else:
                    print(f"Warning: Custom trigger file not found: {trigger}")
            else:
                print(f"Warning: Unknown trigger: {trigger}")
        
        return validated_triggers


# Global configuration instance
config_parser = TradingConfigParser()