"""Integration tests for market analysis service integration."""

import os
import pytest
import httpx
from decimal import Decimal
from datetime import datetime
from src.core.trade_engine import TradeEngine
from src.core.system_state import SystemState
from src.core.risk_manager import RiskManager
from src.api.market_analysis_client import MarketAnalysisClient

def get_default_config():
    """Get default configuration for testing."""
    return {
        "risk": {
            "max_position_size": 100000,
            "max_risk_per_trade": 0.02,
            "max_correlated_trades": 3,
            "position_sizing_model": "fixed"
        },
        "trading": {
            "min_profit_target": 0.01,
            "max_loss": 0.02,
            "entry_timeout": 30,
            "exit_timeout": 30
        },
        "market_analysis": {
            "base_url": f"http://{os.environ.get('MARKET_ANALYSIS_HOST', 'localhost')}:{os.environ.get('MARKET_ANALYSIS_PORT', '8000')}",
            "indicators": ["RSI", "MACD", "BB"],
            "state_analysis": True,
            "num_states": 3
        }
    }

@pytest.fixture
def market_client():
    """Create market analysis client."""
    client = MarketAnalysisClient(
        base_url=f"http://{os.environ.get('MARKET_ANALYSIS_HOST', 'localhost')}:{os.environ.get('MARKET_ANALYSIS_PORT', '8000')}"
    )
    
    # Wait for market-analysis service to be ready
    max_retries = 5
    retry_delay = 1
    for _ in range(max_retries):
        try:
            response = httpx.get(f"{client.base_url}/health")
            if response.status_code == 200:
                break
        except httpx.RequestError:
            import time
            time.sleep(retry_delay)
    else:
        pytest.fail("Market analysis service is not available")
    
    return client

@pytest.fixture
def system_state():
    """Create system state instance."""
    return SystemState(get_default_config())

@pytest.fixture
def risk_manager(system_state):
    """Create risk manager instance."""
    return RiskManager(get_default_config(), system_state)

@pytest.fixture
def trade_engine(market_client, system_state, risk_manager):
    """Create trade engine instance with market client."""
    config = get_default_config()
    engine = TradeEngine(config, system_state, risk_manager)
    engine.market_client = market_client
    return engine

def test_market_analysis_api_integration(trade_engine):
    """Test integration with market analysis API."""
    symbol = "AAPL"
    
    # Process market analysis
    analysis = trade_engine.process_market_analysis(symbol)
    
    # Verify analysis results structure
    assert analysis["symbol"] == symbol
    assert "indicators" in analysis
    assert "market_state" in analysis
    assert "signals" in analysis
    
    # Verify indicator data
    indicators = analysis["indicators"]
    assert "RSI" in indicators
    assert "MACD" in indicators
    assert "BB" in indicators
    
    # Verify market state data
    market_state = analysis["market_state"]
    assert "current_state" in market_state
    assert "volatility" in market_state
    assert "trend_strength" in market_state
    
    # Verify signal data
    signals = analysis["signals"]
    assert "entry" in signals
    assert "direction" in signals["entry"]
    assert "confidence" in signals["entry"]

def test_risk_adjustment_based_on_market_state(trade_engine):
    """Test risk adjustment based on market state data from API."""
    symbol = "AAPL"
    initial_size = Decimal("100")
    
    # Process market analysis
    trade_engine.process_market_analysis(symbol)
    
    # Calculate adjusted position size
    adjusted_size = trade_engine.risk_manager.calculate_position_size(
        symbol=symbol,
        price=Decimal("150.0"),
        initial_size=initial_size
    )
    
    # Verify position size was adjusted based on market state
    assert isinstance(adjusted_size, Decimal)
    assert adjusted_size > 0
    assert adjusted_size != initial_size

def test_trading_signals_from_market_analysis(trade_engine):
    """Test trading signal generation using market analysis data."""
    symbol = "AAPL"
    
    # Process market analysis
    analysis = trade_engine.process_market_analysis(symbol)
    
    # Generate trading signals
    signals = trade_engine.generate_trading_signals(symbol)
    
    # Verify signals match market analysis
    assert "entry" in signals
    assert signals["entry"]["direction"] in ["long", "short", "neutral"]
    assert isinstance(signals["entry"]["confidence"], (float, int))
    assert 0 <= signals["entry"]["confidence"] <= 1
    
    # Verify signals are based on market state
    market_state = analysis["market_state"]["current_state"]
    if market_state == "bullish":
        assert signals["entry"]["direction"] == "long"
    elif market_state == "bearish":
        assert signals["entry"]["direction"] == "short"
