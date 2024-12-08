from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

@dataclass
class RiskMetrics:
    """Current risk metrics for the portfolio"""
    total_exposure: Decimal
    largest_position: Decimal
    position_count: int
    margin_used: Decimal
    free_margin: Decimal
    risk_per_trade: Decimal
    portfolio_heat: float  # Measure of overall portfolio risk

@dataclass
class PositionRisk:
    """Risk metrics for an individual position"""
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
    Manages risk controls and position sizing across the portfolio.
    Implements dynamic risk adjustment based on market conditions.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize risk manager with configuration parameters.
        
        Args:
            config: Configuration dictionary containing:
                - Max position size
                - Risk limits per trade
                - Portfolio heat limits
                - Drawdown thresholds
                - Volatility adjustments
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.positions: Dict[str, PositionRisk] = {}
        self.risk_metrics = self._initialize_risk_metrics()
        
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
            
            # Check against maximum position size
            max_position_value = self.config.get("max_position_value", Decimal("100000"))
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
            if not self._check_portfolio_heat(position_value):
                return False, {"error": "Portfolio heat limit exceeded"}
            
            return True, {
                "adjusted_size": risk_adjusted_size,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "risk_reward_ratio": self._calculate_risk_reward_ratio(
                    entry_price, stop_loss, take_profit
                )
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
        if symbol not in self.positions:
            return None
            
        position = self.positions[symbol]
        
        # Calculate unrealized P&L
        unrealized_pnl = (current_price - position.entry_price) * position.position_size
        
        # Update max drawdown
        max_drawdown = min(position.max_drawdown, unrealized_pnl)
        
        # Check if stop loss adjustment is needed
        new_stop_loss = self._adjust_stop_loss(
            position.stop_loss,
            current_price,
            market_volatility
        )
        
        # Check if take profit adjustment is needed
        new_take_profit = self._adjust_take_profit(
            position.take_profit,
            current_price,
            market_volatility
        )
        
        # Update position risk metrics
        self.positions[symbol] = PositionRisk(
            position_size=position.position_size,
            entry_price=position.entry_price,
            current_price=current_price,
            unrealized_pnl=unrealized_pnl,
            stop_loss=new_stop_loss,
            take_profit=new_take_profit,
            risk_reward_ratio=self._calculate_risk_reward_ratio(
                current_price, new_stop_loss, new_take_profit
            ),
            max_drawdown=max_drawdown
        )
        
        return {
            "new_stop_loss": new_stop_loss,
            "new_take_profit": new_take_profit,
            "unrealized_pnl": unrealized_pnl,
            "max_drawdown": max_drawdown
        }
        
    def get_risk_metrics(self) -> RiskMetrics:
        """Get current risk metrics for the portfolio"""
        return self.risk_metrics
        
    def _initialize_risk_metrics(self) -> RiskMetrics:
        """Initialize risk metrics with default values"""
        return RiskMetrics(
            total_exposure=Decimal("0"),
            largest_position=Decimal("0"),
            position_count=0,
            margin_used=Decimal("0"),
            free_margin=Decimal(str(self.config.get("initial_margin", 100000))),
            risk_per_trade=Decimal(str(self.config.get("risk_per_trade", 0.02))),
            portfolio_heat=0.0
        )
        
    def _adjust_size_for_volatility(
        self,
        base_size: Decimal,
        volatility: float
    ) -> Decimal:
        """Adjust position size based on market volatility"""
        vol_multiplier = 1.0
        
        # Reduce position size in high volatility
        if volatility > self.config.get("high_volatility_threshold", 0.5):
            vol_multiplier = 0.5
        # Increase position size in low volatility
        elif volatility < self.config.get("low_volatility_threshold", 0.2):
            vol_multiplier = 1.5
            
        return base_size * Decimal(str(vol_multiplier))
        
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
        
    def _check_portfolio_heat(self, new_position_value: Decimal) -> bool:
        """Check if adding new position would exceed portfolio heat limit"""
        current_heat = self.risk_metrics.portfolio_heat
        max_heat = self.config.get("max_portfolio_heat", 1.0)
        
        # Calculate new portfolio heat
        new_heat = current_heat + float(
            new_position_value / Decimal(str(self.config.get("initial_margin", 100000)))
        )
        
        return new_heat <= max_heat
        
    def _calculate_risk_reward_ratio(
        self,
        current_price: Decimal,
        stop_loss: Optional[Decimal],
        take_profit: Optional[Decimal]
    ) -> float:
        """Calculate risk-reward ratio for a position"""
        if not stop_loss or not take_profit:
            return 0.0
            
        risk = float(abs(current_price - stop_loss))
        reward = float(abs(take_profit - current_price))
        
        return reward / risk if risk > 0 else 0.0
        
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
