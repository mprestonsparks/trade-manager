"""
Tests for trade engine core functionality.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock
from src.core.trade_engine import TradeEngine, TradingAction, Trade, TradeResult
from src.core.system_state import SystemState, RiskMetrics, ExecutionState, PerformanceMetrics
from src.config.trading_config import get_default_config
from src.strategy.portfolio_optimizer import UnifiedOptimizer, OptimizedParameters

@pytest.fixture
def trade_engine():
    """Create trade engine instance for testing"""
    config = get_default_config()
    system_state = SystemState(config)
    optimizer = MagicMock(spec=UnifiedOptimizer)
    return TradeEngine(config, system_state, optimizer)

def test_calculate_risk_metrics(trade_engine):
    """Test risk metrics calculation"""
    metrics = trade_engine.calculate_risk_metrics()
    assert isinstance(metrics, RiskMetrics)
    assert hasattr(metrics, "portfolio_var")
    assert hasattr(metrics, "portfolio_volatility")
    assert hasattr(metrics, "position_var")
    assert hasattr(metrics, "position_volatility")
    assert hasattr(metrics, "correlation_matrix")

def test_get_execution_state(trade_engine):
    """Test getting execution state"""
    state = trade_engine.get_execution_state()
    assert isinstance(state, ExecutionState)
    assert hasattr(state, "pending_orders")
    assert hasattr(state, "recent_fills")
    assert hasattr(state, "execution_latency")
    assert hasattr(state, "spread_costs")
    assert hasattr(state, "market_impact")

def test_calculate_performance(trade_engine):
    """Test performance metrics calculation"""
    metrics = trade_engine.calculate_performance()
    assert isinstance(metrics, PerformanceMetrics)
    assert hasattr(metrics, "total_return")
    assert hasattr(metrics, "risk_adjusted_return")
    assert hasattr(metrics, "win_rate")
    assert hasattr(metrics, "profit_factor")
    assert hasattr(metrics, "avg_win_loss_ratio")

def test_process_actions(trade_engine):
    """Test processing optimized parameters into trading actions"""
    params = OptimizedParameters(
        target_allocations={"AAPL": Decimal("0.1")},
        position_sizes={"AAPL": Decimal("100")},
        rebalance_thresholds={"AAPL": Decimal("0.02")},
        position_var_limits={"AAPL": Decimal("0.01")},
        heat_capacity=Decimal("1.0"),
        execution_styles={"AAPL": "MKT"},
        order_types={"AAPL": "MKT"},
        timing_parameters={"AAPL": {"entry_window": 60, "exit_window": 60}},
        stop_loss_levels={"AAPL": Decimal("145")},
        take_profit_levels={"AAPL": Decimal("155")}
    )
    
    actions = trade_engine.process_actions(params)
    assert isinstance(actions, list)
    if actions:
        action = actions[0]
        assert isinstance(action, TradingAction)
        assert action.symbol == "AAPL"
        assert action.size == Decimal("100")
        assert action.order_type == "MKT"
