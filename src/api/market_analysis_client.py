"""
Client for interacting with the market analysis service.
"""

from typing import Dict, Any, Optional
import httpx
from datetime import datetime

class MarketAnalysisClient:
    """Client for interacting with the market analysis service."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize market analysis client.
        
        Args:
            base_url: Base URL for the market analysis service
        """
        self.base_url = base_url
        self.client = httpx.Client()
        
    def analyze(
        self,
        symbol: str,
        indicators: Optional[list] = None,
        state_analysis: bool = True,
        num_states: int = 3,
        thresholds: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Request market analysis for a symbol.
        
        Args:
            symbol: Trading symbol to analyze
            indicators: List of technical indicators to calculate
            state_analysis: Whether to perform state analysis
            num_states: Number of market states to consider
            thresholds: Custom thresholds for analysis
            
        Returns:
            Analysis results including technical indicators and market state
        """
        if indicators is None:
            indicators = ["RSI", "MACD", "BB"]
            
        if thresholds is None:
            thresholds = {
                "rsi_oversold": 30.0,
                "rsi_overbought": 70.0,
                "rsi_weight": 0.4,
                "macd_threshold_std": 1.5,
                "macd_weight": 0.4,
                "stoch_oversold": 20.0,
                "stoch_overbought": 80.0,
                "stoch_weight": 0.2,
                "min_signal_strength": 0.1,
                "min_confidence": 0.5
            }
            
        request = {
            "symbol": symbol,
            "indicators": indicators,
            "state_analysis": state_analysis,
            "num_states": num_states,
            "thresholds": thresholds
        }
        
        response = self.client.post(f"{self.base_url}/analyze", json=request)
        response.raise_for_status()
        return response.json()
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status of the market analysis service."""
        response = self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
