# backend/app/api/health.py
"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
import os
import logging

from services.database_service import DatabaseService
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["monitoring"])

@router.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": "Professional stock trading recommendations with technical analysis",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": "/docs",
        "api_endpoints": {
            "market_scanner": "/api/market/scan",
            "recommendations": "/api/recommendations",
            "watchlist": "/api/watchlist",
            "stats": "/api/stats"
        }
    }

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test database connection
        db_service = DatabaseService()
        db_healthy = db_service.test_connection()
        
        # Check API key configuration
        api_key_configured = bool(settings.ALPHA_VANTAGE_API_KEY)
        polygon_configured = bool(settings.POLYGON_API_KEY)
        
        # Overall health status
        healthy = db_healthy
        
        return {
            "status": "healthy" if healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.API_VERSION,
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "alpha_vantage_api": "configured" if api_key_configured else "not configured",
                "polygon_api": "configured" if polygon_configured else "not configured",
            },
            "environment": settings.ENVIRONMENT
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }