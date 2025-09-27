from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    FOREX = "forex"
    CRYPTO = "crypto"
    STOCKS = "stocks"
    COMMODITIES = "commodities"
    INDICES = "indices"


class TradeDirection(str, Enum):
    CALL = "call"  # Bullish
    PUT = "put"   # Bearish


class TradeStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class MarketData(BaseModel):
    asset: str
    price: float
    timestamp: datetime
    volume: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None


class TradeRequest(BaseModel):
    asset: str
    direction: TradeDirection
    amount: float
    duration: int  # in seconds
    risk_level: float = Field(ge=0.0, le=1.0, default=0.5)


class TradeResponse(BaseModel):
    trade_id: str
    asset: str
    direction: TradeDirection
    amount: float
    entry_price: float
    exit_price: Optional[float] = None
    status: TradeStatus
    profit: Optional[float] = None
    created_at: datetime
    closed_at: Optional[datetime] = None


class LLMResponse(BaseModel):
    decision: TradeDirection
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    time_frame: str  # e.g., "1m", "5m", "15m"


class TradingStrategy(BaseModel):
    name: str
    description: str
    parameters: dict
    active: bool = True