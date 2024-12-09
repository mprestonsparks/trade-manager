# Trade Manager

A sophisticated trading system that combines Active Inference methodology with Genetic Algorithms for optimal trade execution and portfolio management.

## Core Features

- **Active Inference Trading Engine**
  - Maintains and updates market beliefs using variational inference
  - Generates optimal trading actions through genetic evolution
  - Adapts to different market regimes automatically
  - Balances exploration and exploitation in trading decisions

- **Advanced Risk Management**
  - Dynamic position sizing based on market volatility and beliefs
  - Adaptive stop-loss and take-profit levels
  - Portfolio heat monitoring and risk-adjusted position sizing
  - Real-time risk metrics tracking with belief updates

- **Portfolio Management**
  - Dynamic capital allocation using active inference
  - Strategy weight optimization through belief updates
  - Performance tracking and attribution
  - Automated rebalancing based on market beliefs

- **System State Management**
  - Centralized state management through SystemState
  - Belief maintenance and updates
  - Real-time market data integration
  - Position and portfolio tracking

## System Architecture

```
trade-manager/
├── src/
│   ├── core/                   # Core trading components
│   │   ├── trading_session.py  # Main trading coordinator
│   │   ├── system_state.py     # Centralized state management
│   │   ├── trade_engine.py     # Trade execution engine
│   │   ├── portfolio.py        # Portfolio management
│   │   └── risk_manager.py     # Risk management system
│   ├── brokers/                # Broker integrations
│   │   ├── base_broker.py      # Abstract broker interface
│   │   └── interactive_brokers_adapter.py  # IB implementation
│   ├── config/                 # Configuration
│   │   └── trading_config.py   # System configuration
│   └── utils/                  # Utility functions
├── docs/
│   ├── system_components.md    # Component documentation
│   └── architecture.md         # System architecture
└── examples/
    └── paper_trading_example.py  # Example implementation
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The system is configured through `trading_config.py` which controls:
- Active Inference parameters and beliefs
- Risk management limits and thresholds
- Portfolio allocation rules and constraints
- Broker-specific settings
- Trading execution parameters

Example configuration:
```python
config = {
    # Active Inference parameters
    "learning_rate": 0.01,        # Belief update rate
    "exploration_factor": 0.1,    # Exploration vs exploitation
    "num_generations": 10,        # Genetic algorithm generations
    
    # Risk parameters
    "max_position_size": 0.1,     # Maximum position size
    "risk_per_trade": 0.02,       # Risk per trade
    "max_portfolio_heat": 1.0,    # Maximum portfolio risk
    
    # Portfolio parameters
    "max_concurrent_trades": 10,  # Maximum open positions
    "base_position_size": 0.01,   # Base position size
    "rebalance_threshold": 0.05   # Rebalancing threshold
}
```

## Documentation

- [System Components](docs/system_components.md) - Detailed component documentation
- [Architecture](docs/architecture.md) - System architecture and design

## Development

- Follow PEP 8 style guide
- Add type hints to all functions
- Write unit tests for new features
- Document all public interfaces

## Testing

```bash
pytest tests/
```

## License

This project is the private property the author (M. Preston Sparks) and is not intended for outside use. All rights reserved.