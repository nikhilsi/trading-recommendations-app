# backend/app/services/recommendation_service.py
"""
Professional recommendation service that orchestrates market data analysis,
technical analysis, and recommendation generation.
"""
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .market_data_service import MarketDataService
from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Professional recommendation engine that combines market data,
    technical analysis, and business logic to generate trading recommendations.
    """
    
    def __init__(self, api_key: str):
        self.market_data_service = MarketDataService(api_key)
        self.database_service = DatabaseService()
        
        # Configuration
        self.default_confidence_threshold = 50
        self.max_analysis_stocks = 8  # Limit for rate limiting
        
    def generate_recommendations(
        self, 
        confidence_threshold: int = None, 
        max_recommendations: int = 5
    ) -> Dict[str, Any]:
        """
        Generate comprehensive trading recommendations
        
        Args:
            confidence_threshold: Minimum confidence level (20-90)
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            Dictionary containing recommendations and metadata
        """
        if confidence_threshold is None:
            confidence_threshold = self.default_confidence_threshold
            
        logger.info(f"Generating recommendations with {confidence_threshold}% confidence threshold")
        
        try:
            # Get watchlist from database
            watchlist = self.database_service.get_watchlist()
            if not watchlist:
                # Initialize with defaults if empty
                self.database_service.initialize_default_watchlist()
                watchlist = self.database_service.get_watchlist()
            
            logger.info(f"Analyzing {len(watchlist)} stocks from watchlist")
            
            recommendations = []
            analyzed_count = 0
            errors = []
            
            for symbol in watchlist:
                if analyzed_count >= self.max_analysis_stocks:
                    logger.info(f"Stopping analysis at {analyzed_count} stocks (rate limiting)")
                    break
                
                try:
                    recommendation = self._analyze_single_stock(symbol, confidence_threshold)
                    
                    if recommendation:
                        recommendations.append(recommendation)
                        logger.info(f"✅ {symbol}: {recommendation['action']} (Confidence: {recommendation['confidence']}%)")
                        
                        # Save to database (simplified for now)
                        # self._save_recommendation(recommendation)
                    else:
                        logger.info(f"⚪ {symbol}: No strong signal (below threshold)")
                    
                except Exception as e:
                    error_msg = f"Error analyzing {symbol}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                
                analyzed_count += 1
                
                # Reduced rate limiting for better performance
                if analyzed_count < len(watchlist) and analyzed_count < self.max_analysis_stocks:
                    logger.info("⏳ Rate limiting (8 seconds)...")
                    time.sleep(8)  # Reduced from 12 seconds
            
            # Sort by confidence and limit results
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)
            final_recommendations = recommendations[:max_recommendations]
            
            logger.info(f"Generated {len(final_recommendations)} recommendations from {analyzed_count} stocks")
            
            return {
                'recommendations': final_recommendations,
                'generated_at': datetime.utcnow(),
                'market_status': self._get_market_status(),
                'count': len(final_recommendations),
                'parameters': {
                    'confidence_threshold': confidence_threshold,
                    'max_recommendations': max_recommendations,
                    'analyzed_stocks': analyzed_count,
                    'watchlist_size': len(watchlist)
                },
                'errors': errors if errors else None
            }
            
        except Exception as e:
            logger.error(f"Error in recommendation generation: {e}")
            return {
                'recommendations': [],
                'generated_at': datetime.utcnow(),
                'market_status': 'open',
                'count': 0,
                'error': f"Failed to generate recommendations: {str(e)}",
                'parameters': {
                    'confidence_threshold': confidence_threshold,
                    'max_recommendations': max_recommendations
                }
            }
    
    def _analyze_single_stock(self, symbol: str, confidence_threshold: int) -> Optional[Dict[str, Any]]:
        """
        Analyze a single stock and generate recommendation if it meets criteria
        """
        try:
            logger.info(f"Analyzing {symbol}...")
            
            # Get current quote
            quote = self.market_data_service.get_current_quote(symbol)
            if not quote:
                logger.warning(f"No quote data available for {symbol}")
                return None
            
            # Simple analysis for now (can be enhanced with technical analysis later)
            current_price = quote['price']
            change_pct = float(quote['change_percent'])
            volume = quote['volume']
            
            # Basic signal logic
            confidence = 40  # Base confidence
            action = "HOLD"
            reasoning = []
            
            # Price momentum analysis
            if change_pct > 3:
                confidence += 25
                action = "BUY"
                reasoning.append(f"Strong positive momentum (+{change_pct:.1f}%)")
            elif change_pct < -3:
                confidence += 20
                action = "SELL"
                reasoning.append(f"Strong negative momentum ({change_pct:.1f}%)")
            elif change_pct > 1:
                confidence += 15
                action = "BUY"
                reasoning.append(f"Positive momentum (+{change_pct:.1f}%)")
            elif change_pct < -1:
                confidence += 10
                action = "SELL"
                reasoning.append(f"Negative momentum ({change_pct:.1f}%)")
            
            # Volume analysis (simplified)
            if volume > 1000000:  # High volume
                confidence += 10
                reasoning.append("High trading volume supports signal")
            
            # Price level analysis (simplified)
            if current_price > 100:  # Higher-priced stocks often more stable
                confidence += 5
                reasoning.append("Established stock with good liquidity")
            
            # Only return if meets confidence threshold
            if confidence < confidence_threshold or action == "HOLD":
                return None
            
            # Calculate target price and stop loss
            if action == "BUY":
                target_multiplier = 1.06 + (confidence - 50) * 0.002
                stop_multiplier = 0.94
            else:
                target_multiplier = 0.94 - (confidence - 50) * 0.002
                stop_multiplier = 1.06
            
            target_price = round(current_price * target_multiplier, 2)
            stop_loss = round(current_price * stop_multiplier, 2)
            
            # Determine timeframe and risk
            if confidence >= 75:
                timeframe = "Day Trade"
                risk_level = "Medium"
            else:
                timeframe = "Swing (2-3 days)"
                risk_level = "Medium-High"
            
            return {
                'symbol': symbol,
                'company': f"{symbol} Inc",
                'action': action,
                'current_price': current_price,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'confidence': min(confidence, 90),  # Cap at 90%
                'timeframe': timeframe,
                'risk_level': risk_level,
                'reasoning': reasoning,
                'technicals': {
                    'rsi': 50 + (change_pct * 2),  # Simplified RSI approximation
                    'volume': f"{volume:,}",
                    'support': round(current_price * 0.95, 2),
                    'resistance': round(current_price * 1.05, 2)
                },
                'market_data': {
                    'change': quote['change'],
                    'change_percent': change_pct,
                    'volume': volume,
                    'previous_close': quote.get('previous_close')
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _get_market_status(self) -> str:
        """
        Determine current market status (simplified)
        """
        # Simplified market status - in production, you'd check actual market hours
        current_hour = datetime.now().hour
        
        if 9 <= current_hour <= 16:  # Rough US market hours
            return "open"
        else:
            return "closed"
    
    def get_single_stock_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed analysis for a single stock
        """
        try:
            recommendation = self._analyze_single_stock(symbol, confidence_threshold=0)
            
            if recommendation:
                return recommendation
            else:
                return {
                    'symbol': symbol,
                    'error': 'No analysis available - insufficient data or API error'
                }
                
        except Exception as e:
            logger.error(f"Error in single stock analysis for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a symbol exists and can be analyzed
        """
        try:
            return self.market_data_service.validate_symbol(symbol)
        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {e}")
            return False