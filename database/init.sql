-- database/init.sql
-- This script runs when the database container starts for the first time

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create stocks table
CREATE TABLE IF NOT EXISTS stocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create stock_prices table for historical data
CREATE TABLE IF NOT EXISTS stock_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    volume BIGINT,
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    open_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);

-- Create recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('BUY', 'SELL', 'HOLD')),
    current_price DECIMAL(10,2) NOT NULL,
    target_price DECIMAL(10,2) NOT NULL,
    stop_loss DECIMAL(10,2),
    confidence INTEGER CHECK (confidence >= 0 AND confidence <= 100),
    reasoning TEXT,
    timeframe VARCHAR(50),
    risk_level VARCHAR(20),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create technical_indicators table
CREATE TABLE IF NOT EXISTS technical_indicators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    rsi DECIMAL(5,2),
    macd DECIMAL(10,4),
    macd_signal DECIMAL(10,4),
    sma_20 DECIMAL(10,2),
    sma_50 DECIMAL(10,2),
    volume_avg BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON stock_prices(symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_symbol ON recommendations(symbol);
CREATE INDEX IF NOT EXISTS idx_recommendations_generated_at ON recommendations(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_technical_indicators_symbol_date ON technical_indicators(symbol, date DESC);

-- Insert some sample stocks
INSERT INTO stocks (symbol, company_name, sector, market_cap) VALUES
    ('AAPL', 'Apple Inc', 'Technology', 3000000000000),
    ('MSFT', 'Microsoft Corporation', 'Technology', 2800000000000),
    ('GOOGL', 'Alphabet Inc', 'Technology', 1700000000000),
    ('TSLA', 'Tesla Inc', 'Automotive', 800000000000),
    ('NVDA', 'NVIDIA Corporation', 'Technology', 1800000000000),
    ('AMD', 'Advanced Micro Devices', 'Technology', 240000000000),
    ('META', 'Meta Platforms Inc', 'Technology', 800000000000),
    ('NFLX', 'Netflix Inc', 'Media', 180000000000)
ON CONFLICT (symbol) DO NOTHING;

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully!';
END $$;