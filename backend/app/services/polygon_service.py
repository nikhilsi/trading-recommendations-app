# backend/app/services/polygon_service.py
"""
Polygon.io integration for professional market scanning
"""
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PolygonService:
    """
    Professional market data service using Polygon.io
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        self.base_url = "https://api.polygon.io"
        
    def get_market_movers(self, mover_type: str = 'all') -> Dict[str, Any]:
        """
        Get comprehensive market movers with multiple categories
        """
        try:
            result = {}
            
            # Get full market snapshot (all tickers)
            snapshot_url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={self.api_key}"
            response = requests.get(snapshot_url)
            
            if response.status_code != 200:
                logger.error(f"Polygon API error: {response.status_code}")
                return self._get_fallback_data()
            
            data = response.json()
            tickers = data.get('tickers', [])
            
            # Filter and process tickers
            processed_tickers = []
            for ticker in tickers:
                if ticker.get('day') and ticker['day'].get('o') and ticker['day'].get('c'):
                    try:
                        open_price = ticker['day']['o']
                        close_price = ticker['day']['c']
                        volume = ticker['day']['v']
                        
                        # Skip if invalid data
                        if open_price <= 0 or volume <= 0:
                            continue
                        
                        change_pct = ((close_price - open_price) / open_price) * 100
                        
                        processed_tickers.append({
                            'symbol': ticker['ticker'],
                            'price': close_price,
                            'change': close_price - open_price,
                            'change_percent': change_pct,
                            'volume': volume,
                            'market_cap': ticker.get('market_cap', 0),
                            'data_source': 'polygon'
                        })
                    except Exception as e:
                        continue
            
            # Sort for different categories
            # Gainers
            gainers = sorted(processed_tickers, key=lambda x: x['change_percent'], reverse=True)[:20]
            
            # Losers
            losers = sorted(processed_tickers, key=lambda x: x['change_percent'])[:20]
            
            # Most Active (by volume)
            most_active = sorted(processed_tickers, key=lambda x: x['volume'], reverse=True)[:20]
            
            # High Volume Unusual Activity (volume spike + price movement)
            volume_movers = [t for t in processed_tickers if abs(t['change_percent']) > 2]
            volume_movers = sorted(volume_movers, key=lambda x: x['volume'], reverse=True)[:20]
            
            result = {
                'gainers': gainers,
                'losers': losers,
                'most_active': most_active,
                'volume_movers': volume_movers,
                'total_symbols': len(processed_tickers),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Processed {len(processed_tickers)} symbols from Polygon")
            return result
            
        except Exception as e:
            logger.error(f"Error in get_market_movers: {e}")
            return self._get_fallback_data()

    def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector performance data"""
        # For now, return placeholder - Polygon requires higher tier for sector data
        # In production, you'd use their aggregates endpoint
        return {
            'sectors': [
                {'name': 'Technology', 'change_percent': 1.2},
                {'name': 'Healthcare', 'change_percent': -0.5},
                {'name': 'Finance', 'change_percent': 0.8},
                {'name': 'Energy', 'change_percent': 2.1},
                {'name': 'Consumer', 'change_percent': -0.3}
            ],
            'timestamp': datetime.now().isoformat()
        }

    def _get_fallback_data(self) -> Dict[str, Any]:
        """Fallback empty data structure"""
        return {
            'gainers': [],
            'losers': [],
            'most_active': [],
            'volume_movers': [],
            'total_symbols': 0,
            'timestamp': datetime.now().isoformat()
        }