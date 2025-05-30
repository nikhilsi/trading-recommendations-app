# backend/app/services/polygon_recommendation_service.py
from .polygon_service import PolygonService
from .technical_analysis import TechnicalAnalysisService

class PolygonRecommendationService:
    def __init__(self, polygon_api_key: str):
        self.polygon = PolygonService(polygon_api_key)
        self.ta_service = TechnicalAnalysisService()
        # NO RATE LIMITING NEEDED!
        
    def generate_recommendations(self, confidence_threshold: int = 50, max_recommendations: int = 5):
        """Generate recommendations using Polygon data - NO RATE LIMITS!"""
        
        # Get ALL market movers at once
        market_data = self.polygon.get_market_movers()
        all_symbols = []
        
        # Combine different categories
        for category in ['gainers', 'losers', 'most_active', 'volume_movers']:
            all_symbols.extend([s['symbol'] for s in market_data.get(category, [])])
        
        # Remove duplicates
        all_symbols = list(set(all_symbols))[:50]  # Analyze top 50 instead of just 8!
        
        recommendations = []
        
        for symbol in all_symbols:
            # No sleep needed - Polygon has no rate limits!
            recommendation = self._analyze_with_polygon(symbol, confidence_threshold)
            if recommendation:
                recommendations.append(recommendation)
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'recommendations': recommendations[:max_recommendations],
            'analyzed_stocks': len(all_symbols),  # 50 instead of 8!
            'generated_at': datetime.utcnow(),
            'data_source': 'polygon'  # No more Alpha Vantage!
        }