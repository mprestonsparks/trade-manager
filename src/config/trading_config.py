"""
Trading system configuration parameters.
Centralizes all configuration for the trading system components.
"""

from typing import Dict, Any
from decimal import Decimal

def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration for the trading system.
    Includes parameters for optimization, risk management, and execution.
    """
    return {
        # Optimization parameters
        'optimization': {
            'learning_rate': 0.01,
            'population_size': 100,
            'num_generations': 10,
            'mutation_rate': 0.1,
            'exploration_factor': 0.1,
            'tournament_size': 5,
            'elite_size': 2
        },
        
        # Portfolio management
        'portfolio': {
            'max_position_size': 0.1,     # 10% of portfolio
            'max_concentration': 0.3,      # 30% in single asset
            'min_position_size': 0.01,     # 1% of portfolio
            'cash_buffer': 0.05,           # 5% cash buffer
            'max_leverage': 1.0,           # No leverage by default
            'rebalance_threshold': 0.05    # 5% deviation triggers rebalance
        },
        
        # Risk management
        'risk': {
            'var_limit': 0.02,            # 2% VaR limit
            'max_drawdown': 0.15,         # 15% max drawdown
            'position_var_limit': 0.01,    # 1% VaR per position
            'correlation_threshold': 0.7,   # Correlation threshold for diversification
            'min_sharpe_ratio': 0.5,       # Minimum Sharpe ratio
            'risk_free_rate': 0.02,        # 2% risk-free rate
            'max_heat': 0.8                # 80% max risk capacity
        },
        
        # Execution parameters
        'execution': {
            'min_trade_size': 1000,        # Minimum trade size in base currency
            'max_slippage': 0.002,         # 0.2% max slippage
            'market_impact_threshold': 0.001,  # 0.1% market impact threshold
            'min_time_between_trades': 60,  # 60 seconds between trades
            'execution_styles': {
                'default': 'MKT',
                'large_orders': 'TWAP',
                'volatile_market': 'LMT'
            }
        },
        
        # Performance metrics
        'performance': {
            'target_sharpe': 1.5,
            'target_sortino': 2.0,
            'max_drawdown_threshold': 0.2,
            'min_profit_factor': 1.5,
            'min_win_rate': 0.55
        },
        
        # Market analysis integration
        'market_analysis': {
            'update_interval': 60,  # Seconds between updates
            'min_data_points': 100,  # Minimum data points for analysis
            'confidence_threshold': 0.7,  # Minimum confidence for signals
            'state_memory': 5  # Number of previous states to consider
        },
        
        # Broker-specific settings
        'interactive_brokers': {
            'paper_trading': True,
            'port': 7497,  # Paper trading port
            'client_id': 1,
            'max_retries': 3,
            'retry_delay': 1,  # Seconds between retries
            'timeout': 30  # Connection timeout in seconds
        },
        
        # System settings
        'system': {
            'log_level': 'INFO',
            'max_concurrent_trades': 10,
            'heartbeat_interval': 5,  # Seconds between heartbeats
            'state_save_interval': 300,  # Save system state every 5 minutes
            'debug_mode': False
        }
    }

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from file or return defaults.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Configuration dictionary
    """
    if config_path:
        # TODO: Implement config file loading
        # This would load from JSON/YAML file
        pass
    
    return get_default_config()

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration parameters.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if configuration is valid
    """
    try:
        # Validate portfolio parameters
        assert 0 < config['portfolio']['max_position_size'] <= 1
        assert 0 < config['portfolio']['max_concentration'] <= 1
        assert 0 < config['portfolio']['min_position_size'] <= config['portfolio']['max_position_size']
        assert 0 <= config['portfolio']['cash_buffer'] < 1
        assert config['portfolio']['max_leverage'] >= 1
        
        # Validate risk parameters
        assert 0 < config['risk']['var_limit'] <= 0.1
        assert 0 < config['risk']['max_drawdown'] <= 1
        assert 0 < config['risk']['position_var_limit'] <= config['risk']['var_limit']
        assert 0 < config['risk']['correlation_threshold'] <= 1
        assert config['risk']['min_sharpe_ratio'] > 0
        assert 0 <= config['risk']['risk_free_rate'] <= 1
        
        # Validate execution parameters
        assert config['execution']['min_trade_size'] > 0
        assert 0 < config['execution']['max_slippage'] <= 0.05
        assert config['execution']['min_time_between_trades'] > 0
        
        # Validate performance parameters
        assert config['performance']['target_sharpe'] > 0
        assert config['performance']['target_sortino'] > 0
        assert 0 < config['performance']['max_drawdown_threshold'] <= 1
        assert config['performance']['min_profit_factor'] > 1
        assert 0 < config['performance']['min_win_rate'] <= 1
        
        return True
        
    except AssertionError:
        return False
    except KeyError:
        return False
