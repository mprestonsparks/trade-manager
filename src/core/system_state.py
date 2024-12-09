"""
System state management for the trade manager.
Implements belief state tracking for active inference framework.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime

@dataclass
class PortfolioState:
    """Portfolio state including positions and allocations"""
    positions: Dict[str, Dict[str, Any]]
    total_value: Decimal
    cash_balance: Decimal
    margin_used: Decimal
    margin_available: Decimal
    asset_allocation: Dict[str, float]
    realized_pnl: Decimal
    unrealized_pnl: Decimal

@dataclass
class RiskMetrics:
    """Risk metrics across portfolio"""
    portfolio_var: float
    portfolio_volatility: float
    position_var: Dict[str, float]
    position_volatility: Dict[str, float]
    correlation_matrix: Dict[str, Dict[str, float]]
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    current_heat: float

@dataclass
class ExecutionState:
    """Execution state and metrics"""
    pending_orders: List[Dict[str, Any]]
    recent_fills: List[Dict[str, Any]]
    execution_latency: float
    spread_costs: Dict[str, float]
    market_impact: Dict[str, float]
    order_book_state: Dict[str, Dict[str, Any]]

@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    total_return: float
    risk_adjusted_return: float
    win_rate: float
    profit_factor: float
    avg_win_loss_ratio: float
    max_drawdown: float
    recovery_factor: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    portfolio_turnover: float
    transaction_costs: float

class SystemState:
    """
    System state management implementing active inference belief states.
    Tracks and updates beliefs about portfolio, risk, and execution states.
    """
    
    def __init__(self):
        """Initialize system state"""
        self.portfolio_state = PortfolioState(
            positions={},
            total_value=Decimal('0'),
            cash_balance=Decimal('0'),
            margin_used=Decimal('0'),
            margin_available=Decimal('0'),
            asset_allocation={},
            realized_pnl=Decimal('0'),
            unrealized_pnl=Decimal('0')
        )
        
        self.risk_metrics = RiskMetrics(
            portfolio_var=0.0,
            portfolio_volatility=0.0,
            position_var={},
            position_volatility={},
            correlation_matrix={},
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            current_heat=0.0
        )
        
        self.execution_state = ExecutionState(
            pending_orders=[],
            recent_fills=[],
            execution_latency=0.0,
            spread_costs={},
            market_impact={},
            order_book_state={}
        )
        
        self.performance_metrics = PerformanceMetrics(
            total_return=0.0,
            risk_adjusted_return=0.0,
            win_rate=0.0,
            profit_factor=0.0,
            avg_win_loss_ratio=0.0,
            max_drawdown=0.0,
            recovery_factor=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            portfolio_turnover=0.0,
            transaction_costs=0.0
        )
        
        self.market_data: Dict[str, Dict[str, Any]] = {}
        self.last_update: Optional[datetime] = None
        
    def update_market_data(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Update market data and beliefs.
        
        Args:
            data: Market data by symbol
        """
        self.market_data = data
        self.last_update = datetime.now()
        
    def update_positions(self, positions: List[Any]) -> None:
        """
        Update position beliefs.
        
        Args:
            positions: List of position objects from broker
        """
        # Convert broker positions to internal format
        position_dict = {}
        total_value = Decimal('0')
        
        for pos in positions:
            symbol = pos.contract.symbol
            position_dict[symbol] = {
                'size': Decimal(str(pos.position)),
                'avg_cost': Decimal(str(pos.avgCost)),
                'market_price': Decimal(str(pos.marketPrice)),
                'market_value': Decimal(str(pos.marketValue)),
                'unrealized_pnl': Decimal(str(pos.unrealizedPNL)),
                'realized_pnl': Decimal(str(pos.realizedPNL))
            }
            total_value += Decimal(str(pos.marketValue))
            
        self.portfolio_state.positions = position_dict
        self.portfolio_state.total_value = total_value
        
        # Update asset allocation
        if total_value > 0:
            self.portfolio_state.asset_allocation = {
                symbol: float(pos['market_value'] / total_value)
                for symbol, pos in position_dict.items()
            }
            
    def update_portfolio(self, portfolio: List[Any]) -> None:
        """
        Update portfolio beliefs.
        
        Args:
            portfolio: Portfolio information from broker
        """
        total_value = Decimal('0')
        unrealized_pnl = Decimal('0')
        realized_pnl = Decimal('0')
        
        for item in portfolio:
            total_value += Decimal(str(item.marketValue))
            unrealized_pnl += Decimal(str(item.unrealizedPNL))
            realized_pnl += Decimal(str(item.realizedPNL))
            
        self.portfolio_state.total_value = total_value
        self.portfolio_state.unrealized_pnl = unrealized_pnl
        self.portfolio_state.realized_pnl = realized_pnl
        
    def get_optimization_features(self) -> Dict[str, float]:
        """Get features used for optimization"""
        return {
            # Portfolio features
            'portfolio_concentration': max(self.portfolio_state.asset_allocation.values()),
            'cash_ratio': float(self.portfolio_state.cash_balance / self.portfolio_state.total_value),
            'margin_utilization': float(self.portfolio_state.margin_used / 
                                  (self.portfolio_state.margin_used + self.portfolio_state.margin_available)),
            
            # Risk features
            'portfolio_var': self.risk_metrics.portfolio_var,
            'portfolio_heat': self.risk_metrics.current_heat,
            'max_position_var': max(self.risk_metrics.position_var.values()),
            
            # Performance features
            'sharpe_ratio': self.performance_metrics.sharpe_ratio,
            'sortino_ratio': self.performance_metrics.sortino_ratio,
            'recovery_factor': self.performance_metrics.recovery_factor,
            
            # Execution features
            'avg_spread_cost': sum(self.execution_state.spread_costs.values()) / 
                         len(self.execution_state.spread_costs) if self.execution_state.spread_costs else 0,
            'avg_market_impact': sum(self.execution_state.market_impact.values()) / 
                           len(self.execution_state.market_impact) if self.execution_state.market_impact else 0,
            'execution_latency': self.execution_state.execution_latency
        }
        
    def calculate_risk_adjusted_returns(self) -> float:
        """Calculate overall risk-adjusted return metric"""
        if self.risk_metrics.portfolio_volatility == 0:
            return 0.0
        return (self.performance_metrics.total_return / 
                self.risk_metrics.portfolio_volatility)
