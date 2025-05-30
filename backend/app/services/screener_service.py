# backend/app/services/screener_service.py
"""
Professional stock screener with technical indicators
"""
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .polygon_service import PolygonService
from .technical_analysis import TechnicalAnalysisService

logger = logging.getLogger(__name__)

class ScreenerService:
    def __init__(self, polygon_api_key: str):
        self.polygon = PolygonService(polygon_api_key)
        self.polygon_api_key = polygon_api_key
        self.ta = TechnicalAnalysisService()
        
    def screen_stocks(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Screen stocks based on multiple criteria
        
        Filters:
        - min_price, max_price: Price range
        - volume_filter: '1m', '5m', '10m', 'unusual'
        - change_filter: 'up5', 'up2', 'down2', 'down5'
        - above_sma_20: Boolean
        - above_sma_50: Boolean
        - rsi_oversold: Boolean (RSI < 30)
        - rsi_overbought: Boolean (RSI > 70)
        - scan_type: Type of scan (momentum, volume, all, etc.)
        """
        try:
            scan_type = filters.get('scan_type', 'momentum')
            
            if scan_type == 'all':
                # Get FULL market snapshot for "ALL" mode
                logger.info("Fetching full market snapshot for ALL stocks...")
                url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={self.polygon_api_key}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    raw_tickers = data.get('tickers', [])
                    
                    # Convert all tickers to our format
                    all_tickers = []
                    for ticker_data in raw_tickers:
                        if ticker_data.get('day') and ticker_data['day'].get('c'):
                            day = ticker_data['day']
                            prev_day = ticker_data.get('prevDay', {})
                            
                            if prev_day.get('c'):
                                change = day['c'] - prev_day['c']
                                change_pct = (change / prev_day['c']) * 100
                                
                                all_tickers.append({
                                    'symbol': ticker_data['ticker'],
                                    'price': day['c'],
                                    'volume': day.get('v', 0),
                                    'change': change,
                                    'change_percent': change_pct
                                })
                    
                    logger.info(f"Processing {len(all_tickers)} stocks for ALL mode")
                else:
                    logger.error("Failed to get full market snapshot")
                    all_tickers = []
            else:
                # Use market movers for specific scan types
                market_data = self.polygon.get_market_movers()
                all_tickers = self._get_all_tickers(market_data)
                logger.info(f"Processing {len(all_tickers)} stocks for {scan_type} scan")
            
            # First pass: Basic filters (price, volume, change)
            filtered_tickers = self._apply_basic_filters(all_tickers, filters)
            
            # Second pass: Technical filters (if any selected)
            if self._has_technical_filters(filters):
                filtered_tickers = self._apply_technical_filters(filtered_tickers, filters)
            
            # Format results to match scanner format
            formatted_results = []
            for ticker in filtered_tickers[:100]:  # Limit processing to top 100
                # Generate signals based on data
                signals = []
                change_pct = ticker.get('change_percent', 0)
                volume = ticker.get('volume', 0)
                
                if change_pct > 2:
                    signals.append(f"Up {change_pct:.1f}%")
                elif change_pct < -2:
                    signals.append(f"Down {change_pct:.1f}%")
                
                if volume > 10000000:
                    signals.append(f"High volume: {volume:,}")
                elif volume > 5000000:
                    signals.append(f"Good volume: {volume:,}")
                
                # Add technical signals if available
                if ticker.get('rsi'):
                    if ticker['rsi'] < 30:
                        signals.append(f"Oversold RSI: {ticker['rsi']:.0f}")
                    elif ticker['rsi'] > 70:
                        signals.append(f"Overbought RSI: {ticker['rsi']:.0f}")
                
                # Calculate score
                score = 50  # Base score for passing filters
                if abs(change_pct) > 5:
                    score += 30
                elif abs(change_pct) > 2:
                    score += 20
                
                if volume > 10000000:
                    score += 20
                elif volume > 5000000:
                    score += 10
                
                formatted_results.append({
                    'symbol': ticker['symbol'],
                    'price': ticker['price'],
                    'change_percent': change_pct,
                    'volume': volume,
                    'score': score,
                    'signals': signals if signals else ['Matched filter criteria'],
                    'scan_type': scan_type,
                    'data_source': 'polygon'
                })
            
            # Sort by score
            formatted_results.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'results': formatted_results[:50],
                'opportunities': formatted_results[:50],  # For compatibility
                'total_screened': len(all_tickers),
                'total_matched': len(filtered_tickers),
                'filters_applied': filters,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Screener error: {e}")
            return {'results': [], 'opportunities': [], 'error': str(e)}
    
    def _get_all_tickers(self, market_data: Dict) -> List[Dict]:
        """Extract all tickers from market data"""
        all_tickers = []
        
        # Combine all categories
        for category in ['gainers', 'losers', 'most_active', 'volume_movers']:
            tickers = market_data.get(category, [])
            for ticker in tickers:
                # Avoid duplicates
                if not any(t['symbol'] == ticker['symbol'] for t in all_tickers):
                    all_tickers.append(ticker)
        
        return all_tickers
    
    def _apply_basic_filters(self, tickers: List[Dict], filters: Dict) -> List[Dict]:
        """Apply price, volume, and change filters"""
        results = []
        
        for ticker in tickers:
            # Price filter (convert filter values to float)
            price = float(ticker.get('price', 0))
            min_price = float(filters.get('min_price', 0))
            max_price = float(filters.get('max_price', 0))
            
            if min_price > 0 and price < min_price:
                continue
            if max_price > 0 and price > max_price:
                continue
            
            # Volume filter
            volume = int(ticker.get('volume', 0))
            volume_filter = filters.get('volume_filter', 'any')
            
            if volume_filter == '1m' and volume < 1000000:
                continue
            elif volume_filter == '5m' and volume < 5000000:
                continue
            elif volume_filter == '10m' and volume < 10000000:
                continue
            
            # Change filter
            change_pct = float(ticker.get('change_percent', 0))
            change_filter = filters.get('change_filter', 'any')
            
            if change_filter == 'up5' and change_pct < 5:
                continue
            elif change_filter == 'up2' and change_pct < 2:
                continue
            elif change_filter == 'down2' and change_pct > -2:
                continue
            elif change_filter == 'down5' and change_pct > -5:
                continue
            
            results.append(ticker)
        
        return results
    
    def _apply_technical_filters(self, tickers: List[Dict], filters: Dict) -> List[Dict]:
        """Apply technical indicator filters"""
        results = []
        
        for ticker in tickers:
            symbol = ticker['symbol']
            
            # Get historical data for technical analysis
            historical = self.polygon.get_historical_bars(symbol, days=60)
            if not historical or len(historical) < 20:
                continue
            
            # Calculate technical indicators
            prices = [bar['close'] for bar in historical]
            current_price = ticker['price']
            
            # SMA calculations
            if filters.get('above_sma_20') or filters.get('above_sma_50'):
                sma_20 = self.ta.calculate_sma(prices, 20)
                if filters.get('above_sma_20') and current_price < sma_20:
                    continue
                
                if filters.get('above_sma_50') and len(prices) >= 50:
                    sma_50 = self.ta.calculate_sma(prices, 50)
                    if current_price < sma_50:
                        continue
            
            # RSI filter
            if filters.get('rsi_oversold') or filters.get('rsi_overbought'):
                rsi = self.ta.calculate_rsi(prices)
                if filters.get('rsi_oversold') and rsi > 30:
                    continue
                if filters.get('rsi_overbought') and rsi < 70:
                    continue
                
                # Add RSI to ticker data
                ticker['rsi'] = rsi
            
            results.append(ticker)
        
        return results
    
    def _has_technical_filters(self, filters: Dict) -> bool:
        """Check if any technical filters are enabled"""
        return any([
            filters.get('above_sma_20', False),
            filters.get('above_sma_50', False),
            filters.get('rsi_oversold', False),
            filters.get('rsi_overbought', False)
        ])
    
    def _score_and_sort(self, tickers: List[Dict]) -> List[Dict]:
        """Score and sort results by relevance"""
        for ticker in tickers:
            score = 0
            
            # Score based on volume
            volume = ticker.get('volume', 0)
            if volume > 10000000:
                score += 20
            elif volume > 5000000:
                score += 10
            
            # Score based on price change
            change_pct = abs(ticker.get('change_percent', 0))
            if change_pct > 5:
                score += 30
            elif change_pct > 2:
                score += 15
            
            ticker['relevance_score'] = score
        
        # Sort by score, then by volume
        return sorted(tickers, key=lambda x: (x.get('relevance_score', 0), x.get('volume', 0)), reverse=True)