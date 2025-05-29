# backend/app/main.py
"""
Professional FastAPI application with clean architecture,
proper error handling, logging, and modular design.
"""
import logging
import os
import sys
from datetime import datetime
from contextlib import asynccontextmanager

# Add the app directory to Python path
sys.path.insert(0, '/app/app')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import API routers with try/catch for graceful fallback
try:
    from api.recommendations import router as recommendations_router
    MODULAR_IMPORTS = True
except ImportError as e:
    print(f"Warning: Could not import modular API router: {e}")
    MODULAR_IMPORTS = False

# Import services for initialization with fallbacks
try:
    from services.database_service import DatabaseService
    from models.database import create_tables
except ImportError as e:
    print(f"Warning: Could not import modular services: {e}")
    DatabaseService = None
    create_tables = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Changed from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Also set specific loggers to DEBUG
logging.getLogger("app").setLevel(logging.INFO)
logging.getLogger("services").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Trading Recommendations API...")
    
    try:
        # Create database tables if modular imports work
        if create_tables:
            create_tables()
            logger.info("Database tables created/verified")
        else:
            logger.warning("Modular database service not available")
        
        # Initialize database service if available
        if DatabaseService:
            db_service = DatabaseService()
            
            # Test database connection
            if db_service.test_connection():
                logger.info("Database connection successful")
                
                # Initialize default watchlist if needed
                db_service.initialize_default_watchlist()
            else:
                logger.error("Database connection failed")
        
        # Verify API key
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if api_key:
            logger.info(f"Alpha Vantage API key configured: {api_key[:8]}...")
        else:
            logger.warning("Alpha Vantage API key not configured")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Don't raise - allow app to start even with issues
    
    yield
    
    # Shutdown
    logger.info("Shutting down Trading Recommendations API...")

# Create FastAPI application with lifespan
app = FastAPI(
    title="Trading Recommendations API",
    description="""
    Professional stock trading recommendations API with real-time market data analysis,
    technical indicators, and comprehensive database persistence.
    
    ## Features
    * Real-time stock analysis using Alpha Vantage data
    * Technical analysis with RSI, moving averages, and momentum indicators
    * Customizable confidence thresholds and recommendation limits
    * Persistent watchlist management
    * Historical recommendation tracking
    * Comprehensive database statistics
    
    ## Usage
    1. Configure your Alpha Vantage API key
    2. Manage your watchlist of stocks to monitor
    3. Generate recommendations with custom parameters
    4. Track historical performance and database statistics
    """,
    version="2.0.0",
    contact={
        "name": "Trading App Developer",
        "email": "developer@tradingapp.com"
    },
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://frontend:3000",   # Docker frontend service
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routers if available
if MODULAR_IMPORTS and 'recommendations_router' in locals():
    app.include_router(recommendations_router)
    logger.info("Modular API router included successfully")
else:
    logger.warning("Using fallback API endpoints")
    
    # Fallback to simplified endpoints
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from pydantic import BaseModel
    import requests
    import time
    import json
    
    class WatchlistItem(BaseModel):
        symbol: str
    
    def get_db_connection():
        try:
            conn = psycopg2.connect(
                host="postgres",
                port="5432",
                database="trading_app",
                user="trading_user",
                password="trading_password123"
            )
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    @app.get("/api/watchlist")
    async def get_watchlist():
        """Fallback watchlist endpoint"""
        conn = get_db_connection()
        if not conn:
            return {"watchlist": ['AAPL', 'MSFT', 'GOOGL', 'TSLA']}
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT symbol FROM watchlist WHERE is_active = TRUE ORDER BY symbol;")
                results = cursor.fetchall()
                symbols = [row['symbol'] for row in results]
                return {"watchlist": symbols, "count": len(symbols)}
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
            return {"watchlist": []}
        finally:
            conn.close()
    
    @app.post("/api/watchlist")
    async def add_to_watchlist(item: WatchlistItem):
        """Fallback add to watchlist"""
        symbol = item.symbol.upper().strip()
        
        if not symbol or len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid symbol")
        
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO watchlist (symbol) VALUES (%s) 
                    ON CONFLICT (symbol) DO UPDATE SET is_active = TRUE, added_at = CURRENT_TIMESTAMP;
                """, (symbol,))
                conn.commit()
                return {"message": f"Added {symbol} to watchlist", "symbol": symbol}
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            raise HTTPException(status_code=500, detail="Failed to add symbol")
        finally:
            conn.close()
    
    @app.delete("/api/watchlist/{symbol}")
    async def remove_from_watchlist(symbol: str):
        """Fallback remove from watchlist"""
        symbol = symbol.upper()
        
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE watchlist SET is_active = FALSE WHERE symbol = %s;", (symbol,))
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Symbol not found in watchlist")
                conn.commit()
                return {"message": f"Removed {symbol} from watchlist"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            raise HTTPException(status_code=500, detail="Failed to remove symbol")
        finally:
            conn.close()
    
    @app.get("/api/stats")
    async def get_database_stats():
        """Fallback database stats"""
        conn = get_db_connection()
        if not conn:
            return {"error": "Database not available"}
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM stocks;")
                total_stocks = cursor.fetchone()['count'] if cursor.rowcount > 0 else 0
                
                cursor.execute("SELECT COUNT(*) as count FROM recommendations;")
                total_recommendations = cursor.fetchone()['count'] if cursor.rowcount > 0 else 0
                
                cursor.execute("SELECT COUNT(*) as count FROM stock_prices;")
                total_prices = cursor.fetchone()['count'] if cursor.rowcount > 0 else 0
                
                cursor.execute("SELECT COUNT(*) as count FROM watchlist WHERE is_active = TRUE;")
                watchlist_size = cursor.fetchone()['count'] if cursor.rowcount > 0 else 0
                
                return {
                    "total_stocks": total_stocks,
                    "total_recommendations": total_recommendations,
                    "total_prices": total_prices,
                    "watchlist_size": watchlist_size,
                    "last_updated": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": "Failed to get statistics"}
        finally:
            conn.close()
    
    @app.get("/api/recommendations")
    async def get_recommendations(
        confidence_threshold: int = 50,
        max_recommendations: int = 5
    ):
        """Fallback recommendations endpoint"""
        return {
            "recommendations": [],
            "generated_at": datetime.utcnow().isoformat(),
            "message": "Modular recommendation service not available, using fallback",
            "parameters": {
                "confidence_threshold": confidence_threshold,
                "max_recommendations": max_recommendations
            }
        }

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing API information and health status
    """
    return {
        "name": "Trading Recommendations API",
        "version": "2.0.0",
        "description": "Professional stock trading recommendations with technical analysis",
        "features": [
            "Real-time market data analysis",
            "Technical indicators (RSI, SMA, momentum)",
            "Customizable confidence thresholds",
            "Watchlist management",
            "Historical tracking",
            "Database persistence"
        ],
        "status": "operational",
        "modular_services": MODULAR_IMPORTS,
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": "/docs",
        "api_endpoints": {
            "recommendations": "/api/recommendations",
            "watchlist": "/api/watchlist",
            "stats": "/api/stats"
        }
    }

# Health check endpoint
@app.get("/health", tags=["monitoring"])
async def health_check():
    """
    Comprehensive health check endpoint for monitoring and diagnostics
    """
    try:
        # Test database connection
        if DatabaseService:
            db_service = DatabaseService()
            db_healthy = db_service.test_connection()
        else:
            # Fallback database test
            conn = get_db_connection() if 'get_db_connection' in locals() else None
            db_healthy = conn is not None
            if conn:
                conn.close()
        
        # Check API key configuration
        api_key_configured = bool(os.getenv('ALPHA_VANTAGE_API_KEY'))
        
        # Overall health status
        healthy = db_healthy and api_key_configured
        
        return {
            "status": "healthy" if healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "api_key": "configured" if api_key_configured else "missing",
                "modular_services": "available" if MODULAR_IMPORTS else "fallback_mode",
                "services": "operational"
            },
            "uptime": "Available",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

# Market scanner endpoint
@app.get("/api/market/scan", tags=["market"])
async def scan_market(
    scan_type: str = "momentum",
    limit: int = 10
):
    """Scan market for opportunities using Yahoo Finance"""
    try:
        from services.yahoo_data_service import YahooDataService
        yahoo = YahooDataService()
        
        opportunities = yahoo.scan_for_opportunities(scan_type)
        
        return {
            "opportunities": opportunities[:limit],
            "scan_type": scan_type,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "yahoo"
        }
    except Exception as e:
        logger.error(f"Market scan error: {e}")
        return {
            "opportunities": [],
            "error": str(e)
        }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom HTTP exception handler with consistent error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )