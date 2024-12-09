"""
Interactive Brokers Paper Trading Example
=======================================

This example demonstrates how to use the trade manager system with Interactive Brokers' paper trading
environment. Before running this example, ensure:

1. Interactive Brokers Trader Workstation (TWS) is running
2. Paper trading account is enabled in TWS
3. API connections are enabled in TWS (File -> Global Configuration -> API -> Settings)
4. The correct port is set (7497 for paper trading)

The example will:
1. Connect to IB's paper trading environment
2. Initialize the trading system components
3. Monitor a set of symbols
4. Execute trades based on system signals
5. Manage positions and risk
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.brokers.interactive_brokers_adapter import InteractiveBrokersAdapter
from src.core.trading_session import TradingSession
from src.core.system_state import SystemState
from src.core.portfolio import PortfolioManager
from src.core.risk_manager import RiskManager
from src.core.trade_engine import TradeEngine
from src.config.trading_config import get_default_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PaperTradingSession:
    """Manages the paper trading session with Interactive Brokers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize paper trading session.
        
        Args:
            config: Trading system configuration
        """
        self.config = config
        self.broker = None
        self.session = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize all trading components and establish connection."""
        try:
            # Initialize and connect broker
            logger.info("Connecting to Interactive Brokers paper trading...")
            self.broker = InteractiveBrokersAdapter(self.config)
            await self.broker.connect()
            
            # Initialize system components
            logger.info("Initializing trading system components...")
            system_state = SystemState(self.config)
            
            portfolio_manager = PortfolioManager(system_state, self.config)
            risk_manager = RiskManager(system_state, self.config)
            trade_engine = TradeEngine(system_state, self.config)
            
            # Create trading session
            self.session = TradingSession(
                broker=self.broker,
                system_state=system_state,
                portfolio_manager=portfolio_manager,
                risk_manager=risk_manager,
                trade_engine=trade_engine,
                config=self.config
            )
            
            logger.info("Trading system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize paper trading session: {str(e)}")
            await self.cleanup()
            raise
            
    async def start_trading(self, symbols: List[str]):
        """
        Start the paper trading session.
        
        Args:
            symbols: List of symbols to trade
        """
        try:
            if not self.session:
                raise RuntimeError("Trading session not initialized")
                
            logger.info(f"Starting paper trading for symbols: {symbols}")
            self.is_running = True
            
            # Start the trading session
            await self.session.start(symbols)
            
            # Monitor the session
            while self.is_running:
                # Check system health
                if not await self.broker.is_connected():
                    logger.error("Lost connection to Interactive Brokers")
                    break
                    
                # Add any additional monitoring logic here
                
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Error during trading session: {str(e)}")
        finally:
            await self.cleanup()
            
    async def cleanup(self):
        """Clean up resources and connections."""
        self.is_running = False
        
        if self.session:
            try:
                await self.session.stop()
            except Exception as e:
                logger.error(f"Error stopping trading session: {str(e)}")
                
        if self.broker:
            try:
                await self.broker.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting from broker: {str(e)}")
                
async def main():
    """Main entry point for paper trading example."""
    # Load configuration
    config = get_default_config()
    
    # Trading symbols (major tech stocks for example)
    symbols = [
        'AAPL',  # Apple
        'MSFT',  # Microsoft
        'GOOGL', # Alphabet
        'AMZN',  # Amazon
        'META'   # Meta Platforms
    ]
    
    # Create and run paper trading session
    paper_session = PaperTradingSession(config)
    
    try:
        await paper_session.initialize()
        await paper_session.start_trading(symbols)
    except KeyboardInterrupt:
        logger.info("Shutting down paper trading example")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
        
if __name__ == "__main__":
    asyncio.run(main())
