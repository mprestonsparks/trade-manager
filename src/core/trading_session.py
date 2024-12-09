"""
Trading session class that coordinates the interaction between
system components using dependency injection.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.system_state import SystemState
from ..core.trade_engine import TradeEngine
from ..strategy.portfolio_optimizer import UnifiedOptimizer
from ..brokers.base_broker import BaseBroker
from ..config.trading_config import get_default_config, validate_config

logger = logging.getLogger(__name__)

class TradingSession:
    """
    Manages a trading session with injected dependencies.
    
    This class coordinates the interaction between the broker,
    system state, optimizer, and trade engine components.
    """
    
    def __init__(
        self,
        broker: BaseBroker,
        config: Optional[Dict[str, Any]] = None,
        system_state: Optional[SystemState] = None,
        optimizer: Optional[UnifiedOptimizer] = None,
        trade_engine: Optional[TradeEngine] = None
    ):
        """
        Initialize trading session with dependencies.
        
        Args:
            broker: Broker implementation
            config: Optional configuration dictionary
            system_state: Optional system state instance
            optimizer: Optional optimizer instance
            trade_engine: Optional trade engine instance
        """
        self.config = config or get_default_config()
        if not validate_config(self.config):
            raise ValueError("Invalid configuration")
            
        self.broker = broker
        self.system_state = system_state or SystemState()
        self.optimizer = optimizer or UnifiedOptimizer(self.config)
        self.trade_engine = trade_engine or TradeEngine(
            self.config,
            self.system_state,
            self.optimizer
        )
        
        self.running = False
        self.symbols: List[str] = []
        
    async def start(self, symbols: List[str]):
        """
        Start the trading session.
        
        Args:
            symbols: List of symbols to trade
        """
        self.symbols = symbols
        self.running = True
        
        try:
            async with self.broker:
                if not await self._initialize():
                    return
                    
                await self._run_trading_loop()
                
        except Exception as e:
            logger.error(f"Fatal error in trading session: {str(e)}")
        finally:
            self.running = False
            
    async def stop(self):
        """Stop the trading session."""
        self.running = False
        
    async def _initialize(self) -> bool:
        """
        Initialize the trading session.
        
        Returns:
            True if initialization successful
        """
        if not self.broker.connected:
            logger.error("Failed to connect to broker")
            return False
            
        logger.info("Trading session initialized")
        return True
        
    async def _run_trading_loop(self):
        """Run the main trading loop."""
        while self.running:
            try:
                # Update market data
                market_data = {}
                for symbol in self.symbols:
                    data = await self.broker.get_market_data(symbol)
                    if data:
                        market_data[symbol] = data
                        
                if not market_data:
                    logger.warning("No market data received")
                    continue
                    
                # Update system state
                self.system_state.update_market_data(market_data)
                
                # Update positions and portfolio
                positions = await self.broker.get_positions()
                portfolio = await self.broker.get_portfolio()
                
                self.system_state.update_positions(positions)
                self.system_state.update_portfolio(portfolio)
                
                # Run optimization
                optimized_params = self.optimizer.optimize(self.system_state)
                
                # Generate and execute trading decisions
                actions = self.trade_engine.process_state(optimized_params)
                await self._execute_actions(actions)
                
                # Wait for next iteration
                await asyncio.sleep(self.config['market_analysis']['update_interval'])
                
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                await asyncio.sleep(5)
                
    async def _execute_actions(self, actions: List[Dict[str, Any]]):
        """
        Execute trading actions.
        
        Args:
            actions: List of trading actions to execute
        """
        for action in actions:
            if action['type'] == 'ORDER':
                trade = await self.broker.place_order(
                    symbol=action['symbol'],
                    quantity=action['quantity'],
                    order_type=action['order_type'],
                    limit_price=action.get('limit_price'),
                    stop_price=action.get('stop_price')
                )
                
                if trade:
                    logger.info(f"Executed trade: {action}")
                else:
                    logger.warning(f"Failed to execute trade: {action}")
                    error = self.broker.get_last_error()
                    if error:
                        logger.error(f"Broker error: {error}")
