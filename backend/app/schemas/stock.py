# backend/app/schemas/stock.py
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ActionEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class RiskLevelEnum(str, Enum):
    LOW = "Low"
    LOW_MEDIUM = "Low-Medium"
    MEDIUM = "Medium"
    MEDIUM_HIGH = "Medium-High"
    HIGH = "High"

# Request schemas
class WatchlistRequest(BaseModel):
    symbol: str
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Symbol cannot be empty')
        if len(v.strip()) > 10:
            raise ValueError('Symbol too long')
        return v.upper().strip()

class RecommendationRequest(BaseModel):
    confidence_threshold: Optional[int] = 50
    max_recommendations: Optional[int] = 5
    
    @validator('confidence_threshold')
    def validate_confidence(cls, v):
        if v < 20 or v > 90:
            raise ValueError('Confidence threshold must be between 20 and 90')
        return v
    
    @validator('max_recommendations')
    def validate_max_recs(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Max recommendations must be between 1 and 10')
        return v

# Response schemas
class StockQuote(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: str
    volume: int
    latest_trading_day: Optional[str] = None
    timestamp: datetime

class TechnicalIndicators(BaseModel):
    rsi: Optional[float] = None
    volume: Optional[str] = None
    support: Optional[float] = None
    resistance: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None

class MarketData(BaseModel):
    change: float
    change_percent: float
    volume: int
    previous_close: Optional[float] = None

class Recommendation(BaseModel):
    symbol: str
    company: str
    action: ActionEnum
    current_price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    confidence: int
    timeframe: Optional[str] = None
    risk_level: Optional[RiskLevelEnum] = None
    reasoning: List[str] = []
    technicals: Optional[TechnicalIndicators] = None
    market_data: Optional[MarketData] = None
    generated_at: datetime
    expires_at: Optional[datetime] = None

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
    generated_at: datetime
    market_status: str = "open"
    count: int
    parameters: Dict[str, Any]
    error: Optional[str] = None

class WatchlistResponse(BaseModel):
    watchlist: List[str]
    count: int

class DatabaseStats(BaseModel):
    total_stocks: int
    total_recommendations: int
    total_prices: int
    watchlist_size: int
    last_updated: datetime

# Error responses
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

# Historical data schemas
class HistoricalRecommendation(BaseModel):
    id: str
    symbol: str
    action: ActionEnum
    current_price: float
    target_price: Optional[float]
    confidence: int
    reasoning: List[str]
    generated_at: datetime
    is_active: bool

class HistoricalResponse(BaseModel):
    recommendations: List[HistoricalRecommendation]
    count: int
    retrieved_at: datetime