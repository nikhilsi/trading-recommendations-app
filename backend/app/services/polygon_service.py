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
        
    def get_market_snapshot(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get complete market snapshot - gainers, losers, most active"""
        try:
            # Get gainers
            gainers_url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/gainers?apiKey={self.api_key}"
            gainers_resp = requests.get(gainers_url)
            gainers_data = gainers_resp.json() if gainers_resp.status_code == 200 else {"tickers": []}
            
            # Get losers
            losers_url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/losers?apiKey={self.api_key}"
            losers_resp = requests.get(losers_url)
            losers_data = losers_resp.json() if losers_resp.status_code == 200 else {"tickers": []}
            
            # Process gainers
            gainers = []
            for ticker in gainers_data.get("tickers", [])[:20]:
                gainers.append({
                    'symbol': ticker['ticker'],
                    'price': ticker['day']['c'],  # Close price
                    'change': ticker['day']['c'] - ticker['day']['o'],
                    'change_percent': ((ticker['day']['c'] - ticker['day']['o']) / ticker['day']['o'] * 100),
                    'volume': ticker['day']['v'],
                    'data_source': 'polygon'
                })
            
            # Process losers
            losers = []
            for ticker in losers_data.get("tickers", [])[:20]:
                losers.append({
                    'symbol': ticker['ticker'],
                    'price': ticker['day']['c'],
                    'change': ticker['day']['c'] - ticker['day']['o'],
                    'change_percent': ((ticker['day']['c'] - ticker['day']['o']) / ticker['day']['o'] * 100),
                    'volume': ticker['day']['v'],
                    'data_source': 'polygon'
                })
            
            logger.info(f"Found {len(gainers)} gainers, {len(losers)} losers")
            
            return {
                'gainers': gainers,
                'losers': losers,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market snapshot: {e}")
            return {'gainers': [], 'losers': []}