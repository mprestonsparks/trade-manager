"""
Portfolio management component implementing active inference for asset allocation.
"""

from decimal import Decimal
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from .system_state import SystemState, PortfolioState
from ..strategy.portfolio_optimizer import OptimizedParameters
from .market_types import MarketState

@dataclass
class TradeSignal:
    """Trade signal with confidence metrics"""
    symbol: str
    direction: str  # 'buy' or 'sell'
    confidence: float
    target_position: Optional[Decimal]
    metadata: Dict[str, Any]

class PortfolioManager:
    """
    Portfolio management using active inference for asset allocation.
    Maintains beliefs about optimal allocations and position sizes.
    """
    
    def __init__(self, config: Dict[str, Any], system_state: SystemState):
        """
        Initialize portfolio manager with configuration.
        
        Args:
            config: Configuration containing:
                - Initial capital
                - Risk limits
                - Asset allocations
                - Strategy weights
            system_state: System state instance
        """
        self.config = config
        self.system_state = system_state
        self.logger = logging.getLogger(__name__)
        
        # Initialize portfolio state
        self.portfolio_value = Decimal(str(config.get("initial_capital", 100000)))
        self.target_allocations: Dict[str, float] = {}
        self.strategy_weights: Dict[str, float] = {}
        self.last_rebalance: Optional[datetime] = None
        
    def update_allocation(self, optimized_params: OptimizedParameters) -> None:
        """
        Update portfolio allocation based on optimized parameters.
        
        Args:
            optimized_params: Parameters from unified optimizer
        """
        try:
            self.logger.info("Updating portfolio allocation")
            
            # Update target allocations from optimized parameters
            self.target_allocations = optimized_params.target_allocations
            
            # Update strategy weights
            self.strategy_weights = optimized_params.strategy_weights
            
            # Check if rebalancing is needed
            if self._should_rebalance():
                self._rebalance_portfolio()
                
        except Exception as e:
            self.logger.error(f"Error updating allocation: {str(e)}")
            
    def calculate_position_size(self, signal: TradeSignal) -> Decimal:
        """
        Calculate position size based on portfolio value and risk parameters.
        
        Args:
            signal: Trade signal with confidence metrics
            
        Returns:
            Position size in base currency
        """
        try:
            # Get risk parameters
            max_position_size = Decimal(str(self.config.get("max_position_size", 0.1)))
            risk_per_trade = Decimal(str(self.config.get("risk_per_trade", 0.02)))
            
            # Get current portfolio state
            portfolio_state = self.system_state.portfolio_state
            
            # Calculate base position size based on portfolio value and risk
            base_size = portfolio_state.total_value * risk_per_trade
            
            # Adjust size based on signal confidence and target allocation
            target_alloc = self.target_allocations.get(signal.symbol, 0.0)
            confidence_adj = Decimal(str(signal.confidence))
            allocation_adj = Decimal(str(target_alloc))
            
            adjusted_size = base_size * confidence_adj * allocation_adj
            
            # Apply position limits
            max_size = portfolio_state.total_value * max_position_size
            position_size = min(adjusted_size, max_size)
            
            self.logger.info(f"Calculated position size: {position_size}")
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return Decimal("0")
            
    def _should_rebalance(self) -> bool:
        """
        Check if portfolio rebalancing is needed based on:
        1. Time since last rebalance
        2. Deviation from target allocations
        3. Market conditions
        """
        if not self.last_rebalance:
            return True
            
        # Get rebalancing parameters
        min_rebalance_interval = self.config.get("min_rebalance_interval", 86400)  # 1 day
        rebalance_threshold = Decimal(str(self.config.get("rebalance_threshold", 0.05)))
        
        # Check time interval
        time_since_rebalance = (datetime.now() - self.last_rebalance).total_seconds()
        if time_since_rebalance < min_rebalance_interval:
            return False
            
        # Check allocation deviation
        portfolio_state = self.system_state.portfolio_state
        for symbol, target in self.target_allocations.items():
            current = portfolio_state.asset_allocation.get(symbol, 0.0)
            if abs(current - target) > float(rebalance_threshold):
                return True
                
        return False
        
    def _rebalance_portfolio(self) -> None:
        """
        Rebalance portfolio to target allocations.
        Generates rebalancing trades based on current positions and targets.
        """
        try:
            portfolio_state = self.system_state.portfolio_state
            total_value = portfolio_state.total_value
            
            # Calculate required position adjustments
            adjustments: Dict[str, Decimal] = {}
            for symbol, target in self.target_allocations.items():
                target_value = total_value * Decimal(str(target))
                current_value = Decimal("0")
                
                if symbol in portfolio_state.positions:
                    position = portfolio_state.positions[symbol]
                    current_value = position['market_value']
                    
                value_diff = target_value - current_value
                if abs(value_diff) > Decimal("0"):
                    # Convert value difference to position size
                    price = portfolio_state.positions[symbol]['market_price']
                    size_adjustment = value_diff / price
                    adjustments[symbol] = size_adjustment
                    
            # Log rebalancing actions
            self.logger.info(f"Portfolio rebalancing adjustments: {adjustments}")
            self.last_rebalance = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error rebalancing portfolio: {str(e)}")
            
    def get_portfolio_state(self) -> PortfolioState:
        """Get current portfolio state"""
        return self.system_state.portfolio_state
