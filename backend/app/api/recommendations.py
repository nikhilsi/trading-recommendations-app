# backend/app/api/recommendations.py
"""
Clean, professional API endpoints for recommendations with proper error handling,
validation, and documentation.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List

from schemas.stock import (
    RecommendationRequest, RecommendationResponse, 
    WatchlistRequest, WatchlistResponse, DatabaseStats,
    HistoricalResponse, ErrorResponse, SuccessResponse
)
from services.recommendation_service import RecommendationService
from services.database_service import DatabaseService
import os

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["recommendations"])

# Dependency to get recommendation service
def get_recommendation_service():
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    return RecommendationService(api_key)

# Dependency to get database service
def get_database_service():
    return DatabaseService()

@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    confidence_threshold: int = Query(50, ge=20, le=90, description="Minimum confidence percentage"),
    max_recommendations: int = Query(5, ge=1, le=10, description="Maximum number of recommendations"),
    service = Depends(get_recommendation_service)
):
    """
    Generate trading recommendations based on technical analysis.
    
    - **confidence_threshold**: Minimum confidence level (20-90%)
    - **max_recommendations**: Maximum number of recommendations to return (1-10)
    
    Returns comprehensive trading recommendations with technical analysis,
    target prices, and risk assessments.
    """
    try:
        logger.info(f"Generating recommendations: threshold={confidence_threshold}%, max={max_recommendations}")
        
        result = service.generate_recommendations(
            confidence_threshold=confidence_threshold,
            max_recommendations=max_recommendations
        )
        
        return RecommendationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.get("/recommendations/history", response_model=HistoricalResponse)
async def get_recommendations_history(
    limit: int = Query(50, ge=1, le=100, description="Number of historical recommendations"),
    db_service = Depends(get_database_service)
):
    """
    Get historical recommendations from the database.
    
    - **limit**: Number of recommendations to retrieve (1-100)
    
    Returns historical recommendations with performance tracking.
    """
    try:
        recommendations = db_service.get_recommendations_history(limit)
        
        return HistoricalResponse(
            recommendations=recommendations,
            count=len(recommendations),
            retrieved_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error fetching recommendation history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recommendation history: {str(e)}"
        )

@router.get("/stocks/{symbol}")
async def get_stock_analysis(
    symbol: str,
    service = Depends(get_recommendation_service)
):
    """
    Get detailed analysis for a specific stock symbol.
    
    - **symbol**: Stock symbol (e.g., AAPL, MSFT)
    
    Returns comprehensive technical analysis and recommendation for the specified stock.
    """
    try:
        symbol = symbol.upper().strip()
        
        if not symbol or len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid symbol format")
        
        analysis = service.get_single_stock_analysis(symbol)
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"No analysis available for {symbol}")
        
        if 'error' in analysis:
            raise HTTPException(status_code=400, detail=analysis['error'])
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze {symbol}: {str(e)}"
        )

@router.get("/watchlist", response_model=WatchlistResponse)
async def get_watchlist(
    db_service = Depends(get_database_service)
):
    """
    Get current watchlist symbols.
    
    Returns the list of stock symbols currently being monitored.
    """
    try:
        watchlist = db_service.get_watchlist()
        
        return WatchlistResponse(
            watchlist=watchlist,
            count=len(watchlist)
        )
        
    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch watchlist: {str(e)}"
        )

@router.post("/watchlist", response_model=SuccessResponse)
async def add_to_watchlist(
    item: WatchlistRequest,
    db_service = Depends(get_database_service),
    rec_service = Depends(get_recommendation_service)
):
    """
    Add a stock symbol to the watchlist.
    
    - **symbol**: Stock symbol to add (will be validated)
    
    Validates the symbol exists before adding to watchlist.
    """
    try:
        symbol = item.symbol.upper().strip()
        
        # Validate symbol exists
        if not rec_service.validate_symbol(symbol):
            raise HTTPException(
                status_code=400, 
                detail=f"Symbol {symbol} not found or invalid"
            )
        
        success = db_service.add_to_watchlist(symbol)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add {symbol} to watchlist"
            )
        
        return SuccessResponse(
            message=f"Successfully added {symbol} to watchlist",
            data={"symbol": symbol}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add symbol to watchlist: {str(e)}"
        )

@router.delete("/watchlist/{symbol}", response_model=SuccessResponse)
async def remove_from_watchlist(
    symbol: str,
    db_service = Depends(get_database_service)
):
    """
    Remove a stock symbol from the watchlist.
    
    - **symbol**: Stock symbol to remove
    
    Removes the specified symbol from active monitoring.
    """
    try:
        symbol = symbol.upper().strip()
        
        success = db_service.remove_from_watchlist(symbol)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Symbol {symbol} not found in watchlist"
            )
        
        return SuccessResponse(
            message=f"Successfully removed {symbol} from watchlist",
            data={"symbol": symbol}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove symbol from watchlist: {str(e)}"
        )

@router.get("/stats", response_model=DatabaseStats)
async def get_database_stats(
    db_service = Depends(get_database_service)
):
    """
    Get comprehensive database statistics.
    
    Returns statistics about stored data including recommendations,
    price records, and watchlist information.
    """
    try:
        stats = db_service.get_database_stats()
        
        return DatabaseStats(**stats)
        
    except Exception as e:
        logger.error(f"Error fetching database stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch database statistics: {str(e)}"
        )