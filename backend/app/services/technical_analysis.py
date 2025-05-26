# backend/app/services/technical_analysis.py
"""
Professional technical analysis service with proper error handling and logging.
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TechnicalSignal:
    """Data class for technical analysis signals"""
    signal: str  # BUY, SELL, HOLD
    confidence: int  # 0-100
    reasoning: List[str]
    indicators: Dict[str, float]

class TechnicalAnalysisService:
    """
    Professional technical analysis service with comprehensive indicators
    and signal generation logic.
    """
    
    def __init__(self):
        self.min_data_points = 20
        self.rsi_period = 14
        self.sma_short_period = 10
        self.sma_long_period = 20
    
    def calculate_rsi(self, prices: List[float], period: int = None) -> float:
        """
        Calculate Relative Strength Index
        
        Args:
            prices: List of closing prices (oldest first)
            period: RSI calculation period (default: 14)
            
        Returns:
            RSI value between 0-100, or 50 if insufficient data
        """
        if period is None:
            period = self.rsi_period
            
        if len(prices) < period + 1:
            logger.warning(f"Insufficient data for RSI calculation: {len(prices)} < {period + 1}")
            return 50.0
        
        try:
            # Calculate price changes
            price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            
            # Get recent changes for RSI calculation
            recent_changes = price_changes[-period:]
            
            # Separate gains and losses
            gains = [change if change > 0 else 0 for change in recent_changes]
            losses = [-change if change < 0 else 0 for change in recent_changes]
            
            # Calculate average gain and loss
            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period
            
            # Calculate RSI
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return round(rsi, 2)
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 50.0
    
    def calculate_sma(self, prices: List[float], period: int) -> float:
        """
        Calculate Simple Moving Average
        
        Args:
            prices: List of closing prices (oldest first)
            period: SMA calculation period
            
        Returns:
            SMA value or last price if insufficient data
        """
        if len(prices) < period:
            logger.warning(f"Insufficient data for SMA calculation: {len(prices)} < {period}")
            return prices[-1] if prices else 0.0
        
        try:
            return round(sum(prices[-period:]) / period, 2)
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return prices[-1] if prices else 0.0
    
    def calculate_momentum(self, prices: List[float], period: int = 5) -> float:
        """
        Calculate price momentum over specified period
        
        Args:
            prices: List of closing prices (oldest first)
            period: Period for momentum calculation
            
        Returns:
            Momentum percentage change
        """
        if len(prices) < period:
            return 0.0
        
        try:
            current_price = prices[-1]
            past_price = prices[-period]
            momentum = ((current_price - past_price) / past_price) * 100
            return round(momentum, 2)
        except Exception as e:
            logger.error(f"Error calculating momentum: {e}")
            return 0.0
    
    def calculate_volatility(self, prices: List[float], period: int = 20) -> float:
        """
        Calculate price volatility (standard deviation)
        
        Args:
            prices: List of closing prices (oldest first)
            period: Period for volatility calculation
            
        Returns:
            Volatility as percentage
        """
        if len(prices) < period:
            return 0.0
        
        try:
            recent_prices = prices[-period:]
            mean_price = sum(recent_prices) / len(recent_prices)
            
            # Calculate standard deviation
            variance = sum((price - mean_price) ** 2 for price in recent_prices) / len(recent_prices)
            std_dev = variance ** 0.5
            
            # Return as percentage of mean price
            volatility = (std_dev / mean_price) * 100
            return round(volatility, 2)
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.0
    
    def analyze_volume_trend(self, volumes: List[int], period: int = 10) -> Dict[str, Any]:
        """
        Analyze volume trends
        
        Args:
            volumes: List of trading volumes (oldest first)
            period: Period for volume analysis
            
        Returns:
            Dictionary with volume analysis results
        """
        if not volumes or len(volumes) < period:
            return {
                'trend': 'NEUTRAL',
                'ratio': 1.0,
                'strength': 'NORMAL'
            }
        
        try:
            current_volume = volumes[-1]
            avg_volume = sum(volumes[-period:]) / len(volumes[-period:])
            
            ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            if ratio > 1.5:
                trend = 'HIGH'
                strength = 'STRONG'
            elif ratio > 1.2:
                trend = 'ABOVE_AVERAGE'
                strength = 'MEDIUM'
            elif ratio < 0.7:
                trend = 'LOW'
                strength = 'WEAK'
            else:
                trend = 'NORMAL'
                strength = 'NORMAL'
            
            return {
                'trend': trend,
                'ratio': round(ratio, 2),
                'strength': strength,
                'current_volume': current_volume,
                'avg_volume': int(avg_volume)
            }
        except Exception as e:
            logger.error(f"Error analyzing volume trend: {e}")
            return {'trend': 'NEUTRAL', 'ratio': 1.0, 'strength': 'NORMAL'}
    
    def generate_signal(self, prices: List[float], volumes: List[int] = None) -> TechnicalSignal:
        """
        Generate comprehensive trading signal based on multiple indicators
        
        Args:
            prices: List of closing prices (oldest first)
            volumes: List of trading volumes (oldest first)
            
        Returns:
            TechnicalSignal object with signal, confidence, and reasoning
        """
        if len(prices) < self.min_data_points:
            return TechnicalSignal(
                signal='HOLD',
                confidence=0,
                reasoning=['Insufficient data for analysis'],
                indicators={}
            )
        
        try:
            # Calculate technical indicators
            current_price = prices[-1]
            rsi = self.calculate_rsi(prices)
            sma_short = self.calculate_sma(prices, self.sma_short_period)
            sma_long = self.calculate_sma(prices, self.sma_long_period)
            momentum_5d = self.calculate_momentum(prices, 5)
            volatility = self.calculate_volatility(prices)
            
            # Volume analysis
            volume_analysis = self.analyze_volume_trend(volumes) if volumes else None
            
            # Signal scoring system
            bullish_signals = 0
            bearish_signals = 0
            reasoning = []
            
            # RSI Analysis
            if rsi < 30:
                bullish_signals += 2
                reasoning.append(f"RSI oversold at {rsi:.1f}")
            elif rsi > 70:
                bearish_signals += 2
                reasoning.append(f"RSI overbought at {rsi:.1f}")
            elif 45 <= rsi <= 55:
                reasoning.append(f"RSI neutral at {rsi:.1f}")
            
            # Moving Average Analysis
            if current_price > sma_short > sma_long:
                bullish_signals += 2
                reasoning.append("Price above both short and long-term moving averages")
            elif current_price < sma_short < sma_long:
                bearish_signals += 2
                reasoning.append("Price below both short and long-term moving averages")
            elif current_price > sma_short:
                bullish_signals += 1
                reasoning.append("Price above short-term moving average")
            
            # Momentum Analysis
            if momentum_5d > 3:
                bullish_signals += 1
                reasoning.append(f"Strong positive momentum (+{momentum_5d:.1f}%)")
            elif momentum_5d < -3:
                bearish_signals += 1
                reasoning.append(f"Strong negative momentum ({momentum_5d:.1f}%)")
            
            # Volume Analysis
            if volume_analysis:
                if volume_analysis['trend'] in ['HIGH', 'ABOVE_AVERAGE']:
                    reasoning.append(f"Volume {volume_analysis['ratio']:.1f}x average supports signal")
                    # Amplify existing signals
                    if bullish_signals > bearish_signals:
                        bullish_signals += 1
                    elif bearish_signals > bullish_signals:
                        bearish_signals += 1
                elif volume_analysis['trend'] == 'LOW':
                    reasoning.append("Low volume - signal may lack conviction")
            
            # Volatility consideration
            if volatility > 5:
                reasoning.append(f"High volatility ({volatility:.1f}%) - increased risk")
            
            # Determine final signal
            signal_strength = abs(bullish_signals - bearish_signals)
            
            if bullish_signals > bearish_signals and signal_strength >= 2:
                signal = 'BUY'
                confidence = min(50 + (signal_strength * 10), 95)
            elif bearish_signals > bullish_signals and signal_strength >= 2:
                signal = 'SELL'
                confidence = min(50 + (signal_strength * 10), 95)
            else:
                signal = 'HOLD'
                confidence = 30
                reasoning.append("Mixed signals or insufficient conviction")
            
            # Compile indicators
            indicators = {
                'rsi': rsi,
                'sma_short': sma_short,
                'sma_long': sma_long,
                'momentum_5d': momentum_5d,
                'volatility': volatility,
                'current_price': current_price
            }
            
            if volume_analysis:
                indicators['volume_ratio'] = volume_analysis['ratio']
            
            return TechnicalSignal(
                signal=signal,
                confidence=confidence,
                reasoning=reasoning,
                indicators=indicators
            )
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return TechnicalSignal(
                signal='HOLD',
                confidence=0,
                reasoning=[f'Analysis error: {str(e)}'],
                indicators={}
            )
    
    def validate_data(self, prices: List[float], volumes: List[int] = None) -> bool:
        """
        Validate input data quality
        
        Args:
            prices: List of closing prices
            volumes: List of trading volumes
            
        Returns:
            True if data is valid for analysis
        """
        if not prices or len(prices) < self.min_data_points:
            logger.warning(f"Insufficient price data: {len(prices) if prices else 0}")
            return False
        
        # Check for valid price data
        if any(price <= 0 for price in prices):
            logger.warning("Invalid price data found (zero or negative values)")
            return False
        
        # Check for volume data if provided
        if volumes and any(vol < 0 for vol in volumes):
            logger.warning("Invalid volume data found (negative values)")
            return False
        
        return True