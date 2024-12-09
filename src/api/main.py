"""
FastAPI application for trade manager service.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.trading_session import TradingSession
from ..core.system_state import SystemState
from ..core.portfolio import PortfolioManager
from ..core.risk_manager import RiskManager
from ..core.trade_engine import TradeEngine
from ..strategy.portfolio_optimizer import UnifiedOptimizer
from ..config.trading_config import get_default_config
from market_analysis.market_analysis import MarketAnalyzer
from market_analysis.config.technical_indicators import get_indicator_config
from .models import (
    TradeRequest,
    TradeResponse,
    PositionInfo,
    SystemStatus,
    OrderStatus
)

app = FastAPI(
    title="Trade Manager API",
    description="API for managing trading operations and portfolio management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize trading components
config = get_default_config()
system_state = SystemState(config)

# Initialize market analyzer with default symbol and indicator config
market_analyzer = MarketAnalyzer(
    symbol=config.get("default_symbol", "SPY"),
    indicator_config=get_indicator_config(),
    test_mode=config.get("test_mode", False)
)

# Initialize optimizer with market analyzer
optimizer = UnifiedOptimizer(config, market_analyzer)
portfolio_manager = PortfolioManager(config, system_state)
risk_manager = RiskManager(config, system_state)
trade_engine = TradeEngine(config, system_state, optimizer)

@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get current system status and health information"""
    return {
        "status": "operational",
        "timestamp": datetime.utcnow(),
        "components": {
            "portfolio_manager": "healthy",
            "risk_manager": "healthy",
            "trade_engine": "healthy"
        }
    }

@app.get("/positions", response_model=List[PositionInfo])
async def get_positions():
    """Get all current positions"""
    try:
        positions = portfolio_manager.get_positions()
        return [
            {
                "symbol": pos.symbol,
                "quantity": pos.quantity,
                "entry_price": pos.entry_price,
                "current_price": pos.current_price,
                "pnl": pos.pnl,
                "timestamp": pos.timestamp
            }
            for pos in positions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trade", response_model=TradeResponse)
async def execute_trade(trade_request: TradeRequest):
    """Execute a trade based on the provided request"""
    try:
        # Validate trade against risk rules
        if not risk_manager.validate_trade(trade_request.dict()):
            raise HTTPException(
                status_code=400,
                detail="Trade rejected by risk manager"
            )
        
        # Execute trade
        trade_result = trade_engine.execute_trade(trade_request.dict())
        
        return {
            "trade_id": trade_result.trade_id,
            "status": trade_result.status,
            "timestamp": datetime.utcnow(),
            "details": trade_result.details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}", response_model=OrderStatus)
async def get_order_status(order_id: str):
    """Get status of a specific order"""
    try:
        order = trade_engine.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"Order {order_id} not found"
            )
        
        return {
            "order_id": order.order_id,
            "status": order.status,
            "filled_quantity": order.filled_quantity,
            "remaining_quantity": order.remaining_quantity,
            "average_price": order.average_price,
            "timestamp": order.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/opportunities")
async def process_opportunities(opportunities: List[Dict[str, Any]]):
    """Process trading opportunities from the discovery service"""
    try:
        results = []
        for opp in opportunities:
            # Validate opportunity against current portfolio and risk rules
            if risk_manager.validate_opportunity(opp):
                # Generate trade request
                trade_request = trade_engine.generate_trade_request(opp)
                # Execute trade if conditions are met
                if trade_request:
                    trade_result = trade_engine.execute_trade(trade_request)
                    results.append({
                        "opportunity_id": opp.get("id"),
                        "trade_id": trade_result.trade_id,
                        "status": "executed",
                        "details": trade_result.details
                    })
                else:
                    results.append({
                        "opportunity_id": opp.get("id"),
                        "status": "rejected",
                        "reason": "Trade conditions not met"
                    })
            else:
                results.append({
                    "opportunity_id": opp.get("id"),
                    "status": "rejected",
                    "reason": "Failed risk validation"
                })
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
