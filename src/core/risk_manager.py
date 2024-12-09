"""
Risk management component implementing active inference for risk control.
"""

from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

from .system_state import SystemState, RiskMetrics

@dataclass
class PositionRisk:
    """Risk metrics for individual positions"""
    position_size: Decimal
    entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    risk_reward_ratio: float
    max_drawdown: Decimal

class RiskManager:
    """
    Risk management using active inference for dynamic risk control.
    Maintains beliefs about position and portfolio risk levels.
    """
    
    def __init__(self, config: Dict[str, Any], system_state: SystemState):
        """
        Initialize risk manager with configuration parameters.
        
        Args:
            config: Configuration dictionary containing:
                - Max position size
                - Risk limits per trade
                - Portfolio heat limits
                - Drawdown thresholds
                - Volatility adjustments
            system_state: System state instance
        """
        self.config = config
        self.system_state = system_state
        self.logger = logging.getLogger(__name__)
        self.positions: Dict[str, PositionRisk] = {}
        
    def calculate_position_risk(
        self,
        symbol: str,
        proposed_size: Decimal,
        entry_price: Decimal,
        volatility: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Calculate risk metrics for a proposed position and determine if it's acceptable.
        
        Args:
            symbol: Trading symbol
            proposed_size: Proposed position size
            entry_price: Proposed entry price
            volatility: Current market volatility
            
        Returns:
            Tuple of (is_acceptable, risk_metrics)
        """
        try:
            # Calculate position value
            position_value = proposed_size * entry_price
            
            # Get current portfolio state
            portfolio_state = self.system_state.portfolio_state
            
            # Check against maximum position size
            max_position_value = Decimal(str(self.config.get("max_position_value", 100000)))
            if position_value > max_position_value:
                return False, {"error": "Position size exceeds maximum allowed"}
            
            # Calculate risk-adjusted position size based on volatility
            risk_adjusted_size = self._adjust_size_for_volatility(
                proposed_size,
                volatility
            )
            
            # Calculate suggested stop loss and take profit levels
            stop_loss, take_profit = self._calculate_exit_levels(
                entry_price,
                volatility,
                risk_adjusted_size
            )
            
            # Check portfolio heat
            current_heat = self.system_state.risk_metrics.current_heat
            new_heat = current_heat + float(
                position_value / portfolio_state.total_value
            )
            max_heat = self.config.get("max_portfolio_heat", 1.0)
            
            if new_heat > max_heat:
                return False, {"error": "Portfolio heat limit exceeded"}
            
            return True, {
                "adjusted_size": risk_adjusted_size,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "risk_reward_ratio": self._calculate_risk_reward_ratio(
                    entry_price, stop_loss, take_profit
                ),
                "new_portfolio_heat": new_heat
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating position risk: {str(e)}")
            return False, {"error": str(e)}
            
    def update_position_risk(
        self,
        symbol: str,
        current_price: Decimal,
        market_volatility: float
    ) -> Optional[Dict[str, Any]]:
        """
        Update risk metrics for an existing position and suggest adjustments.
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            market_volatility: Current market volatility
            
        Returns:
            Optional dict with suggested adjustments
        """
        portfolio_state = self.system_state.portfolio_state
        if symbol not in portfolio_state.positions:
            return None
            
        position = portfolio_state.positions[symbol]
        
        # Get position details
        position_size = position['size']
        entry_price = position['avg_cost']
        unrealized_pnl = position['unrealized_pnl']
        
        # Update stop loss and take profit levels
        stop_loss = self._adjust_stop_loss(
            self._get_current_stop_loss(symbol),
            current_price,
            market_volatility
        )
        
        take_profit = self._adjust_take_profit(
            self._get_current_take_profit(symbol),
            current_price,
            market_volatility
        )
        
        # Calculate risk metrics
        risk_reward = self._calculate_risk_reward_ratio(
            current_price, stop_loss, take_profit
        )
        
        # Update position risk tracking
        self.positions[symbol] = PositionRisk(
            position_size=position_size,
            entry_price=entry_price,
            current_price=current_price,
            unrealized_pnl=unrealized_pnl,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward,
            max_drawdown=self._calculate_max_drawdown(symbol, unrealized_pnl)
        )
        
        return {
            "new_stop_loss": stop_loss,
            "new_take_profit": take_profit,
            "risk_reward_ratio": risk_reward,
            "unrealized_pnl": unrealized_pnl
        }
        
    def _adjust_size_for_volatility(
        self,
        base_size: Decimal,
        volatility: float
    ) -> Decimal:
        """
        Adjust position size based on market volatility.
        Higher volatility leads to smaller position sizes.
        """
        vol_factor = 1.0 / (1.0 + volatility)
        return base_size * Decimal(str(vol_factor))
        
    def _calculate_exit_levels(
        self,
        entry_price: Decimal,
        volatility: float,
        position_size: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """Calculate stop loss and take profit levels"""
        # Use volatility to determine stop loss distance
        stop_distance = entry_price * Decimal(str(volatility))
        stop_loss = entry_price - stop_distance
        
        # Set take profit at 2x the stop distance (adjustable risk-reward ratio)
        take_profit = entry_price + (stop_distance * Decimal("2"))
        
        return stop_loss, take_profit
        
    def _adjust_stop_loss(
        self,
        current_stop: Optional[Decimal],
        current_price: Decimal,
        volatility: float
    ) -> Optional[Decimal]:
        """Adjust stop loss based on current price and volatility"""
        if not current_stop:
            return None
            
        # Calculate new stop loss distance based on volatility
        stop_distance = current_price * Decimal(str(volatility))
        
        # Trail the stop loss if price has moved favorably
        if current_price > current_stop:
            return max(current_stop, current_price - stop_distance)
        
        return current_stop
        
    def _adjust_take_profit(
        self,
        current_tp: Optional[Decimal],
        current_price: Decimal,
        volatility: float
    ) -> Optional[Decimal]:
        """Adjust take profit based on current price and volatility"""
        if not current_tp:
            return None
            
        # Adjust take profit based on volatility
        tp_distance = current_price * Decimal(str(volatility)) * Decimal("2")
        
        # Move take profit up if price is approaching
        if current_price > current_tp * Decimal("0.9"):
            return current_price + tp_distance
        
        return current_tp
        
    def _calculate_risk_reward_ratio(
        self,
        current_price: Decimal,
        stop_loss: Optional[Decimal],
        take_profit: Optional[Decimal]
    ) -> float:
        """Calculate risk-reward ratio for a position"""
        if not stop_loss or not take_profit:
            return 0.0
            
        risk = float(current_price - stop_loss)
        reward = float(take_profit - current_price)
        
        if risk == 0:
            return 0.0
            
        return reward / risk
        
    def _calculate_max_drawdown(
        self,
        symbol: str,
        current_pnl: Decimal
    ) -> Decimal:
        """Calculate maximum drawdown for a position"""
        if symbol not in self.positions:
            return current_pnl if current_pnl < Decimal("0") else Decimal("0")
            
        return min(self.positions[symbol].max_drawdown, current_pnl)
        
    def _get_current_stop_loss(self, symbol: str) -> Optional[Decimal]:
        """Get current stop loss for a position"""
        return (self.positions[symbol].stop_loss 
                if symbol in self.positions else None)
                
    def _get_current_take_profit(self, symbol: str) -> Optional[Decimal]:
        """Get current take profit for a position"""
        return (self.positions[symbol].take_profit 
                if symbol in self.positions else None)
                
    def get_risk_metrics(self) -> RiskMetrics:
        """Get current risk metrics"""
        return self.system_state.risk_metrics
