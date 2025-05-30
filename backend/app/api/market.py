# backend/app/api/market.py
"""
Market scanner endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import logging

from services.yahoo_data_service import YahooDataService
from services.polygon_service import PolygonService
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/market", tags=["market"])

@router.get("/scan")
async def scan_market(
    scan_type: str = Query("momentum", description="Type of scan: momentum, volume, oversold, most_active"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    source: str = Query("polygon", description="Data source: polygon or yahoo"),
    min_price: float = Query(0, ge=0, description="Minimum stock price"),
    max_price: float = Query(0, ge=0, description="Maximum stock price (0 = no limit)"),
    min_volume: int = Query(0, ge=0, description="Minimum trading volume"),
    min_score: int = Query(30, ge=0, le=100, description="Minimum opportunity score")
):
    """
    Scan market for trading opportunities
    
    - **scan_type**: Type of scan to perform
    - **limit**: Maximum number of results
    - **source**: Data provider to use
    - **min_price**: Filter by minimum price
    - **max_price**: Filter by maximum price
    - **min_volume**: Filter by minimum volume
    - **min_score**: Filter by minimum score
    """
    try:
        opportunities = []
        market_stats = {}
        
        if source == "polygon" and settings.POLYGON_API_KEY:
            polygon = PolygonService()
            market_data = polygon.get_market_movers()
            
            # Process based on scan type
            if scan_type == "momentum":
                raw_opportunities = market_data['gainers']
            elif scan_type == "volume":
                raw_opportunities = market_data['volume_movers']
            elif scan_type == "oversold":
                raw_opportunities = market_data['losers']
            elif scan_type == "most_active":
                raw_opportunities = market_data['most_active']
            else:
                raw_opportunities = market_data['gainers']
            
            # Convert to opportunity format
            for stock in raw_opportunities:
                score = calculate_opportunity_score(stock, scan_type)
                opportunities.append({
                    'symbol': stock['symbol'],
                    'price': stock['price'],
                    'change_percent': stock['change_percent'],
                    'volume': stock['volume'],
                    'score': score,
                    'signals': generate_signals(stock, scan_type),
                    'scan_type': scan_type,
                    'data_source': 'polygon'
                })
            
            market_stats = {
                "total_symbols_scanned": market_data.get('total_symbols', 0),
                "data_freshness": market_data.get('timestamp')
            }
        else:
            # Fallback to Yahoo
            yahoo = YahooDataService()
            opportunities = yahoo.scan_for_opportunities(scan_type)
        
        # Apply filters
        filtered_opportunities = apply_filters(
            opportunities, 
            min_price, 
            max_price, 
            min_volume, 
            min_score
        )
        
        return {
            "opportunities": filtered_opportunities[:limit],
            "scan_type": scan_type,
            "source": source,
            "market_stats": {
                "total_symbols_scanned": market_stats.get("total_symbols_scanned", 0),
                "pre_filter_count": len(opportunities),
                "post_filter_count": len(filtered_opportunities),
                "filters_applied": {
                    "min_price": min_price,
                    "max_price": max_price,
                    "min_volume": min_volume,
                    "min_score": min_score
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market scan error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Market scan failed: {str(e)}"
        )

def calculate_opportunity_score(stock: dict, scan_type: str) -> int:
    """Calculate opportunity score based on scan type"""
    if scan_type == "momentum":
        return min(95, int(50 + stock['change_percent'] * 5))
    elif scan_type == "volume":
        return min(90, int(60 + abs(stock['change_percent']) * 3))
    elif scan_type == "oversold":
        return min(80, int(40 + abs(stock['change_percent']) * 4))
    else:
        return 70

def generate_signals(stock: dict, scan_type: str) -> list:
    """Generate trading signals based on stock data"""
    signals = []
    
    if scan_type == "momentum" and stock['change_percent'] > 0:
        signals.append(f"Strong momentum: +{stock['change_percent']:.1f}%")
        signals.append(f"Volume: {stock['volume']:,}")
        if stock['change_percent'] > 5:
            signals.append("Top market gainer")
            
    elif scan_type == "volume":
        signals.append(f"High volume: {stock['volume']:,}")
        signals.append(f"Price movement: {stock['change_percent']:+.1f}%")
        signals.append("Unusual activity detected")
        
    elif scan_type == "oversold" and stock['change_percent'] < 0:
        signals.append(f"Oversold: {stock['change_percent']:.1f}%")
        signals.append("Potential bounce candidate")
        
    elif scan_type == "most_active":
        signals.append(f"Most traded: {stock['volume']:,} shares")
        signals.append(f"Price change: {stock['change_percent']:+.1f}%")
        signals.append("High market interest")
    
    return signals

def apply_filters(opportunities: list, min_price: float, max_price: float, 
                  min_volume: int, min_score: int) -> list:
    """Apply filters to opportunities"""
    filtered = []
    
    for opp in opportunities:
        # Price filter
        if min_price > 0 and opp.get('price', 0) < min_price:
            continue
        if max_price > 0 and opp.get('price', 0) > max_price:
            continue
            
        # Volume filter
        if min_volume > 0 and opp.get('volume', 0) < min_volume:
            continue
            
        # Score filter
        if opp.get('score', 0) < min_score:
            continue
            
        filtered.append(opp)
    
    return filtered