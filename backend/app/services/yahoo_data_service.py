# backend/app/services/yahoo_data_service.py
"""
Yahoo Finance integration for free market data
No API key required!
"""
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class YahooDataService:
    """
    Free market data service using Yahoo Finance
    """
    
    def __init__(self):
        # Popular stock universes for scanning
        self.universes = {
            'mega_cap_tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA'],
            'high_volume': ['SPY', 'QQQ', 'AAPL', 'TSLA', 'AMD', 'NVDA', 'BAC', 'F'],
            'momentum_stocks': ['NVDA', 'AMD', 'MELI', 'NFLX', 'AVGO', 'CRM', 'NOW'],
            'popular_retail': ['GME', 'AMC', 'BB', 'PLTR', 'SOFI', 'NIO', 'RIVN'],
            'sp500_leaders': self._get_sp500_leaders()
        }
    
    def _get_sp500_leaders(self) -> List[str]:
        """Get top S&P 500 stocks by market cap"""
        # Top 30 S&P 500 stocks
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            'UNH', 'XOM', 'JPM', 'JNJ', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK',
            'ABBV', 'PEP', 'COST', 'AVGO', 'KO', 'WMT', 'MCD', 'CSCO', 'CRM',
            'ACN', 'LIN', 'TMO'
        ]
    
    def get_market_movers(self, mover_type: str = 'gainers') -> List[Dict[str, Any]]:
        """
        Get market movers (gainers, losers, most active)
        
        Args:
            mover_type: 'gainers', 'losers', or 'active'
            
        Returns:
            List of stock data with price and volume info
        """
        try:
            # Get a universe of stocks to check
            symbols = self.universes['sp500_leaders'] + self.universes['momentum_stocks']
            symbols = list(set(symbols))  # Remove duplicates
            
            logger.info(f"Scanning {len(symbols)} stocks for {mover_type}")
            
            # Download today's data for all symbols at once (very efficient!)
            data = yf.download(
                symbols, 
                period='2d',  # Get 2 days to calculate change
                interval='1d',
                group_by='ticker',
                auto_adjust=True,
                prepost=True,
                threads=True
            )
            
            movers = []
            
            for symbol in symbols:
                try:
                    if symbol in data.columns.levels[0]:
                        # Get the last 2 days of data
                        symbol_data = data[symbol].dropna()
                        
                        if len(symbol_data) >= 2:
                            current_price = symbol_data['Close'].iloc[-1]
                            prev_price = symbol_data['Close'].iloc[-2]
                            volume = symbol_data['Volume'].iloc[-1]
                            
                            change_pct = ((current_price - prev_price) / prev_price) * 100
                            
                            ticker_info = {
                                'symbol': symbol,
                                'price': round(current_price, 2),
                                'change': round(current_price - prev_price, 2),
                                'change_percent': round(change_pct, 2),
                                'volume': int(volume),
                                'data_source': 'yahoo'
                            }
                            
                            movers.append(ticker_info)
                            
                except Exception as e:
                    logger.warning(f"Error processing {symbol}: {e}")
                    continue
            
            # Sort based on mover type
            if mover_type == 'gainers':
                movers.sort(key=lambda x: x['change_percent'], reverse=True)
                return movers[:20]  # Top 20 gainers
            elif mover_type == 'losers':
                movers.sort(key=lambda x: x['change_percent'])
                return movers[:20]  # Top 20 losers
            else:  # active
                movers.sort(key=lambda x: x['volume'], reverse=True)
                return movers[:20]  # Top 20 by volume
                
        except Exception as e:
            logger.error(f"Error getting market movers: {e}")
            return []
    
    def get_quick_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quick quote data for a single symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current data
            current_price = info.get('regularMarketPrice', info.get('price', 0))
            prev_close = info.get('regularMarketPreviousClose', info.get('previousClose', 0))
            
            if current_price and prev_close:
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
            else:
                change = 0
                change_pct = 0
            
            return {
                'symbol': symbol,
                'price': current_price,
                'change': round(change, 2),
                'change_percent': round(change_pct, 2),
                'volume': info.get('regularMarketVolume', info.get('volume', 0)),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE'),
                'name': info.get('longName', symbol),
                'data_source': 'yahoo'
            }
            
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    def scan_for_opportunities(self, scan_type: str = 'momentum') -> List[Dict[str, Any]]:
        """
        Scan for trading opportunities based on criteria
        
        Args:
            scan_type: Type of scan ('momentum', 'oversold', 'breakout', 'volume')
            
        Returns:
            List of opportunities with analysis
        """
        try:
            # Select universe based on scan type
            if scan_type == 'momentum':
                universe = self.universes['momentum_stocks'] + self.universes['mega_cap_tech']
            elif scan_type == 'volume':
                universe = self.universes['high_volume'] + self.universes['popular_retail']
            else:
                universe = self.universes['sp500_leaders']
            
            universe = list(set(universe))[:30]  # Limit to 30 stocks
            
            logger.info(f"Running {scan_type} scan on {len(universe)} stocks")
            
            # Download data for analysis (5 days)
            data = yf.download(
                universe,
                period='5d',
                interval='1d',
                auto_adjust=True,
                threads=True
            )
            
            opportunities = []
            
            for symbol in universe:
                try:
                    opportunity = self._analyze_opportunity(symbol, data, scan_type)
                    if opportunity and opportunity['score'] > 60:
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.warning(f"Error analyzing {symbol}: {e}")
                    continue
            
            # Sort by score
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            return opportunities[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error in opportunity scan: {e}")
            return []
    
    def _analyze_opportunity(self, symbol: str, data: pd.DataFrame, scan_type: str) -> Optional[Dict[str, Any]]:
        """Analyze a single stock for opportunity"""
        try:
            # Extract symbol data
            if symbol in data.columns.levels[0]:
                symbol_data = data[symbol].dropna()
            else:
                symbol_data = data.dropna()
                
            if len(symbol_data) < 2:
                return None
            
            # Calculate basic metrics
            current_price = symbol_data['Close'].iloc[-1]
            prev_price = symbol_data['Close'].iloc[-2]
            avg_volume = symbol_data['Volume'].mean()
            current_volume = symbol_data['Volume'].iloc[-1]
            
            change_pct = ((current_price - prev_price) / prev_price) * 100
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Calculate simple technical indicators
            prices = symbol_data['Close'].values
            sma_5 = prices[-5:].mean() if len(prices) >= 5 else current_price
            
            # Scoring based on scan type
            score = 0
            signals = []
            
            if scan_type == 'momentum':
                if change_pct > 2:
                    score += 40
                    signals.append(f"Strong momentum: +{change_pct:.1f}%")
                if current_price > sma_5:
                    score += 20
                    signals.append("Price above 5-day average")
                if volume_ratio > 1.5:
                    score += 20
                    signals.append(f"High volume: {volume_ratio:.1f}x average")
                    
            elif scan_type == 'volume':
                if volume_ratio > 2:
                    score += 50
                    signals.append(f"Volume spike: {volume_ratio:.1f}x average")
                if change_pct > 0:
                    score += 30
                    signals.append("Positive price action")
                    
            elif scan_type == 'oversold':
                # Simple oversold check
                if change_pct < -3:
                    score += 30
                    signals.append("Potential oversold")
                if current_price < sma_5 * 0.95:
                    score += 30
                    signals.append("Price below 5-day average")
                    
            if score > 0:
                return {
                    'symbol': symbol,
                    'price': round(current_price, 2),
                    'change_percent': round(change_pct, 2),
                    'volume_ratio': round(volume_ratio, 2),
                    'score': score,
                    'signals': signals,
                    'scan_type': scan_type,
                    'data_source': 'yahoo'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            return hist
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return None