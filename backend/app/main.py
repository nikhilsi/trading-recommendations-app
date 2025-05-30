# backend/app/main.py
"""
Professional FastAPI application with clean modular architecture
"""
import logging
import sys
from contextlib import asynccontextmanager

# Add the app directory to Python path
sys.path.insert(0, '/app/app')

from fastapi import FastAPI, HTTPException

# Core imports
from core.config import settings
from core.middleware import setup_cors
from core.exceptions import http_exception_handler, global_exception_handler

# API routers
from api.health import router as health_router
from api.market import router as market_router
from api.watchlist import router as watchlist_router
from api.recommendations import router as recommendations_router

# Services
from services.database_service import DatabaseService
from models.database import create_tables

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.API_TITLE}...")
    
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created/verified")
        
        # Initialize database service
        db_service = DatabaseService()
        if db_service.test_connection():
            logger.info("Database connection successful")
            db_service.initialize_default_watchlist()
        else:
            logger.error("Database connection failed")
        
        # Log API key status
        if settings.ALPHA_VANTAGE_API_KEY:
            logger.info("Alpha Vantage API key configured")
        else:
            logger.warning("Alpha Vantage API key not configured")
            
        if settings.POLYGON_API_KEY:
            logger.info("Polygon API key configured")
        else:
            logger.warning("Polygon API key not configured")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Setup middleware
setup_cors(app)

# Include routers
app.include_router(health_router)
app.include_router(market_router)
app.include_router(watchlist_router)
app.include_router(recommendations_router)

# Register exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )