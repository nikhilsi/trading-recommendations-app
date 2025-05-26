# backend/app/services/market_data_service.py
"""
Professional market data service for Alpha Vantage API integration
with proper error handling and rate limiting.
"""
import requests
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketDataService:
    """
    Professional market data service with proper error handling and rate limiting
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.request_delay = 12  # Alpha Vantage free tier: 5 calls per minute
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TradingApp/1.0',
            'Accept': 'application/json'
        })
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting to respect API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            logger.info(f"Rate limiting: waiting {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict[str, str]) -> Optional[Dict]:
        """Make rate-limited request with proper error handling"""
        self._rate_limit()
        
        params['apikey'] = self.api_key
        
        try:
            logger.info(f"Fetching data for {params.get('symbol', 'unknown')}...")
            response = self.session.get(
                self.base_url, 
                params=params, 
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API-specific errors
            if "Error Message" in data:
                logger.error(f"API Error: {data['Error Message']}")
                return None
            
            if "Note" in data:
                logger.warning(f"Rate limit notice: {data['Note']}")
                return None
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {params.get('symbol')}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {params.get('symbol')}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {params.get('symbol')}: {e}")
            return None
    
    def get_current_quote(self, symbol: str) -> Optional[Dict]:
        """Get current quote for a symbol with validation and fallback"""
        if not symbol or len(symbol.strip()) == 0:
            logger.error("Empty symbol provided")
            return None
        
        symbol = symbol.upper().strip()
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        if not data:
            logger.error(f"No quote data found for {symbol}")
            return None
        
        # Check for rate limit
        if "Information" in data and "rate limit" in data["Information"].lower():
            logger.warning(f"API rate limit hit, using mock data for {symbol}")
            return self._get_mock_quote(symbol)
        
        if "Global Quote" not in data:
            logger.error(f"No quote data found for {symbol}")
            return self._get_mock_quote(symbol)  # Fallback to mock data
        
        try:
            quote = data["Global Quote"]
            
            return {
                'symbol': quote.get('01. symbol'),
                'price': float(quote.get('05. price', 0)),
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'latest_trading_day': quote.get('07. latest trading day'),
                'previous_close': float(quote.get('08. previous close', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                'timestamp': datetime.utcnow()
            }
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing quote data for {symbol}: {e}")
            return self._get_mock_quote(symbol)
    
    def _get_mock_quote(self, symbol: str) -> Dict:
        """Generate mock quote data for testing when API limit is hit"""
        import random
        
        # Base prices for common stocks
        base_prices = {
            'AAPL': 190.0,
            'MSFT': 380.0,
            'GOOGL': 140.0,
            'TSLA': 250.0,
            'NVDA': 900.0,
            'AMD': 160.0,
            'META': 320.0,
            'AMZN': 150.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Generate realistic price movement
        change_pct = random.uniform(-5.0, 5.0)  # -5% to +5%
        current_price = base_price * (1 + change_pct / 100)
        change = current_price - base_price
        
        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'open': round(base_price * random.uniform(0.98, 1.02), 2),
            'high': round(current_price * random.uniform(1.0, 1.03), 2),
            'low': round(current_price * random.uniform(0.97, 1.0), 2),
            'volume': random.randint(1000000, 50000000),
            'latest_trading_day': datetime.utcnow().strftime('%Y-%m-%d'),
            'previous_close': round(base_price, 2),
            'change': round(change, 2),
            'change_percent': f"{change_pct:.2f}",
            'timestamp': datetime.utcnow(),
            'mock_data': True  # Flag to indicate this is mock data
        }
    
    def get_daily_prices(self, symbol: str, outputsize: str = "compact") -> Optional[Dict]:
        """Get daily price data with proper validation"""
        if not symbol:
            return None
        
        symbol = symbol.upper().strip()
        
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': outputsize  # compact = 100 days, full = 20+ years
        }
        
        data = self._make_request(params)
        if not data or "Time Series (Daily)" not in data:
            logger.error(f"No daily data found for {symbol}")
            return None
        
        try:
            time_series = data["Time Series (Daily)"]
            
            price_data = []
            for date_str in sorted(time_series.keys(), reverse=True):
                prices = time_series[date_str]
                price_data.append({
                    'date': date_str,
                    'open': float(prices['1. open']),
                    'high': float(prices['2. high']),
                    'low': float(prices['3. low']),
                    'close': float(prices['4. close']),
                    'adjusted_close': float(prices['5. adjusted close']),
                    'volume': int(prices['6. volume']),
                    'dividend': float(prices['7. dividend amount']),
                    'split': float(prices['8. split coefficient'])
                })
            
            return {
                'symbol': symbol,
                'last_refreshed': data["Meta Data"]["3. Last Refreshed"],
                'data': price_data
            }
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing daily data for {symbol}: {e}")
            return None
    
    def get_company_overview(self, symbol: str) -> Optional[Dict]:
        """Get company fundamental data"""
        if not symbol:
            return None
        
        symbol = symbol.upper().strip()
        
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        if not data or not data.get('Symbol'):
            logger.error(f"No company data found for {symbol}")
            return None
        
        try:
            return {
                'symbol': data.get('Symbol'),
                'name': data.get('Name'),
                'sector': data.get('Sector'),
                'industry': data.get('Industry'),
                'market_cap': data.get('MarketCapitalization'),
                'pe_ratio': data.get('PERatio'),
                'price_to_book': data.get('PriceToBookRatio'),
                'dividend_yield': data.get('DividendYield'),
                'eps': data.get('EPS'),
                'beta': data.get('Beta'),
                '52_week_high': data.get('52WeekHigh'),
                '52_week_low': data.get('52WeekLow'),
                'description': data.get('Description')
            }
        except Exception as e:
            logger.error(f"Error parsing company data for {symbol}: {e}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol exists by trying to get a quote"""
        quote = self.get_current_quote(symbol)
        return quote is not None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()