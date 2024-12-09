"""
Pytest configuration and fixtures for trade-manager tests.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Mock the entire market_analysis module
@pytest.fixture(autouse=True)
def mock_market_analysis():
    """Mock the market_analysis module"""
    with patch.dict('sys.modules', {'market_analysis': MagicMock()}):
        yield

@pytest.fixture
def mock_market_analysis_response():
    """Mock responses from market-analysis API"""
    def _mock_response(symbol="AAPL", timeframe="1d"):
        current_time = datetime.now()
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "analysis": {
                "technical_indicators": {
                    "rsi": 65.5,
                    "macd": {
                        "macd": 2.5,
                        "signal": 1.8,
                        "histogram": 0.7
                    },
                    "moving_averages": {
                        "sma_20": 150.5,
                        "sma_50": 148.2,
                        "ema_12": 151.3,
                        "ema_26": 149.8
                    }
                },
                "price_data": {
                    "current_price": 152.35,
                    "open": 150.20,
                    "high": 153.45,
                    "low": 149.80,
                    "volume": 75000000,
                    "timestamp": current_time.isoformat()
                },
                "signals": {
                    "trend": "BULLISH",
                    "strength": 0.75,
                    "recommendation": "BUY",
                    "confidence": 0.82
                }
            },
            "timestamp": current_time.isoformat()
        }
    return _mock_response

@pytest.fixture
def mock_market_opportunities():
    """Mock trading opportunities from market-analysis API"""
    def _mock_opportunities():
        current_time = datetime.now()
        return {
            "opportunities": [
                {
                    "symbol": "AAPL",
                    "type": "ENTRY",
                    "direction": "LONG",
                    "confidence": 0.85,
                    "price_target": 155.00,
                    "stop_loss": 148.50,
                    "timeframe": "1d",
                    "timestamp": current_time.isoformat()
                },
                {
                    "symbol": "MSFT",
                    "type": "EXIT",
                    "direction": "SHORT",
                    "confidence": 0.78,
                    "price_target": 335.00,
                    "stop_loss": 345.00,
                    "timeframe": "1d",
                    "timestamp": current_time.isoformat()
                }
            ],
            "timestamp": current_time.isoformat()
        }
    return _mock_opportunities

@pytest.fixture
def mock_market_analysis_client(mock_market_analysis_response, mock_market_opportunities):
    """Mock the entire market analysis client"""
    mock_client = MagicMock()
    mock_client.get_analysis.return_value = mock_market_analysis_response()
    mock_client.get_opportunities.return_value = mock_market_opportunities()
    
    with patch("src.api.main.MarketAnalyzer") as mock_analyzer:
        mock_analyzer.return_value = mock_client
        yield mock_client
