# backend/app/core/config.py
"""
Application configuration
"""
import os
from typing import List

class Settings:
    # API Settings
    API_TITLE = "Trading Recommendations API"
    API_VERSION = "2.0.0"
    API_DESCRIPTION = """
    Professional stock trading recommendations API with real-time market data analysis,
    technical indicators, and comprehensive database persistence.
    """
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://frontend:3000",
    ]
    
    # Database
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://trading_user:trading_password123@postgres:5432/trading_app'
    )
    
    # API Keys
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()