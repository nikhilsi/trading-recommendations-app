# backend/app/models/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, Date, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://trading_user:trading_password123@postgres:5432/trading_app'
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100))
    market_cap = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StockPrice(Base):
    __tablename__ = "stock_prices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(BigInteger)
    high = Column(Float)
    low = Column(Float)
    open_price = Column(Float)
    close_price = Column(Float)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False, index=True)
    action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    current_price = Column(Float, nullable=False)
    target_price = Column(Float)
    stop_loss = Column(Float)
    confidence = Column(Integer)
    reasoning = Column(Text)  # JSON string
    timeframe = Column(String(50))
    risk_level = Column(String(20))
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False)
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    volume_avg = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), unique=False, nullable=False)  # Changed to non-unique
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  
    added_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Database utility functions
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db_connection():
    """Get raw database connection for direct SQL queries"""
    return engine.connect()

if __name__ == "__main__":
    # Create tables if run directly
    create_tables()
    print("Database tables created successfully!")