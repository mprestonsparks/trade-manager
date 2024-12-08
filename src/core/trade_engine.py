from decimal import Decimal
from typing import Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import logging
from .risk_manager import RiskManager
from ..strategy.optimizer import ActiveInferenceOptimizer, MarketBelief, TradingAction

@dataclass
class MarketSignal:
    """Market signal containing state and trade recommendations"""
    symbol: str
    direction: str  # "long" or "short"
    confidence: float
    timestamp: float
    volatility: float
    metadata: Dict[str, Any]

@dataclass
class Trade:
    """Trade execution details"""
    symbol: str
    direction: str
    size: Decimal
    entry_price: Optional[Decimal]
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    metadata: Dict[str, Any]

@dataclass
class TradeResult:
    """Result of trade execution"""
    success: bool
    trade_id: Optional[str]
    executed_price: Optional[Decimal]
    message: str
    timestamp: float

class TradeEngine:
    """
    Primary trade management system coordinating all trading operations.
    Implements Active Inference methodology for trade optimization.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize trade engine with configuration parameters.
        
        Args:
            config: Configuration dictionary containing:
                - API endpoints
                - Risk parameters
                - Strategy settings
                - Portfolio limits
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.active_trades: Dict[str, Trade] = {}
        self.risk_manager = RiskManager(config)
        self.optimizer = ActiveInferenceOptimizer(config)
        
    async def process_market_signal(self, signal: MarketSignal) -> None:
        try:
            self.logger.info(f"Processing signal for {signal.symbol}")
            
            # Validate signal
            if not self._validate_signal(signal):
                self.logger.warning(f"Invalid signal received for {signal.symbol}")
                return
                
            # Update market beliefs using Active Inference
            self.optimizer.update_beliefs({
                'symbol': signal.symbol,
                'price': signal.metadata.get('price', 0),
                'volume': signal.metadata.get('volume', 0),
                'timestamp': signal.timestamp,
                'volatility': signal.volatility,
                'market_data': signal.metadata.get('market_data', {})
            })
            
            # Generate optimal actions using genetic algorithm
            possible_actions = self.optimizer.generate_actions()
            
            if not possible_actions:
                self.logger.warning("No viable actions generated")
                return
                
            # Select best action
            best_action = possible_actions[0]  # Actions are already sorted by fitness
            
            # Check if we have capacity for new trades
            if best_action.action_type in ['enter_long', 'enter_short']:
                if not self._check_trade_capacity():
                    self.logger.info("Trade capacity reached, skipping signal")
                    return
                    
            # Check risk metrics and adjust position size
            is_acceptable, risk_metrics = self.risk_manager.calculate_position_risk(
                signal.symbol,
                best_action.size,
                Decimal("0"),  # Entry price will be determined during execution
                signal.volatility
            )
            
            if not is_acceptable:
                self.logger.warning(f"Risk check failed: {risk_metrics.get('error')}")
                return
                
            # Create trade object with risk-adjusted parameters
            trade = self._create_trade_from_action(signal, best_action, risk_metrics)
            
            # Execute trade
            result = await self.execute_trade(trade)
            
            if result.success:
                self.active_trades[result.trade_id] = trade
                self.logger.info(f"Successfully executed trade {result.trade_id}")
            else:
                self.logger.error(f"Failed to execute trade: {result.message}")
                
        except Exception as e:
            self.logger.error(f"Error processing signal: {str(e)}")
            
    async def execute_trade(self, trade: Trade) -> TradeResult:
        """
        Execute a trade based on validated signals and risk parameters.
        
        Args:
            trade: Trade object containing execution details
            
        Returns:
            TradeResult containing execution status and details
        """
        try:
            # TODO: Implement actual trade execution logic with broker API
            # This is a placeholder implementation
            mock_price = Decimal("100")  # Mock current price
            
            # Update risk metrics with actual execution price
            self.risk_manager.update_position_risk(
                trade.symbol,
                mock_price,
                float(trade.metadata.get("volatility", 0.2))
            )
            
            return TradeResult(
                success=True,
                trade_id="mock_trade_id",
                executed_price=mock_price,
                message="Trade executed successfully",
                timestamp=asyncio.get_event_loop().time()
            )
        except Exception as e:
            return TradeResult(
                success=False,
                trade_id=None,
                executed_price=None,
                message=f"Trade execution failed: {str(e)}",
                timestamp=asyncio.get_event_loop().time()
            )
            
    def _validate_signal(self, signal: MarketSignal) -> bool:
        """Validate incoming market signal"""
        return (
            0 <= signal.confidence <= 1 and
            signal.direction in ["long", "short"] and
            signal.symbol and
            signal.timestamp > 0 and
            signal.volatility >= 0
        )
        
    def _check_trade_capacity(self) -> bool:
        """Check if we have capacity for new trades"""
        max_trades = self.config.get("max_concurrent_trades", 10)
        return len(self.active_trades) < max_trades
        
    def _create_trade_from_action(
        self,
        signal: MarketSignal,
        action: TradingAction,
        risk_metrics: Dict[str, Any]
    ) -> Trade:
        """Create a trade object from an optimized trading action"""
        return Trade(
            symbol=signal.symbol,
            direction=action.action_type.replace('enter_', ''),
            size=risk_metrics["adjusted_size"],
            entry_price=None,  # Will be set during execution
            stop_loss=risk_metrics["stop_loss"],
            take_profit=risk_metrics["take_profit"],
            metadata={
                **signal.metadata,
                "risk_reward_ratio": risk_metrics["risk_reward_ratio"],
                "volatility": signal.volatility,
                "expected_reward": action.expected_reward,
                "action_uncertainty": action.uncertainty
            }
        )
