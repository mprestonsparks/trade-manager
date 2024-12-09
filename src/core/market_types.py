"""
Market-related data types shared across the trade manager.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

@dataclass
class MarketState:
    """Current state of the market from market-analysis service"""
    symbol: str
    state_id: int
    description: str
    characteristics: Dict[str, float]  # Contains PCA state components
    confidence: float
    current_price: Decimal
    bid_price: Decimal
    ask_price: Decimal
    volume: int
    timestamp: datetime
    metadata: Dict[str, Any]
