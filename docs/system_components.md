# Trading System Components Documentation

This document provides a comprehensive overview of the core components in the trading system and their interactions.

## System Architecture

The trading system follows a modular architecture with dependency injection, centered around active inference principles. The main components interact through a central `SystemState` class, which maintains the system's beliefs and current state.

```
TradingSession
├── SystemState
│   ├── PortfolioManager
│   │   └── Allocation Beliefs
│   └── RiskManager
│       └── Risk Control Beliefs
├── UnifiedOptimizer
└── TradeEngine
```

## Core Components

### TradingSession

The `TradingSession` class serves as the main coordinator for the trading system, managing the interaction between various components through dependency injection.

**Key Responsibilities:**
- Initializes and coordinates system components
- Manages the trading lifecycle
- Ensures holistic optimization across components
- Handles dependency injection and component communication

### SystemState

The `SystemState` class encapsulates the system's beliefs and current state, serving as the central source of truth for all components.

**Key Features:**
- Maintains market data and position information
- Tracks portfolio and risk metrics
- Updates beliefs about market conditions
- Provides a unified interface for state access

### PortfolioManager

The `PortfolioManager` handles portfolio allocation and position sizing using active inference principles.

**Key Features:**
- Portfolio allocation optimization
- Position sizing calculations
- Dynamic rebalancing
- Strategy weight management

**Active Inference Implementation:**
- Maintains beliefs about optimal allocations
- Updates beliefs based on market conditions
- Optimizes position sizes based on confidence levels
- Implements dynamic rebalancing thresholds

### RiskManager

The `RiskManager` handles risk assessment and control using active inference principles.

**Key Features:**
- Position risk calculation
- Portfolio heat tracking
- Dynamic stop loss/take profit management
- Risk-reward optimization

**Active Inference Implementation:**
- Maintains beliefs about position risks
- Updates risk parameters dynamically
- Calculates portfolio-level risk metrics
- Implements adaptive risk controls

### UnifiedOptimizer

The `UnifiedOptimizer` handles joint optimization of trading decisions across components.

**Key Features:**
- Multi-objective optimization
- Parameter tuning
- Strategy optimization
- Performance evaluation

### TradeEngine

The `TradeEngine` handles trade execution and order management.

**Key Features:**
- Order execution
- Position tracking
- Trade lifecycle management
- Broker integration

## Component Interactions

### State Management
1. `SystemState` maintains the current state and beliefs
2. Components update their beliefs through `SystemState`
3. `TradingSession` coordinates state updates

### Trading Flow
1. Market data updates trigger state updates
2. `PortfolioManager` and `RiskManager` update beliefs
3. `UnifiedOptimizer` generates trading decisions
4. `TradeEngine` executes trades

### Risk Control
1. `RiskManager` monitors position and portfolio risks
2. Updates risk parameters based on market conditions
3. Communicates with `PortfolioManager` for position adjustments

### Portfolio Management
1. `PortfolioManager` maintains target allocations
2. Calculates position sizes based on risk parameters
3. Implements rebalancing when needed

## Configuration

The system is configured through `trading_config.py`, which includes:
- Optimization parameters
- Risk limits
- Portfolio constraints
- Execution settings
- Broker configurations

## Integration Points

### Broker Integration
- Abstract `BaseBroker` class defines the interface
- Specific broker adapters implement the interface
- `TradeEngine` uses broker adapters for execution

### Strategy Integration
- Strategies can be plugged into the `TradingSession`
- Must implement required interfaces
- Can access system state through `SystemState`

## Active Inference Framework

The system implements active inference principles through:
1. Belief maintenance about market states
2. Confidence-weighted decision making
3. Dynamic parameter adaptation
4. Joint optimization of trading decisions

This architecture ensures:
- Robust trading decisions
- Adaptive risk management
- Efficient portfolio optimization
- Scalable system design
