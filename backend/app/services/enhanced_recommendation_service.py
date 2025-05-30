# backend/app/services/enhanced_recommendation_service.py
"""
Enhanced recommendation service using Polygon.io
NO RATE LIMITS! Analyze 50+ stocks instead of 8!
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .polygon_service import PolygonService
from .database_service import DatabaseService
from .technical_analysis import TechnicalAnalysisService

logger = logging.getLogger(__name__)

class EnhancedRecommendationService:
    def __init__(self, polygon_api_key: str):
        self.polygon = PolygonService(polygon_api_key)
        self.database = DatabaseService()
        self.ta_service = TechnicalAnalysisService()
        
    def generate_recommendations(self, confidence_threshold: int = 50, max_recommendations: int = 5):
        """Generate recommendations for WATCHLIST stocks using Polygon"""
        logger.info("Generating recommendations for watchlist...")
        
        try:
            # Get YOUR watchlist from database!
            watchlist = self.database.get_watchlist()
            if not watchlist:
                self.database.initialize_default_watchlist()
                watchlist = self.database.get_watchlist()
            
            logger.info(f"Analyzing {len(watchlist)} stocks from YOUR watchlist")
            
            recommendations = []
            
            for symbol in watchlist:
                # Analyze each watchlist stock with Polygon (no rate limits!)
                rec = self._analyze_stock_fast(symbol, confidence_threshold)
                if rec:
                    recommendations.append(rec)
                    logger.info(f"✅ {symbol}: {rec['action']} (Confidence: {rec['confidence']}%)")
            
            # Sort by confidence
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)
            
            return {
                'recommendations': recommendations[:max_recommendations],
                'generated_at': datetime.utcnow(),
                'market_status': 'open',
                'count': len(recommendations[:max_recommendations]),
                'parameters': {
                    'confidence_threshold': confidence_threshold,
                    'max_recommendations': max_recommendations,
                    'analyzed_stocks': len(watchlist),  # Your watchlist size
                    'watchlist_size': len(watchlist),
                    'data_source': 'polygon'
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {
                'recommendations': [],
                'error': str(e),
                'generated_at': datetime.utcnow()
            }
    
    def _analyze_stock_fast(self, symbol: str, confidence_threshold: int) -> Optional[Dict]:
        """Fast analysis using Polygon data with more reasonable thresholds"""
        try:
            # Get current data from Polygon
            snapshot = self.polygon.get_stock_snapshot(symbol)
            if not snapshot:
                return None
            
            # Basic data
            current_price = snapshot['price']
            change_pct = snapshot.get('change_percent', 0)
            volume = snapshot['volume']
            
            # Start with base confidence
            confidence = 30  # Lower base
            action = "HOLD"
            reasoning = []
            
            # More reasonable momentum thresholds
            if change_pct > 1.5:  # Lowered from 3%
                confidence += 25
                action = "BUY"
                reasoning.append(f"Positive momentum: +{change_pct:.1f}%")
            elif change_pct > 0.5:
                confidence += 15
                action = "BUY"
                reasoning.append(f"Mild uptrend: +{change_pct:.1f}%")
            elif change_pct < -1.5:  # Lowered from -3%
                confidence += 25
                action = "SELL"
                reasoning.append(f"Negative momentum: {change_pct:.1f}%")
            elif change_pct < -0.5:
                confidence += 15
                action = "SELL"
                reasoning.append(f"Mild downtrend: {change_pct:.1f}%")
            
            # Volume analysis
            if volume > 5000000:  # Lowered from 10M
                confidence += 10
                reasoning.append(f"Good volume: {volume:,}")
            
            # Price level bonus
            if current_price > 50:
                confidence += 5
                reasoning.append("Established stock")
            
            # Log what we're analyzing
            logger.info(f"{symbol}: price=${current_price:.2f}, change={change_pct:.1f}%, confidence={confidence}, action={action}")
            
            # Only return if meets threshold AND has a signal
            if confidence < confidence_threshold or action == "HOLD":
                logger.info(f"{symbol}: Below threshold or HOLD - skipping")
                return None
            
            # Calculate targets
            if action == "BUY":
                target_price = current_price * 1.03  # 3% target
                stop_loss = current_price * 0.98     # 2% stop
            else:
                target_price = current_price * 0.97
                stop_loss = current_price * 1.02
            
            return {
                'symbol': symbol,
                'company': f"{symbol} Inc",
                'action': action,
                'current_price': current_price,
                'target_price': round(target_price, 2),
                'stop_loss': round(stop_loss, 2),
                'confidence': min(confidence, 90),
                'timeframe': 'Day Trade' if confidence > 60 else 'Swing Trade',
                'risk_level': 'Medium',
                'reasoning': reasoning,
                'market_data': {
                    'change': snapshot.get('change', 0),
                    'change_percent': change_pct,
                    'volume': volume
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
        
    def scan_market_opportunities(self, confidence_threshold: int = 50, max_results: int = 10):
        """Scan entire market for opportunities (separate from watchlist)"""
        # Your existing code that analyzes 50 market movers
        # This could be called from a different endpoint