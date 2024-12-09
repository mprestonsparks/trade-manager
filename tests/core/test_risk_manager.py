"""
Tests for risk manager core functionality.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock
from src.core.risk_manager import RiskManager, PositionRisk
from src.core.system_state import SystemState
from src.config.trading_config import get_default_config

@pytest.fixture
def risk_manager():
    """Create risk manager instance for testing"""
    config = get_default_config()
    system_state = SystemState(config)
    return RiskManager(config, system_state)

def test_calculate_position_risk(risk_manager):
    """Test position risk calculation"""
    symbol = "AAPL"
    proposed_size = Decimal("100")
    entry_price = Decimal("150")
    volatility = 0.2
    
    is_acceptable, metrics = risk_manager.calculate_position_risk(
        symbol, proposed_size, entry_price, volatility
    )
    assert isinstance(is_acceptable, bool)
    assert isinstance(metrics, dict)
    if is_acceptable:
        assert "adjusted_size" in metrics
        assert "stop_loss" in metrics
        assert "take_profit" in metrics
        assert "risk_reward_ratio" in metrics
        assert "new_portfolio_heat" in metrics
    else:
        assert "error" in metrics

def test_update_position_risk(risk_manager):
    """Test updating position risk"""
    symbol = "AAPL"
    current_price = Decimal("150")
    market_volatility = 0.2
    
    # First need to simulate an existing position
    risk_manager.system_state.portfolio_state.positions["AAPL"] = {
        'size': Decimal("100"),
        'avg_cost': Decimal("145"),
        'unrealized_pnl': Decimal("500")
    }
    
    adjustments = risk_manager.update_position_risk(
        symbol, current_price, market_volatility
    )
    assert isinstance(adjustments, dict)
    assert "new_stop_loss" in adjustments
    assert "new_take_profit" in adjustments
    assert "risk_reward_ratio" in adjustments
    assert "unrealized_pnl" in adjustments

def test_adjust_size_for_volatility(risk_manager):
    """Test volatility-based position size adjustment"""
    base_size = Decimal("100")
    volatility = 0.2
    
    adjusted_size = risk_manager._adjust_size_for_volatility(base_size, volatility)
    assert isinstance(adjusted_size, Decimal)
    assert adjusted_size < base_size  # Higher volatility should reduce size

def test_calculate_exit_levels(risk_manager):
    """Test calculation of stop loss and take profit levels"""
    entry_price = Decimal("150")
    volatility = 0.2
    position_size = Decimal("100")
    
    stop_loss, take_profit = risk_manager._calculate_exit_levels(
        entry_price, volatility, position_size
    )
    assert isinstance(stop_loss, Decimal)
    assert isinstance(take_profit, Decimal)
    assert stop_loss < entry_price
    assert take_profit > entry_price
