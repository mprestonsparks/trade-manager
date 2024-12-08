# Trade Manager

A sophisticated trading system that combines Active Inference methodology with Genetic Algorithms for optimal trade execution and portfolio management.

## Core Features

- **Active Inference Trading Engine**
  - Maintains and updates market beliefs using variational inference
  - Generates optimal trading actions through genetic evolution
  - Adapts to different market regimes automatically
  - Balances exploration and exploitation in trading decisions

- **Advanced Risk Management**
  - Dynamic position sizing based on market volatility
  - Adaptive stop-loss and take-profit levels
  - Portfolio heat monitoring
  - Real-time risk metrics tracking

- **Portfolio Management**
  - Dynamic capital allocation
  - Strategy weight optimization
  - Performance tracking
  - Automated rebalancing

- **Market Analysis Integration**
  - Real-time signal processing
  - Market state analysis
  - Multi-timeframe analysis
  - Technical indicator integration

## System Architecture

```
trade-manager/
├── src/
│   ├── core/                   # Core trading components
│   │   ├── trade_engine.py     # Main trading engine
│   │   ├── portfolio.py        # Portfolio management
│   │   └── risk_manager.py     # Risk management system
│   ├── strategy/               # Trading strategies
│   │   ├── optimizer.py        # Active Inference optimizer
│   │   └── executor.py         # Strategy execution
│   ├── api/                    # External integrations
│   └── utils/                  # Utility functions
└── docs/
    ├── active_inference.md     # Active Inference documentation
    ├── api_reference.md        # API documentation
    └── architecture.md         # System architecture
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

The system is configured through a configuration dictionary that controls:
- Active Inference parameters
- Risk management limits
- Portfolio allocation rules
- Trading constraints

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
    
    # Trading parameters
    "max_concurrent_trades": 10,  # Maximum open positions
    "base_position_size": 0.01    # Base position size
}
```

## Documentation

- [Active Inference System](docs/active_inference.md) - Detailed explanation of the Active Inference trading system
- [API Reference](docs/api_reference.md) - API documentation
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

[License details to be added]