# backend/app/api/watchlist.py
"""
Watchlist management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from schemas.stock import WatchlistRequest, WatchlistResponse, SuccessResponse
from services.database_service import DatabaseService
from services.recommendation_service import RecommendationService
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["watchlist"])

def get_db_service():
    return DatabaseService()

def get_recommendation_service():
    if not settings.ALPHA_VANTAGE_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    return RecommendationService(settings.ALPHA_VANTAGE_API_KEY)

@router.get("/watchlist", response_model=WatchlistResponse)
async def get_watchlist(db_service = Depends(get_db_service)):
    """Get current watchlist symbols"""
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
    db_service = Depends(get_db_service),
    rec_service = Depends(get_recommendation_service)
):
    """Add a stock symbol to the watchlist"""
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
    db_service = Depends(get_db_service)
):
    """Remove a stock symbol from the watchlist"""
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