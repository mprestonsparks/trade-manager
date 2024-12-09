"""
Pydantic models for the trade manager API.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeRequest(BaseModel):
    """Model for trade execution requests"""
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType = OrderType.MARKET
    price: Optional[float] = None  # Required for LIMIT and STOP_LIMIT orders
    stop_price: Optional[float] = None  # Required for STOP and STOP_LIMIT orders
    time_in_force: str = "DAY"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TradeResponse(BaseModel):
    """Model for trade execution responses"""
    trade_id: str
    status: str
    timestamp: datetime
    details: Dict[str, Any]

class PositionInfo(BaseModel):
    """Model for position information"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    pnl: float
    timestamp: datetime

class SystemStatus(BaseModel):
    """Model for system status information"""
    status: str
    timestamp: datetime
    components: Dict[str, str]

class OrderStatus(BaseModel):
    """Model for order status information"""
    order_id: str
    status: str
    filled_quantity: float
    remaining_quantity: float
    average_price: float
    timestamp: datetime

class OpportunityResult(BaseModel):
    """Model for opportunity processing results"""
    opportunity_id: str
    status: str
    trade_id: Optional[str] = None
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
