-- ======================================================================================
-- IQ Option Trading Bot Database Initialization
-- ======================================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS logs;

-- ======================================================================================
-- Trading Tables
-- ======================================================================================

-- Trades table
CREATE TABLE IF NOT EXISTS trading.trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trade_id VARCHAR(255) UNIQUE NOT NULL,
    asset VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('call', 'put')),
    amount DECIMAL(10,2) NOT NULL,
    duration INTEGER NOT NULL,
    entry_price DECIMAL(15,8),
    exit_price DECIMAL(15,8),
    profit DECIMAL(10,2),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    strategy VARCHAR(100),
    confidence DECIMAL(3,2),
    risk_level DECIMAL(3,2)
);

-- Create indexes for trades
CREATE INDEX IF NOT EXISTS idx_trades_asset ON trading.trades(asset);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trading.trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_created_at ON trading.trades(created_at);
CREATE INDEX IF NOT EXISTS idx_trades_trade_id ON trading.trades(trade_id);

-- Trading sessions table
CREATE TABLE IF NOT EXISTS trading.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_date DATE NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_profit DECIMAL(10,2) DEFAULT 0,
    max_drawdown DECIMAL(10,2) DEFAULT 0,
    
    -- Configuration snapshot
    config JSONB,
    
    CONSTRAINT unique_session_date UNIQUE(session_date)
);

-- Market data table for caching
CREATE TABLE IF NOT EXISTS trading.market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open_price DECIMAL(15,8) NOT NULL,
    high_price DECIMAL(15,8) NOT NULL,
    low_price DECIMAL(15,8) NOT NULL,
    close_price DECIMAL(15,8) NOT NULL,
    volume DECIMAL(20,2) DEFAULT 0,
    
    CONSTRAINT unique_market_data UNIQUE(asset, timeframe, timestamp)
);

-- Create indexes for market data
CREATE INDEX IF NOT EXISTS idx_market_data_asset_timeframe ON trading.market_data(asset, timeframe);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON trading.market_data(timestamp);

-- ======================================================================================
-- Analytics Tables
-- ======================================================================================

-- Performance analytics
CREATE TABLE IF NOT EXISTS analytics.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0,
    profit_factor DECIMAL(5,2) DEFAULT 0,
    max_consecutive_wins INTEGER DEFAULT 0,
    max_consecutive_losses INTEGER DEFAULT 0,
    average_win DECIMAL(10,2) DEFAULT 0,
    average_loss DECIMAL(10,2) DEFAULT 0,
    
    -- Risk metrics
    sharpe_ratio DECIMAL(5,2) DEFAULT 0,
    max_drawdown DECIMAL(10,2) DEFAULT 0,
    
    -- Asset breakdown
    asset_performance JSONB,
    
    CONSTRAINT unique_performance_date UNIQUE(date)
);

-- Indicator calculations cache
CREATE TABLE IF NOT EXISTS analytics.indicators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    values JSONB NOT NULL,
    
    CONSTRAINT unique_indicator UNIQUE(asset, timeframe, indicator_name, timestamp)
);

-- Create indexes for indicators
CREATE INDEX IF NOT EXISTS idx_indicators_asset_timeframe ON analytics.indicators(asset, timeframe);
CREATE INDEX IF NOT EXISTS idx_indicators_name ON analytics.indicators(indicator_name);
CREATE INDEX IF NOT EXISTS idx_indicators_timestamp ON analytics.indicators(timestamp);

-- ======================================================================================
-- Logging Tables  
-- ======================================================================================

-- Trading signals log
CREATE TABLE IF NOT EXISTS logs.trading_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    asset VARCHAR(50) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    direction VARCHAR(10),
    confidence DECIMAL(3,2),
    reason TEXT,
    indicators JSONB,
    market_data JSONB
);

-- Create indexes for signals
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON logs.trading_signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_signals_asset ON logs.trading_signals(asset);
CREATE INDEX IF NOT EXISTS idx_signals_type ON logs.trading_signals(signal_type);

-- System logs
CREATE TABLE IF NOT EXISTS logs.system_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    level VARCHAR(20) NOT NULL,
    component VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB
);

-- Create indexes for system events
CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON logs.system_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_events_level ON logs.system_events(level);
CREATE INDEX IF NOT EXISTS idx_system_events_component ON logs.system_events(component);

-- ======================================================================================
-- Views
-- ======================================================================================

-- Daily trading summary view
CREATE OR REPLACE VIEW analytics.daily_summary AS
SELECT 
    DATE(created_at) as trade_date,
    COUNT(*) as total_trades,
    COUNT(*) FILTER (WHERE profit > 0) as winning_trades,
    COUNT(*) FILTER (WHERE profit <= 0) as losing_trades,
    ROUND(COUNT(*) FILTER (WHERE profit > 0) * 100.0 / COUNT(*), 2) as win_rate,
    ROUND(SUM(profit), 2) as total_profit,
    ROUND(AVG(profit), 2) as avg_profit,
    ROUND(MAX(profit), 2) as max_win,
    ROUND(MIN(profit), 2) as max_loss
FROM trading.trades 
WHERE status = 'closed'
GROUP BY DATE(created_at)
ORDER BY trade_date DESC;

-- Asset performance view
CREATE OR REPLACE VIEW analytics.asset_performance AS
SELECT 
    asset,
    COUNT(*) as total_trades,
    COUNT(*) FILTER (WHERE profit > 0) as winning_trades,
    ROUND(COUNT(*) FILTER (WHERE profit > 0) * 100.0 / COUNT(*), 2) as win_rate,
    ROUND(SUM(profit), 2) as total_profit,
    ROUND(AVG(profit), 2) as avg_profit
FROM trading.trades 
WHERE status = 'closed'
GROUP BY asset
ORDER BY total_profit DESC;

-- ======================================================================================
-- Functions
-- ======================================================================================

-- Function to calculate win rate
CREATE OR REPLACE FUNCTION calculate_win_rate(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date DATE DEFAULT CURRENT_DATE
)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    win_rate DECIMAL(5,2);
BEGIN
    SELECT 
        ROUND(COUNT(*) FILTER (WHERE profit > 0) * 100.0 / COUNT(*), 2)
    INTO win_rate
    FROM trading.trades 
    WHERE status = 'closed'
      AND DATE(created_at) BETWEEN start_date AND end_date;
    
    RETURN COALESCE(win_rate, 0);
END;
$$ LANGUAGE plpgsql;

-- ======================================================================================
-- Initial Data
-- ======================================================================================

-- Insert initial configuration
INSERT INTO logs.system_events (level, component, event_type, message, metadata)
VALUES (
    'INFO', 
    'database', 
    'initialization', 
    'Database initialized successfully',
    json_build_object('version', '1.0.0', 'timestamp', NOW())
) ON CONFLICT DO NOTHING;

COMMIT;