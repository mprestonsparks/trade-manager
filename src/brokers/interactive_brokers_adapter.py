"""
Interactive Brokers adapter for executing trades and managing positions.
Handles communication with IB API using ib_insync library.
"""

from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
import asyncio
import logging
from datetime import datetime, timedelta

from ib_insync import IB, Contract, Order, Trade, Position, PortfolioItem
from ib_insync.order import MarketOrder, LimitOrder, StopOrder

from ..config.trading_config import get_default_config
from ..core.system_state import SystemState
from .base_broker import BaseBroker

logger = logging.getLogger(__name__)

class InteractiveBrokersAdapter(BaseBroker):
    """Adapter for Interactive Brokers API integration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize IB adapter with configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or get_default_config()['interactive_brokers']
        self.ib = IB()
        self.connected = False
        self._last_error = None
        self._order_callbacks = {}
        
    async def connect(self) -> bool:
        """
        Connect to Interactive Brokers TWS/Gateway.
        
        Returns:
            True if connection successful
        """
        try:
            port = self.config['port']
            client_id = self.config['client_id']
            
            for attempt in range(self.config['max_retries']):
                try:
                    await self.ib.connectAsync(
                        'localhost', 
                        port, 
                        clientId=client_id,
                        timeout=self.config['timeout']
                    )
                    self.connected = True
                    logger.info(f"Connected to IB on port {port}")
                    
                    # Set up error handling
                    self.ib.errorEvent += self._handle_error
                    
                    return True
                    
                except Exception as e:
                    logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                    await asyncio.sleep(self.config['retry_delay'])
            
            return False
            
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Failed to connect to IB: {str(e)}")
            return False
            
    async def disconnect(self):
        """Disconnect from IB."""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IB")
            
    def _handle_error(self, reqId: int, errorCode: int, errorString: str, contract: Contract):
        """
        Handle IB API errors.
        
        Args:
            reqId: Request ID
            errorCode: IB error code
            errorString: Error message
            contract: Associated contract if any
        """
        self._last_error = f"IB Error {errorCode}: {errorString}"
        logger.error(self._last_error)
        
        # Handle specific error codes
        if errorCode in [1100, 1101, 1102]:  # Connection-related errors
            self.connected = False
            
    async def place_order(
        self, 
        symbol: str, 
        quantity: int, 
        order_type: str = 'MKT',
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = 'DAY'
    ) -> Optional[Trade]:
        """
        Place an order with Interactive Brokers.
        
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
        if not self.connected:
            logger.error("Not connected to IB")
            return None
            
        try:
            # Create contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = 'STK'
            contract.exchange = 'SMART'
            contract.currency = 'USD'
            
            # Create order based on type
            if order_type == 'MKT':
                order = MarketOrder('BUY' if quantity > 0 else 'SELL', abs(quantity))
            elif order_type == 'LMT' and limit_price is not None:
                order = LimitOrder('BUY' if quantity > 0 else 'SELL', abs(quantity), limit_price)
            elif order_type == 'STP' and stop_price is not None:
                order = StopOrder('BUY' if quantity > 0 else 'SELL', abs(quantity), stop_price)
            else:
                raise ValueError(f"Invalid order type or missing price: {order_type}")
                
            order.tif = time_in_force
            
            # Place order
            trade = self.ib.placeOrder(contract, order)
            logger.info(f"Placed {order_type} order for {quantity} {symbol}")
            
            return trade
            
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Error placing order: {str(e)}")
            return None
            
    async def get_positions(self) -> List[Position]:
        """
        Get current positions.
        
        Returns:
            List of Position objects
        """
        if not self.connected:
            return []
            
        try:
            positions = self.ib.positions()
            return positions
            
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Error getting positions: {str(e)}")
            return []
            
    async def get_portfolio(self) -> List[PortfolioItem]:
        """
        Get current portfolio state.
        
        Returns:
            List of PortfolioItem objects
        """
        if not self.connected:
            return []
            
        try:
            portfolio = self.ib.portfolio()
            return portfolio
            
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Error getting portfolio: {str(e)}")
            return []
            
    async def cancel_order(self, trade: Trade) -> bool:
        """
        Cancel an open order.
        
        Args:
            trade: Trade object to cancel
            
        Returns:
            True if cancellation successful
        """
        if not self.connected:
            return False
            
        try:
            self.ib.cancelOrder(trade.order)
            logger.info(f"Cancelled order: {trade.order.orderId}")
            return True
            
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Error cancelling order: {str(e)}")
            return False
            
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
        if not self.connected:
            return None
            
        try:
            contract = Contract()
            contract.symbol = symbol
            contract.secType = 'STK'
            contract.exchange = 'SMART'
            contract.currency = 'USD'
            
            self.ib.reqMktData(contract, '', False, False)
            
            # Wait for data
            ticker = self.ib.ticker(contract)
            await asyncio.sleep(0.5)  # Allow time for data to arrive
            
            return {
                'last_price': ticker.last,
                'bid': ticker.bid,
                'ask': ticker.ask,
                'volume': ticker.volume,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Error getting market data: {str(e)}")
            return None
            
    def get_last_error(self) -> Optional[str]:
        """
        Get the last error message.
        
        Returns:
            Last error message or None
        """
        return self._last_error
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
