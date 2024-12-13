"""
Configuration management for the trade manager service.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    METRICS_PORT: int = 8091
    
    # Service Dependencies
    MARKET_ANALYSIS_HOST: str = "market-analysis"
    MARKET_ANALYSIS_PORT: int = 8000
    TRADE_DISCOVERY_HOST: str = "trade-discovery"
    TRADE_DISCOVERY_PORT: int = 8002
    
    # Monitoring Configuration
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Trading Configuration
    MAX_POSITION_SIZE: float = 100000
    RISK_PERCENTAGE: float = 2
    MAX_DRAWDOWN: float = 10
    STOP_LOSS_PERCENTAGE: float = 2
    TAKE_PROFIT_PERCENTAGE: float = 4
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/trade_manager"
    
    # Security
    API_KEY: str = "your-api-key-here"
    API_KEY_HEADER: str = "X-API-Key"
    
    # Development
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache to ensure we don't load .env file multiple times.
    """
    return Settings()

# Create a global settings instance
settings = get_settings()
