"""Market analyzer for processing market analysis data."""

from typing import Dict, Any, Optional
from src.api.market_analysis_client import MarketAnalysisClient

class MarketAnalyzer:
    """Analyzes market data using the market analysis service."""
    
    def __init__(self, client: MarketAnalysisClient):
        """Initialize market analyzer.
        
        Args:
            client: Market analysis client instance
        """
        self.client = client
        
    def analyze_symbol(
        self,
        symbol: str,
        indicators: Optional[list] = None,
        state_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a trading symbol.
        
        Args:
            symbol: Trading symbol to analyze
            indicators: List of technical indicators to calculate
            state_analysis: Whether to perform state analysis
            
        Returns:
            Analysis results including technical indicators and market state
        """
        return self.client.analyze(
            symbol=symbol,
            indicators=indicators,
            state_analysis=state_analysis
        )
    
    def get_market_state(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market state for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Market state information
        """
        analysis = self.analyze_symbol(symbol, state_analysis=True)
        return analysis.get("market_state", {})
    
    def get_trading_signals(self, symbol: str) -> Dict[str, Any]:
        """
        Get trading signals for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Trading signals including direction, strength and confidence
        """
        analysis = self.analyze_symbol(symbol)
        return analysis.get("signals", {})
