# backend/app/services/database_service.py
"""
Professional database service layer with proper error handling,
connection management, and data access patterns.
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, func

from models.database import (
    SessionLocal, Stock, StockPrice, Recommendation, 
    TechnicalIndicator, Watchlist, get_db
)
from schemas.stock import HistoricalRecommendation

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Professional database service with comprehensive data access methods
    and proper error handling.
    """
    
    def __init__(self):
        self.session_local = SessionLocal
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions with automatic cleanup
        """
        session = self.session_local()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Test database connectivity
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    # Watchlist Operations
    def get_watchlist(self) -> List[str]:
        """
        Get active watchlist symbols
        
        Returns:
            List of stock symbols
        """
        try:
            with self.get_session() as session:
                watchlist_items = session.query(Watchlist).filter(
                    Watchlist.is_active == True
                ).order_by(Watchlist.symbol).all()
                
                return [item.symbol for item in watchlist_items]
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
            return []
    
    def add_to_watchlist(self, symbol: str) -> bool:
        """
        Add symbol to watchlist
        
        Args:
            symbol: Stock symbol to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            symbol = symbol.upper().strip()
            
            with self.get_session() as session:
                # Check if symbol already exists
                existing = session.query(Watchlist).filter(
                    Watchlist.symbol == symbol
                ).first()
                
                if existing:
                    # Reactivate if exists
                    existing.is_active = True
                    existing.added_at = datetime.utcnow()
                else:
                    # Create new entry
                    new_item = Watchlist(symbol=symbol)
                    session.add(new_item)
                
                logger.info(f"Added {symbol} to watchlist")
                return True
                
        except Exception as e:
            logger.error(f"Error adding {symbol} to watchlist: {e}")
            return False
    
    def remove_from_watchlist(self, symbol: str) -> bool:
        """
        Remove symbol from watchlist (mark as inactive)
        
        Args:
            symbol: Stock symbol to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            symbol = symbol.upper().strip()
            
            with self.get_session() as session:
                watchlist_item = session.query(Watchlist).filter(
                    Watchlist.symbol == symbol
                ).first()
                
                if watchlist_item:
                    watchlist_item.is_active = False
                    logger.info(f"Removed {symbol} from watchlist")
                    return True
                else:
                    logger.warning(f"Symbol {symbol} not found in watchlist")
                    return False
                    
        except Exception as e:
            logger.error(f"Error removing {symbol} from watchlist: {e}")
            return False
    
    # Stock Data Operations
    def save_stock_price(self, symbol: str, price_data: Dict[str, Any]) -> bool:
        """
        Save stock price data
        
        Args:
            symbol: Stock symbol
            price_data: Dictionary containing price information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            symbol = symbol.upper().strip()
            
            with self.get_session() as session:
                # Create or update stock price record
                today = date.today()
                
                existing_price = session.query(StockPrice).filter(
                    StockPrice.symbol == symbol,
                    StockPrice.date == today
                ).first()
                
                if existing_price:
                    # Update existing record
                    existing_price.price = price_data.get('price', existing_price.price)
                    existing_price.volume = price_data.get('volume', existing_price.volume)
                    existing_price.high = price_data.get('high', existing_price.high)
                    existing_price.low = price_data.get('low', existing_price.low)
                    existing_price.created_at = datetime.utcnow()
                else:
                    # Create new record
                    new_price = StockPrice(
                        symbol=symbol,
                        price=price_data.get('price', 0.0),
                        volume=price_data.get('volume', 0),
                        high=price_data.get('high'),
                        low=price_data.get('low'),
                        open_price=price_data.get('open'),
                        close_price=price_data.get('close', price_data.get('price', 0.0)),
                        date=today
                    )
                    session.add(new_price)
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving stock price for {symbol}: {e}")
            return False
    
    def get_historical_prices(self, symbol: str, days: int = 100) -> List[Dict[str, Any]]:
        """
        Get historical price data for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days to retrieve
            
        Returns:
            List of price data dictionaries
        """
        try:
            symbol = symbol.upper().strip()
            
            with self.get_session() as session:
                prices = session.query(StockPrice).filter(
                    StockPrice.symbol == symbol
                ).order_by(StockPrice.date.desc()).limit(days).all()
                
                return [
                    {
                        'date': price.date.isoformat(),
                        'price': float(price.price),
                        'volume': price.volume,
                        'high': float(price.high) if price.high else None,
                        'low': float(price.low) if price.low else None,
                        'open': float(price.open_price) if price.open_price else None,
                        'close': float(price.close_price) if price.close_price else None
                    }
                    for price in reversed(prices)  # Return oldest first
                ]
                
        except Exception as e:
            logger.error(f"Error fetching historical prices for {symbol}: {e}")
            return []
    
    # Recommendation Operations
    def save_recommendation(self, recommendation_data: Dict[str, Any]) -> bool:
        """
        Save recommendation to database
        
        Args:
            recommendation_data: Dictionary containing recommendation information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                new_recommendation = Recommendation(
                    symbol=recommendation_data['symbol'],
                    action=recommendation_data['action'],
                    current_price=recommendation_data['current_price'],
                    target_price=recommendation_data.get('target_price'),
                    stop_loss=recommendation_data.get('stop_loss'),
                    confidence=recommendation_data['confidence'],
                    reasoning=json.dumps(recommendation_data.get('reasoning', [])),
                    timeframe=recommendation_data.get('timeframe'),
                    risk_level=recommendation_data.get('risk_level'),
                    generated_at=datetime.utcnow()
                )
                session.add(new_recommendation)
                
                logger.info(f"Saved recommendation for {recommendation_data['symbol']}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
            return False
    
    def get_recommendations_history(self, limit: int = 50) -> List[HistoricalRecommendation]:
        """
        Get historical recommendations
        
        Args:
            limit: Maximum number of recommendations to return
            
        Returns:
            List of historical recommendations
        """
        try:
            with self.get_session() as session:
                recommendations = session.query(Recommendation).order_by(
                    Recommendation.generated_at.desc()
                ).limit(limit).all()
                
                result = []
                for rec in recommendations:
                    try:
                        reasoning = json.loads(rec.reasoning) if rec.reasoning else []
                    except json.JSONDecodeError:
                        reasoning = [rec.reasoning] if rec.reasoning else []
                    
                    result.append(HistoricalRecommendation(
                        id=str(rec.id),
                        symbol=rec.symbol,
                        action=rec.action,
                        current_price=rec.current_price,
                        target_price=rec.target_price,
                        confidence=rec.confidence,
                        reasoning=reasoning,
                        generated_at=rec.generated_at,
                        is_active=rec.is_active
                    ))
                
                return result
                
        except Exception as e:
            logger.error(f"Error fetching recommendations history: {e}")
            return []
    
    # Statistics Operations
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics
        
        Returns:
            Dictionary containing various database statistics
        """
        try:
            with self.get_session() as session:
                # Count records in each table
                stats = {
                    'total_stocks': session.query(Stock).count(),
                    'total_recommendations': session.query(Recommendation).count(),
                    'total_prices': session.query(StockPrice).count(),
                    'watchlist_size': session.query(Watchlist).filter(
                        Watchlist.is_active == True
                    ).count(),
                    'active_recommendations': session.query(Recommendation).filter(
                        Recommendation.is_active == True
                    ).count(),
                    'last_updated': datetime.utcnow()
                }
                
                # Get recent activity
                recent_recommendations = session.query(Recommendation).filter(
                    Recommendation.generated_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                ).count()
                
                stats['recommendations_today'] = recent_recommendations
                
                return stats
                
        except Exception as e:
            logger.error(f"Error fetching database stats: {e}")
            return {
                'error': 'Failed to fetch statistics',
                'total_stocks': 0,
                'total_recommendations': 0,
                'total_prices': 0,
                'watchlist_size': 0,
                'last_updated': datetime.utcnow()
            }
    
    # Maintenance Operations
    def cleanup_old_data(self, days_to_keep: int = 90) -> bool:
        """
        Clean up old data to maintain database performance
        
        Args:
            days_to_keep: Number of days of data to retain
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0) - \
                         datetime.timedelta(days=days_to_keep)
            
            with self.get_session() as session:
                # Delete old stock prices
                old_prices = session.query(StockPrice).filter(
                    StockPrice.created_at < cutoff_date
                ).delete()
                
                # Mark old recommendations as inactive
                session.query(Recommendation).filter(
                    Recommendation.generated_at < cutoff_date
                ).update({'is_active': False})
                
                logger.info(f"Cleaned up {old_prices} old price records")
                return True
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False
    
    def initialize_default_watchlist(self) -> bool:
        """
        Initialize watchlist with default symbols if empty
        
        Returns:
            True if successful, False otherwise
        """
        try:
            current_watchlist = self.get_watchlist()
            
            if not current_watchlist:
                default_symbols = [
                    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
                    'NVDA', 'AMD', 'META', 'NFLX', 'DIS'
                ]
                
                for symbol in default_symbols:
                    self.add_to_watchlist(symbol)
                
                logger.info(f"Initialized watchlist with {len(default_symbols)} default symbols")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing default watchlist: {e}")
            return False