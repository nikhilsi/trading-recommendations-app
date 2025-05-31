# backend/app/api/watchlist_auth.py
"""
Updated watchlist endpoints with user authentication
Replace the existing watchlist.py with this file
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import Optional

from schemas.stock import WatchlistRequest, WatchlistResponse, SuccessResponse
from services.database_service import DatabaseService
from services.recommendation_service import RecommendationService
from core.config import settings
from core.dependencies import get_current_user, get_current_user_optional
from models.auth import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["watchlist"])

def get_db_service():
    return DatabaseService()

def get_recommendation_service():
    if not settings.ALPHA_VANTAGE_API_KEY and not settings.POLYGON_API_KEY:
        raise HTTPException(status_code=500, detail="No API keys configured")
    
    if settings.POLYGON_API_KEY:
        from services.enhanced_recommendation_service import EnhancedRecommendationService
        return EnhancedRecommendationService(settings.POLYGON_API_KEY)
    else:
        return RecommendationService(settings.ALPHA_VANTAGE_API_KEY)

@router.get("/watchlist", response_model=WatchlistResponse)
async def get_watchlist(
    db_service = Depends(get_db_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get current user's watchlist
    Works with or without authentication during transition
    """
    try:
        if current_user:
            # Get user-specific watchlist
            watchlist = db_service.get_user_watchlist(current_user.id)
        else:
            # Legacy: Get global watchlist (for transition period)
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
    rec_service = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)  # Now required
):
    """
    Add a stock symbol to user's watchlist
    Requires authentication
    """
    try:
        symbol = item.symbol.upper().strip()
        
        # Validate symbol exists
        # if not rec_service.validate_symbol(symbol):
        #     raise HTTPException(
        #         status_code=400, 
        #         detail=f"Symbol {symbol} not found or invalid"
            # )
        
        # Check user's watchlist limit
        current_watchlist = db_service.get_user_watchlist(current_user.id)
        watchlist_limit = 20  # Default for free tier
        
        if current_user.tier and current_user.tier.features:
            watchlist_limit = current_user.tier.features.get('watchlist_size', 20)
        
        if len(current_watchlist) >= watchlist_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Watchlist limit reached ({watchlist_limit} stocks). Upgrade to add more."
            )
        
        success = db_service.add_to_user_watchlist(current_user.id, symbol)
        
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
    db_service = Depends(get_db_service),
    current_user: User = Depends(get_current_user)  # Now required
):
    """
    Remove a stock symbol from user's watchlist
    Requires authentication
    """
    try:
        symbol = symbol.upper().strip()
        
        success = db_service.remove_from_user_watchlist(current_user.id, symbol)
        
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