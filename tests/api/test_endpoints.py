"""
Tests for trade manager API endpoints.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

# Mock market_analysis module before importing app
market_analysis_mock = MagicMock()
market_analysis_mock.market_analysis = MagicMock()
market_analysis_mock.market_analysis.MarketAnalyzer = MagicMock()
market_analysis_mock.config = MagicMock()
market_analysis_mock.config.technical_indicators = MagicMock()
market_analysis_mock.config.technical_indicators.get_indicator_config = MagicMock(return_value={})

with patch.dict('sys.modules', {
    'market_analysis': market_analysis_mock,
    'market_analysis.market_analysis': market_analysis_mock.market_analysis,
    'market_analysis.config.technical_indicators': market_analysis_mock.config.technical_indicators
}):
    from src.api.main import app
    from src.api.models import OrderType, OrderSide

@pytest.fixture
def client():
    """Test client"""
    with TestClient(app) as test_client:
        yield test_client

def test_get_system_status(client):
    """Test system status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "timestamp" in data
    assert "components" in data
    assert all(component in data["components"] for component in [
        "portfolio_manager",
        "risk_manager",
        "trade_engine"
    ])

def test_get_positions(client):
    """Test positions endpoint"""
    response = client.get("/positions")
    assert response.status_code == 200
    positions = response.json()
    assert isinstance(positions, list)
    if positions:  # If there are any positions
        position = positions[0]
        assert all(key in position for key in [
            "symbol",
            "quantity",
            "entry_price",
            "current_price",
            "pnl",
            "timestamp"
        ])

def test_execute_trade_market_order(client):
    """Test trade execution with market order"""
    trade_request = {
        "symbol": "AAPL",
        "order_type": OrderType.MARKET.value,
        "side": OrderSide.BUY.value,
        "quantity": 100,
        "price": None  # Market order doesn't need price
    }
    response = client.post("/trade", json=trade_request)
    assert response.status_code == 200
    data = response.json()
    assert "order_id" in data
    assert "status" in data
    assert data["status"] == "EXECUTED"

def test_execute_trade_invalid_request(client):
    """Test trade execution with invalid request"""
    trade_request = {
        "symbol": "INVALID",
        "order_type": "INVALID",
        "side": "INVALID",
        "quantity": -1
    }
    response = client.post("/trade", json=trade_request)
    assert response.status_code == 422

def test_get_order_status(client):
    """Test order status endpoint"""
    # First create an order
    trade_request = {
        "symbol": "AAPL",
        "order_type": OrderType.MARKET.value,
        "side": OrderSide.BUY.value,
        "quantity": 100
    }
    trade_response = client.post("/trade", json=trade_request)
    order_id = trade_response.json()["order_id"]

    # Then get its status
    response = client.get(f"/order/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert all(key in data for key in [
        "order_id",
        "symbol",
        "order_type",
        "side",
        "quantity",
        "status",
        "timestamp"
    ])

def test_get_nonexistent_order(client):
    """Test getting status of non-existent order"""
    response = client.get("/order/nonexistent")
    assert response.status_code == 404

def test_process_opportunities(client):
    """Test processing trading opportunities"""
    opportunities = {
        "opportunities": [
            {
                "symbol": "AAPL",
                "type": "ENTRY",
                "direction": "LONG",
                "confidence": 0.85,
                "price_target": 155.00,
                "stop_loss": 148.50
            }
        ]
    }
    response = client.post("/opportunities", json=opportunities)
    assert response.status_code == 200
    data = response.json()
    assert "processed" in data
    assert isinstance(data["processed"], int)
    assert data["processed"] > 0

def test_get_market_analysis(client):
    """Test getting market analysis for a symbol"""
    response = client.get("/analysis/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert "analysis" in data
    assert "technical_indicators" in data["analysis"]
    assert "signals" in data["analysis"]

def test_get_trading_opportunities(client):
    """Test getting current trading opportunities"""
    response = client.get("/opportunities")
    assert response.status_code == 200
    data = response.json()
    assert "opportunities" in data
    assert isinstance(data["opportunities"], list)
    if data["opportunities"]:
        opportunity = data["opportunities"][0]
        assert all(key in opportunity for key in [
            "symbol",
            "type",
            "direction",
            "confidence",
            "price_target",
            "stop_loss"
        ])
