"""
Abstract base class for broker adapters.
Defines the interface that all broker implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

class BaseBroker(ABC):
    """Abstract base class for broker implementations."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the broker.
        
        Returns:
            True if connection successful
        """
        pass
        
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the broker."""
        pass
        
    @abstractmethod
    async def place_order(
        self, 
        symbol: str, 
        quantity: int, 
        order_type: str = 'MKT',
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = 'DAY'
    ) -> Optional[Any]:
        """
        Place an order with the broker.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity (positive for buy, negative for sell)
            order_type: Order type (MKT, LMT, STP)
            limit_price: Limit price for LMT orders
            stop_price: Stop price for STP orders
            time_in_force: Order time in force
            
        Returns:
            Trade object if successful, None otherwise
        """
        pass
        
    @abstractmethod
    async def get_positions(self) -> List[Any]:
        """
        Get current positions.
        
        Returns:
            List of Position objects
        """
        pass
        
    @abstractmethod
    async def get_portfolio(self) -> List[Any]:
        """
        Get current portfolio state.
        
        Returns:
            List of PortfolioItem objects
        """
        pass
        
    @abstractmethod
    async def cancel_order(self, trade: Any) -> bool:
        """
        Cancel an open order.
        
        Args:
            trade: Trade object to cancel
            
        Returns:
            True if cancellation successful
        """
        pass
        
    @abstractmethod
    async def get_market_data(
        self, 
        symbol: str,
        data_type: str = 'TRADES'
    ) -> Optional[Dict[str, Any]]:
        """
        Get real-time market data for a symbol.
        
        Args:
            symbol: Trading symbol
            data_type: Type of market data to request
            
        Returns:
            Dictionary with market data if successful
        """
        pass
        
    @abstractmethod
    def get_last_error(self) -> Optional[str]:
        """
        Get the last error message.
        
        Returns:
            Last error message or None
        """
        pass
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
